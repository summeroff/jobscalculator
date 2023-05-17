# db.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT,
            url TEXT,
            frame_range TEXT,
            assignee TEXT,
            objects INTEGER,
            attributes INTEGER,
            timestamp TEXT,
            project_id TEXT,
            task_id TEXT
        )
    ''')

    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
