# UmaCP - Umamusume Completionist Planner
# Copyright (C) 2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools

ATTRIBUTES = ['turf', 'dirt', 'sprint', 'mile', 'medium', 'long']

STAR_COSTS = {0: 0, 1: 1, 2: 4, 3: 7, 4: 10}
SLOT_COSTS = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

RANK_SCALE = {'G': 0, 'F': 1, 'E': 2, 'D': 3, 'C': 4, 'B': 5, 'A': 6}
RANK_NAMES = {v: k for k, v in RANK_SCALE.items()}

def get_required_steps(race, base_ranks):
    """
    Calculates the required upgrade steps for a race based on the base ranks.
    If the combined requirements exceed build limits, it prioritizes the distance
    upgrade and downgrades the surface upgrade until a valid build is found.
    """
    req = {attr: 0 for attr in ATTRIBUTES}
    
    # Surface requirement (Turf = 0, Dirt = 1) -> Must be at least C (4)
    surf_name = 'turf' if race['surface'] == 0 else 'dirt'
    surf_base = base_ranks.get(surf_name, 0)
    surf_diff = max(0, 4 - surf_base)
    surf_val = min(4, surf_diff)
    
    # Distance requirement -> Sprint/Mile must be B (5), Medium/Long must be C (4)
    dist_val = race['distance']
    if dist_val == 0:
        dist_name = 'sprint'
        dist_req = 5
    elif dist_val == 1:
        dist_name = 'mile'
        dist_req = 5
    elif dist_val == 2:
        dist_name = 'medium'
        dist_req = 4
    else:
        dist_name = 'long'
        dist_req = 4
        
    dist_base = base_ranks.get(dist_name, 0)
    dist_diff = max(0, dist_req - dist_base)
    dist_val = min(4, dist_diff)
    
    # Adjust surface upgrade until the combination is valid (prioritizing distance)
    test_build = {attr: 0 for attr in ATTRIBUTES}
    test_build[surf_name] = surf_val
    test_build[dist_name] = dist_val
    
    while not is_valid_build(test_build) and surf_val > 0:
        surf_val -= 1
        test_build[surf_name] = surf_val
        
    req[surf_name] = surf_val
    req[dist_name] = dist_val
    return req

def is_valid_build(build):
    """
    Checks if an inheritance build satisfies the rules:
    - Total stars <= 18
    - Total slots <= 6
    """
    total_stars = sum(STAR_COSTS[build[attr]] for attr in ATTRIBUTES)
    total_slots = sum(SLOT_COSTS[build[attr]] for attr in ATTRIBUTES)
    return total_stars <= 18 and total_slots <= 6

def get_build_requirements(build):
    """Returns details of the star and slot costs for a build."""
    reqs = {}
    total_stars = 0
    total_slots = 0
    for attr, val in build.items():
        if val > 0:
            stars = STAR_COSTS[val]
            slots = SLOT_COSTS[val]
            reqs[attr] = {
                'steps': val,
                'stars': stars,
                'slots': slots
            }
            total_stars += stars
            total_slots += slots
    return {
        'attributes': reqs,
        'total_stars': total_stars,
        'total_slots': total_slots
    }

def get_candidate_builds(remaining_heavy_races, base_ranks):
    """
    Generates all valid candidate builds that can support the remaining heavy races.
    Optimized by restricting to active attributes and their max requirements.
    """
    active_attrs = set()
    max_req = {attr: 0 for attr in ATTRIBUTES}
    
    for race in remaining_heavy_races:
        reqs = get_required_steps(race, base_ranks)
        for attr, val in reqs.items():
            if val > 0:
                active_attrs.add(attr)
                max_req[attr] = max(max_req[attr], val)
                
    if not active_attrs:
        return [{attr: 0 for attr in ATTRIBUTES}]
        
    active_list = list(active_attrs)
    ranges = [range(max_req[attr] + 1) for attr in active_list]
    
    candidates = []
    for combo in itertools.product(*ranges):
        build = {attr: 0 for attr in ATTRIBUTES}
        for attr, val in zip(active_list, combo):
            build[attr] = val
        if is_valid_build(build):
            candidates.append(build)
            
    # Sort candidate builds by total stars descending (prioritize larger builds)
    candidates.sort(key=lambda b: sum(STAR_COSTS[b[a]] for a in ATTRIBUTES), reverse=True)
    return candidates

def is_race_supported(race, build, base_ranks):
    """Checks if a build provides enough upgrade steps to run the race."""
    reqs = get_required_steps(race, base_ranks)
    for attr in ATTRIBUTES:
        if build[attr] < reqs[attr]:
            return False
    return True

def is_valid_turn_assignment(schedule, turn, max_consecutive):
    """
    Checks if a race can be placed at a turn without violating:
    - Turn collisions (only 1 race per turn)
    - Consecutive races limit
    """
    if schedule[turn] is not None:
        return False
        
    if max_consecutive is None:
        return True
        
    # Check consecutive races limit (max K consecutive runs)
    K = max_consecutive
    for s in range(turn - K, turn + 1):
        if s < 1 or s + K > 72:
            continue
        consecutive_count = 0
        for t in range(s, s + K + 1):
            if t == turn or schedule[t] is not None:
                consecutive_count += 1
        if consecutive_count > K:
            return False
            
    return True

