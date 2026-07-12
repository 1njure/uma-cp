# Helper function to render HTML calendar grid for a single year
def render_calendar_year(schedule, year_idx):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    quarters = ["Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"]
    
    html = """
    <style>
    .year-table {
        width: 100%;
        background: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 10px;
        table-layout: fixed;
    }
    .year-table th {
        background: rgba(255, 255, 255, 0.03);
        color: #a0aec0;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: 700;
        padding: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        border-right: 1px solid rgba(255, 255, 255, 0.04);
    }
    .year-table td {
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        border-right: 1px solid rgba(255, 255, 255, 0.03);
        text-align: center;
        vertical-align: middle;
        padding: 4px;
        height: 1px;
    }
    .year-table th:last-child, .year-table td:last-child {
        border-right: none;
    }
    .year-table tr:last-child td {
        border-bottom: none;
    }
    .quarter-cell {
        font-weight: 800;
        font-size: 0.9rem;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.02);
        width: 110px;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .month-cell {
        font-weight: 700;
        color: #94a3b8;
        background: rgba(255, 255, 255, 0.005);
        width: 60px;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .race-card {
        min-height: 85px;
        height: 100%;
        box-sizing: border-box;
        padding: 8px;
        margin: 0;
        border-radius: 6px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        text-align: left;
        transition: all 0.2s ease;
    }
    .card-g1 {
        border: 1px solid rgba(59, 130, 246, 0.25);
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(147, 51, 234, 0.08) 100%);
    }
    .card-g2 {
        border: 1px solid rgba(236, 72, 153, 0.25);
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.08) 0%, rgba(219, 39, 119, 0.08) 100%);
    }
    .card-g3 {
        border: 1px solid rgba(16, 185, 129, 0.25);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(45, 212, 191, 0.08) 100%);
    }
    .race-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .card-g1:hover {
        border-color: rgba(59, 130, 246, 0.6);
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 51, 234, 0.15) 100%);
    }
    .card-g2:hover {
        border-color: rgba(236, 72, 153, 0.6);
        background: linear-gradient(135deg, rgba(236, 72, 153, 0.15) 0%, rgba(219, 39, 119, 0.15) 100%);
    }
    .card-g3:hover {
        border-color: rgba(16, 185, 129, 0.6);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(45, 212, 191, 0.15) 100%);
    }
    .card-grade {
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .grade-val-g1 { color: #60a5fa; }
    .grade-val-g2 { color: #f472b6; }
    .grade-val-g3 { color: #34d399; }
    
    .card-name {
        font-size: 0.8rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 6px;
        line-height: 1.2;
    }
    .card-specs {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
    }
    .spec-badge {
        font-size: 0.65rem;
        padding: 1px 5px;
        border-radius: 4px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .spec-surf-turf {
        background: rgba(45, 212, 191, 0.12);
        color: #2dd4bf;
    }
    .spec-surf-dirt {
        background: rgba(251, 146, 60, 0.12);
        color: #fb923c;
    }
    .spec-dist-sprint {
        background: rgba(168, 85, 247, 0.12);
        color: #c084fc;
    }
    .spec-dist-mile {
        background: rgba(250, 204, 21, 0.12);
        color: #fde047;
    }
    .spec-dist-medium {
        background: rgba(6, 182, 212, 0.12);
        color: #22d3ee;
    }
    .spec-dist-long {
        background: rgba(248, 113, 113, 0.12);
        color: #fca5a5;
    }
    .empty-card {
        min-height: 85px;
        height: 100%;
        box-sizing: border-box;
        margin: 0;
        border: 1px dashed rgba(255, 255, 255, 0.03);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4a5568;
        font-size: 0.9rem;
    }
    </style>
    <table class="year-table">
        <thead>
            <tr>
                <th style="width: 110px;">Quarter</th>
                <th style="width: 65px;">Month</th>
                <th>Early</th>
                <th>Late</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for m in range(12):
        html += "<tr>"
        
        # Quarter cell spanning 3 rows
        if m % 3 == 0:
            q_idx = m // 3
            html += f'<td rowspan="3" class="quarter-cell">{quarters[q_idx]}</td>'
            
        # Month cell
        html += f'<td class="month-cell">{months[m]}</td>'
        
        # Early and Late columns
        for half in [0, 1]:
            turn = year_idx * 24 + m * 2 + half + 1
            race = schedule[turn]
            
            html += "<td>"
            if race:
                grade_str = ["G1", "G2", "G3"][race['grade']]
                grade_class = f"card-g{race['grade'] + 1}"
                grade_val_class = f"grade-val-g{race['grade'] + 1}"
                
                dist_str = ["Sprint", "Mile", "Medium", "Long"][race['distance']]
                dist_lower = dist_str.lower()
                
                surf_str = ["Turf", "Dirt"][race['surface']]
                surf_lower = surf_str.lower()
                
                tooltip = f"{race['name']} ({grade_str}, {surf_str} {dist_str}) - Turn {turn}"
                
                html += f"""
                <div class="race-card {grade_class}" title="{tooltip}">
                    <div class="card-grade {grade_val_class}">{grade_str}</div>
                    <div class="card-name">{race['name']}</div>
                    <div class="card-specs">
                        <span class="spec-badge spec-surf-{surf_lower}">{surf_str}</span>
                        <span class="spec-badge spec-dist-{dist_lower}">{dist_str}</span>
                    </div>
                </div>
                """
            else:
                html += '<div class="empty-card">-</div>'
            html += "</td>"
            
        html += "</tr>"
        
    html += "</tbody></table>"
    return html
