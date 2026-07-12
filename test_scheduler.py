import pytest
from scheduler import (
    is_valid_build,
    get_required_steps,
    is_valid_turn_assignment,
    optimize_schedule,
    ATTRIBUTES
)

def test_is_valid_build():
    # Base case: no upgrades
    assert is_valid_build({a: 0 for a in ATTRIBUTES}) == True
    
    # +4 Sprint, +2 Dirt (10 + 4 = 14 stars; 4 + 2 = 6 slots) -> Valid
    b1 = {a: 0 for a in ATTRIBUTES}
    b1['sprint'] = 4
    b1['dirt'] = 2
    assert is_valid_build(b1) == True
    
    # +4 Sprint, +3 Dirt (10 + 7 = 17 stars; 4 + 3 = 7 slots) -> Invalid (too many slots)
    b2 = {a: 0 for a in ATTRIBUTES}
    b2['sprint'] = 4
    b2['dirt'] = 3
    assert is_valid_build(b2) == False
    
    # +4 Sprint, +4 Dirt (10 + 10 = 20 stars; 4 + 4 = 8 slots) -> Invalid
    b3 = {a: 0 for a in ATTRIBUTES}
    b3['sprint'] = 4
    b3['dirt'] = 4
    assert is_valid_build(b3) == False

    # Six +1s (6 stars, 6 slots) -> Valid
    b4 = {a: 1 for a in ATTRIBUTES}
    assert is_valid_build(b4) == True

def test_get_required_steps():
    # Base ranks: Turf A (6), Dirt G (0), Sprint A (6), Mile F (1), Medium E (2), Long G (0)
    base = {
        'turf': 6,
        'dirt': 0,
        'sprint': 6,
        'mile': 1,
        'medium': 2,
        'long': 0
    }
    
    # Race: Hanshin Juvenile Fillies (Mile, Turf)
    # Target: Turf C (4), Mile B (5)
    # Turf base is 6 >= 4 -> 0 steps
    # Mile base is 1, target 5 -> 4 steps
    race_hj = {'surface': 0, 'distance': 1} # Turf, Mile
    reqs_hj = get_required_steps(race_hj, base)
    assert reqs_hj['turf'] == 0
    assert reqs_hj['mile'] == 4
    assert reqs_hj['sprint'] == 0
    
    # Race: Takamatsunomiya Kinen (Sprint, Turf)
    # Sprint base is 6 >= 5 -> 0 steps
    race_tk = {'surface': 0, 'distance': 0}
    reqs_tk = get_required_steps(race_tk, base)
    assert reqs_tk['sprint'] == 0
    
    # Race: February Stakes (Mile, Dirt)
    # Target: Dirt C (4), Mile B (5)
    # Dirt base is 0, target 4 -> 4 steps (downgraded to 2 for valid build)
    # Mile base is 1, target 5 -> 4 steps
    race_fs = {'surface': 1, 'distance': 1}
    reqs_fs = get_required_steps(race_fs, base)
    assert reqs_fs['dirt'] == 2
    assert reqs_fs['mile'] == 4
    
    # Race with impossible requirements: Sprint G (0) to B (5) -> Needs 5 steps
    # Capped at +4 steps (exception logic test)
    base_sprint_g = {
        'turf': 6, 'dirt': 6,
        'sprint': 0, 'mile': 6, 'medium': 6, 'long': 6
    }
    race_sprint = {'surface': 0, 'distance': 0}
    reqs_sprint = get_required_steps(race_sprint, base_sprint_g)
    assert reqs_sprint['sprint'] == 4  # capped at +4

def test_is_valid_turn_assignment():
    # Empty schedule
    schedule = [None] * 73
    
    # Place at turn 10
    assert is_valid_turn_assignment(schedule, 10, max_consecutive=2) == True
    schedule[10] = "Race1"
    
    # Try placing at turn 10 again -> Collision
    assert is_valid_turn_assignment(schedule, 10, max_consecutive=2) == False
    
    # With max_consecutive=2:
    # Schedule: 10 occupied
    # Place at 11 -> Valid
    assert is_valid_turn_assignment(schedule, 11, max_consecutive=2) == True
    schedule[11] = "Race2"
    
    # Schedule: 10 and 11 occupied
    # Try placing at 12 -> Invalid (3 in a row: 10, 11, 12)
    assert is_valid_turn_assignment(schedule, 12, max_consecutive=2) == False
    
    # Try placing at 9 -> Invalid (3 in a row: 9, 10, 11)
    assert is_valid_turn_assignment(schedule, 9, max_consecutive=2) == False
    
    # Place at 8 -> Valid (8 occupied, 9 empty, 10 and 11 occupied)
    assert is_valid_turn_assignment(schedule, 8, max_consecutive=2) == True

def test_optimize_schedule():
    # Simple test of scheduling logic
    # Base ranks: all A (6)
    base = {a: 6 for a in ATTRIBUTES}
    
    # Create mock races that have no requirements
    races = [
        {'id': 1, 'name': 'Race A', 'surface': 0, 'distance': 1, 'turns': [10, 20]},
        {'id': 2, 'name': 'Race B', 'surface': 0, 'distance': 1, 'turns': [10, 30]},
    ]
    
    # If consecutive limit is 2, they should easily schedule on different turns
    careers = optimize_schedule(base, races, max_consecutive=2)
    assert len(careers) == 1
    career = careers[0]
    assert len(career['races']) == 2
    # Ensure they are scheduled on different turns
    sched = career['schedule']
    placed = [t for t in range(1, 73) if sched[t] is not None]
    assert len(placed) == 2
    assert placed != [10, 10]
