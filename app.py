from flask import Flask, render_template, request, redirect, url_for
from models import db, Project

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    sort_field = request.args.get('sort', 'priority')
    sort_order = request.args.get('order', 'desc')

    if sort_order == 'asc':
        projects = Project.query.order_by(Project.priority.asc()).all() # Sort priority by ascending if set
    else:
        projects = Project.query.order_by(Project.priority.desc()).all() # Sor priority by descending if nothing is set

    row_count = len(projects) # Counts the amount of entires.
    shrink_factor = 10 # The factor we want to shrink the entries so they all fit on the screen.
    return render_template('board.html', projects=projects, current_sort=sort_field, current_order=sort_order, row_count=row_count, shrink_factor=shrink_factor) # Sends vars to flask for the web page.

@app.route('/edit', methods=['GET', 'POST'])
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id=None):
    project = Project.query.get(id) if id else None # Loads the specific project if editing, or reasponds None if creating a new entry.
    
    if request.method == 'POST':
        requester = request.form['requester'].strip().title()
        dept = request.form['dept'].strip().title()

        if project:
            project.requester = requester
            project.project_name = request.form['project_name'].strip()
            project.status = request.form['status'].strip()
            project.dept = dept
            project.priority = int(request.form['priority'])
        else:
            new_project = Project(
                requester=requester,
                project_name=request.form['project_name'].strip(),
                status=request.form['status'].strip(),
                dept=dept,
                priority=int(request.form['priority'])
            )
            db.session.add(new_project)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', project=project)

@app.route('/delete/<int:id>')
def delete(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
