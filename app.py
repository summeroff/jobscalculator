# app.py
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/input', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        jobs = request.form['jobs']

        # Split the input into lines
        lines = jobs.split('\n')

        # Connect to the database
        conn = sqlite3.connect('jobs.db')
        c = conn.cursor()

        # Get the current system time for the timestamp
        timestamp = datetime.datetime.now().isoformat()

        # For each line (except the header), parse the data and store it in the database
        for line in lines[1:]:
            # Ignore empty lines
            if line.strip() == '':
                continue
            
            line = line.rstrip()
            # Split the line into fields
            fields = line.split(',')
            job_id, url, frame_range, assignee, objects, attributes = fields[:6]

            # If the line includes project_id and task_id, extract them
            if len(fields) >= 8:
                project_id, task_id = fields[6:8]
            else:
                project_id = task_id = 0
            if len(assignee) < 1:
                assignee = "Unassigned"

            # Insert the data into the database
            c.execute('''
                INSERT INTO jobs (job_id, url, frame_range, assignee, objects, attributes, timestamp, project_id, task_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (job_id, url, frame_range, assignee, int(objects), int(attributes), timestamp, project_id, task_id))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return redirect(url_for('summary'))

    return render_template('home.html')

@app.route('/summary', methods=['GET'])
def summary():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Query the number of unique projects, tasks, jobs, and assignees
    num_projects = c.execute('SELECT COUNT(DISTINCT project_id) FROM jobs').fetchone()[0]
    num_tasks = c.execute('SELECT COUNT(DISTINCT task_id) FROM jobs').fetchone()[0]
    num_jobs = c.execute('SELECT COUNT(DISTINCT job_id) FROM jobs').fetchone()[0]
    num_assignees = c.execute('SELECT COUNT(DISTINCT assignee) FROM jobs').fetchone()[0]

    conn.close()

    return render_template('summary.html', num_projects=num_projects, num_tasks=num_tasks, num_jobs=num_jobs, num_assignees=num_assignees)

@app.route('/report')
def report():
    # Connect to the database
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Execute the query
    c.execute('''
        SELECT j1.task_id, j1.project_id, j1.assignee, SUM(j1.objects), SUM(j1.attributes)
        FROM jobs j1
        JOIN (
            SELECT task_id, project_id, MAX(timestamp) AS max_timestamp
            FROM jobs
            GROUP BY task_id, project_id
        ) j2 ON j1.task_id = j2.task_id AND j1.project_id = j2.project_id AND j1.timestamp = j2.max_timestamp
        GROUP BY j1.task_id, j1.project_id, j1.assignee
        ORDER BY j1.task_id, j1.project_id
    ''')

    # Fetch all the results
    results = c.fetchall()
    for row in results:
        print(row)
    # Close the connection
    conn.close()

    # Render the report template with the results
    return render_template('report.html', results=results)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
