from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column
from datetime import date

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(50), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    dept = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    complete = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.String(10), default='')