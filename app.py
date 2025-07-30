from flask import Flask, render_template, request, redirect, url_for
from models import db, Project
import csv
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def ensure_columns_exist(db_path='instance/projects.db'):
    REQUIRED_COLUMNS = {
        'id': "INTEGER PRIMARY KEY AUTOINCREMENT",
        'requester': "STRING(50) NOT NULL DEFAULT",
        'project_name': "STRING(50) NOT NULL DEFAULT",
        'status': "STRING(100) NOT NULL DEFAULT",
        'dept': "STRING(50) NOT NULL DEFAULT",
        'priority': "INTEGER NOT NULL DEFAULT",
        'complete': "BOOLEAN DEFAULT 0",
        'due_date': "TEXT DEFAULT ''"
    }

    if not os.path.exists(db_path):
        print("No DB found, creating...")
        return # if database doesn't exists it will let db.create_all() make it with all the correct columns
    
    

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(project)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    for column, definition in REQUIRED_COLUMNS.items():
        if column not in existing_columns:
            print(f"Adding missing column '{column}'...")
            cursor.execute(f"ALTER TABLE project ADD COLUMN {column} {definition}")
            conn.commit()
            print(f"Column '{column}' added.")
        else:
            print("No columns added")
    
    conn.close()

def load_dropdown_options(csv_path='options.csv'):
    requesters = set()
    depts = set()
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            requester_val = row.get('requester')
            dept_val = row.get('dept')

            if requester_val:
                requesters.add(requester_val.strip())
            if dept_val:
                depts.add(dept_val.strip())
    
    return sorted(requesters), sorted(depts)

@app.route('/')
def index():
    sort_field = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')
    show_filter = request.args.get('show', 'active')

    query = Project.query

    # Filter options for active, completed or all
    if show_filter == 'active':
        query = query.filter_by(complete=False)
    elif show_filter == 'completed':
        query = query.filter_by(complete=True)

    if sort_order == 'asc':
        projects = query.order_by(getattr(Project, sort_field).asc()).all() # Sort priority by ascending if set
    else:
        projects = query.order_by(getattr(Project, sort_field).desc()).all() # Sor priority by descending if nothing is set

    shrink_factor = 10 # The factor we want to shrink the entries so they all fit on the screen.
    return render_template('board.html', projects=projects, current_sort=sort_field, current_order=sort_order, row_count=len(projects), shrink_factor=shrink_factor, show_filter=show_filter) # Sends vars to flask for the web page.

@app.route('/edit', methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    project = Project.query.get(id) if id else None # Loads the specific project if editing, or reasponds None if creating a new entry.
    requesters, depts = load_dropdown_options()

    if request.method == 'POST':
        requester = request.form['requester'].strip().title() # striping away format differences so we can pull from the database without issue.
        project_name=request.form['project_name'].strip()
        status=request.form['status'].strip()
        dept = request.form['dept'].strip().title()
        priority=int(request.form['priority'])
        due_date = request.form.get('due_date', '').strip()

        if project:
            project.requester = requester
            project.project_name = project_name
            project.status = status
            project.dept = dept
            project.priority = priority
            project.due_date = due_date
        else:
            new_project = Project(
                requester=requester,
                project_name=project_name,
                status=status,
                dept=dept,
                priority=priority,
                due_date=due_date
            )
            db.session.add(new_project)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', project=project, requesters=requesters, depts=depts)

@app.route('/delete/<int:id>')
def delete(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle_complete/<int:id>', methods=['POST'])
def toggle_complete(id):
    project = Project.query.get_or_404(id)
    project.complete = not project.complete
    db.session.commit()
    return redirect(url_for('index', show=request.args.get('show', 'active')))

if __name__ == '__main__':
    ensure_columns_exist()
    with app.app_context():
        db.create_all()
    app.run(debug=True)


