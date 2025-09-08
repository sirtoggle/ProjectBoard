import csv
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, Project, Attachment
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- DB Maintenance ---
def ensure_columns_exist(db_path='instance/projects.db'):
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    create_new = not os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if create_new:
        cursor.execute("""
            CREATE TABLE project(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester TEXT,
                project_name TEXT,
                status TEXT,
                dept TEXT,
                priority INTEGER,
                due_date TEXT,
                complete BOOLEAN DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE attachment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES project(id)
            )
        """)
        print("Created new database with 'project' and 'attachment' tables.")

    else:
        # Check all required columns in project table
        REQUIRED_COLUMNS = {
            'id': "INTEGER PRIMARY KEY AUTOINCREMENT",
            'requester': "TEXT",
            'project_name': "TEXT",
            'status': "TEXT",
            'dept': "TEXT",
            'priority': "INTEGER",
            'complete': "BOOLEAN DEFAULT 0",
            'due_date': "TEXT"
        }

        cursor.execute("PRAGMA table_info(project)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        for column, definition in REQUIRED_COLUMNS.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE project ADD COLUMN {column} {definition}")
                print(f"Column '{column}' added.")

        # Ensure attachment table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachment'")
        table_exists = cursor.fetchone()
        if not table_exists:
            cursor.execute("""
                CREATE TABLE attachment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(project_id) REFERENCES project(id)
                )
            """)
            print("Created 'attachment' table.")

    conn.commit()
    conn.close()

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# --- Routes ---
@app.route('/')
def index():
    sort_field = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')
    show_filter = request.args.get('show', 'active')

    query = Project.query

    if show_filter == 'active':
        query = query.filter_by(complete=False)
    elif show_filter == 'completed':
        query = query.filter_by(complete=True)

    if sort_order == 'asc':
        projects = query.order_by(getattr(Project, sort_field).asc()).all()
    else:
        projects = query.order_by(getattr(Project, sort_field).desc()).all()

    shrink_factor = 10
    return render_template('board.html', projects=projects,
                           current_sort=sort_field,
                           current_order=sort_order,
                           row_count=len(projects),
                           shrink_factor=shrink_factor,
                           show_filter=show_filter)

@app.route('/project/<int:project_id>', methods=['GET', 'POST'])
def project_details(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            attachment = Attachment(
                project_id=project.id,
                filename=filename,
                filepath=filepath
            )
            db.session.add(attachment)
            db.session.commit()

            return redirect(url_for('project_details', project_id=project.id))

    return render_template('project_details.html', project=project)

@app.route('/edit', methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    project = Project.query.get(id) if id else None
    requesters, depts = load_dropdown_options()

    if request.method == 'POST':
        requester = request.form['requester'].strip().title()
        project_name = request.form['project_name'].strip()
        status = request.form['status'].strip()
        dept = request.form['dept'].strip().title()
        priority = int(request.form['priority'])
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

# --- App Entry ---
if __name__ == '__main__':
    ensure_columns_exist()
    with app.app_context():
        db.create_all()
    app.run(debug=True)