def find_schedule_for_races(races_to_schedule, initial_schedule, max_consecutive, max_states=1000):
    """
    Backtracking constraint solver to schedule as many races as possible.
    Uses Minimum Remaining Values (MRV) and branch-and-bound pruning.
    """
    # Sort by MRV: races with fewer turn options first
    sorted_races = sorted(races_to_schedule, key=lambda r: len(r['turns']))
    
    best_count = -1
    best_schedule = list(initial_schedule)
    best_assigned = []
    
    state_count = 0
    
    def dfs(idx, schedule, assigned):
        nonlocal best_count, best_schedule, best_assigned, state_count
        
        state_count += 1
        if state_count > max_states:
            return
            
        remaining = len(sorted_races) - idx
        if len(assigned) + remaining <= best_count:
            return
            
        if idx == len(sorted_races):
            if len(assigned) > best_count:
                best_count = len(assigned)
                best_schedule = list(schedule)
                best_assigned = list(assigned)
            return
            
        race = sorted_races[idx]
        
        # Try placing the race in each of its available turns
        for turn in race['turns']:
            if is_valid_turn_assignment(schedule, turn, max_consecutive):
                schedule[turn] = race
                assigned.append(race)
                
                dfs(idx + 1, schedule, assigned)
                
                schedule[turn] = None
                assigned.pop()
                
        # Try skipping this race
        dfs(idx + 1, schedule, assigned)
        
    dfs(0, list(initial_schedule), [])
    return best_schedule, best_assigned

def schedule_career(supported_heavy, supported_free, max_consecutive):
    """
    Schedules a single career in two phases:
    1. Schedule as many heavy races as possible.
    2. Schedule as many free races as possible in the remaining turns.
    """
    initial_schedule = [None] * 73
    
    # Phase 1: Heavy races
    heavy_schedule, sched_heavy = find_schedule_for_races(
        supported_heavy, initial_schedule, max_consecutive, max_states=2000
    )
    
    # Phase 2: Free races
    final_schedule, sched_free = find_schedule_for_races(
        supported_free, heavy_schedule, max_consecutive, max_states=2000
    )
    
    return final_schedule, sched_heavy, sched_free

def optimize_schedule(base_ranks, uncompleted_races, max_consecutive):
    """
    Partitions the uncompleted races into the minimum number of careers,
    determining the builds and schedules for each.
    """
    remaining_races = list(uncompleted_races)
    careers = []
    
    while remaining_races:
        # Separate into heavy and free races for current remaining set
        heavy_races = []
        free_races = []
        for race in remaining_races:
            reqs = get_required_steps(race, base_ranks)
            if any(val > 0 for val in reqs.values()):
                heavy_races.append(race)
            else:
                free_races.append(race)
                
        # If only free races are left, schedule them under a clean (zero) build
        if not heavy_races:
            build = {attr: 0 for attr in ATTRIBUTES}
            schedule, _, sched_free = schedule_career([], free_races, max_consecutive)
            
            scheduled_all = sched_free
            if not scheduled_all:
                # Safety fallback to prevent infinite loop
                break
                
            careers.append({
                'build': build,
                'schedule': schedule,
                'races': scheduled_all
            })
            
            scheduled_ids = {r['id'] for r in scheduled_all}
            remaining_races = [r for r in remaining_races if r['id'] not in scheduled_ids]
            continue
            
        # Generate candidate builds
        candidates = get_candidate_builds(heavy_races, base_ranks)
        
        best_build = None
        best_schedule = None
        best_scheduled_all = []
        best_score = -1
        
        # Test candidate builds and pick the one with highest score
        for build in candidates:
            supported_heavy = [r for r in heavy_races if is_race_supported(r, build, base_ranks)]
            supported_free = [r for r in free_races if is_race_supported(r, build, base_ranks)]
            
            schedule, sched_heavy, sched_free = schedule_career(supported_heavy, supported_free, max_consecutive)
            
            # Score: prioritizes heavy races (weight 1000) over free ones (weight 1)
            score = 1000 * len(sched_heavy) + len(sched_free)
            
            if score > best_score:
                best_score = score
                best_build = build
                best_schedule = schedule
                best_scheduled_all = sched_heavy + sched_free
            elif score == best_score:
                # Tie-breaker: choose the build with fewer stars
                curr_stars = sum(STAR_COSTS[build[a]] for a in ATTRIBUTES)
                best_stars = sum(STAR_COSTS[best_build[a]] for a in ATTRIBUTES)
                if curr_stars < best_stars:
                    best_build = build
                    best_schedule = schedule
                    best_scheduled_all = sched_heavy + sched_free
                
        # Safety fallback: if no races could be scheduled, force-schedule the first race
        if not best_scheduled_all:
            forced_race = remaining_races[0]
            build = get_required_steps(forced_race, base_ranks)
            # Find the first available turn
            turn = forced_race['turns'][0]
            schedule = [None] * 73
            schedule[turn] = forced_race
            best_build = build
            best_schedule = schedule
            best_scheduled_all = [forced_race]
            
        careers.append({
            'build': best_build,
            'schedule': best_schedule,
            'races': best_scheduled_all
        })
        
        # Remove scheduled races
        scheduled_ids = {r['id'] for r in best_scheduled_all}
        remaining_races = [r for r in remaining_races if r['id'] not in scheduled_ids]
        
    return careers
