from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(50))
    project_name = db.Column(db.String(100))
    status = db.Column(db.String(100))
    dept = db.Column(db.String(50))
    priority = db.Column(db.Integer)