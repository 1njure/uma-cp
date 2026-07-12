import os
import sqlite3
import csv

DB_PATH = "races.db"
CSV_PATH = "racelist.csv"

def init_db():
    """Initializes the SQLite database from the racelist.csv file if it hasn't been loaded already."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS races (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            distance INTEGER NOT NULL,
            surface INTEGER NOT NULL,
            turns TEXT NOT NULL
        )
    """)
    
    # Check if table is empty
    cursor.execute("SELECT COUNT(*) FROM races")
    count = cursor.fetchone()[0]
    
    if count == 0:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"Missing source file: {CSV_PATH}")
            
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            races_to_insert = []
            for row in reader:
                races_to_insert.append((
                    int(row['id']),
                    row['name'],
                    int(row['grade']),
                    int(row['distance']),
                    int(row['surface']),
                    row['turns']
                ))
            
            cursor.executemany("""
                INSERT INTO races (id, name, grade, distance, surface, turns)
                VALUES (?, ?, ?, ?, ?, ?)
            """, races_to_insert)
            conn.commit()
            
    conn.close()

def get_all_races():
    """Fetches all races from the database, returning them as a list of dicts."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM races")
    rows = cursor.fetchall()
    
    races = []
    for row in rows:
        races.append({
            'id': row['id'],
            'name': row['name'],
            'grade': row['grade'],
            'distance': row['distance'],
            'surface': row['surface'],
            # parse turns as a list of ints
            'turns': [int(t.strip()) for t in row['turns'].split(',') if t.strip()]
        })
        
    conn.close()
    return races

if __name__ == "__main__":
    init_db()
    races = get_all_races()
    print(f"Loaded {len(races)} races successfully.")
