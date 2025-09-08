from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column
from datetime import datetime

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
    attachments = db.relationship("Attachment", backref='project', lazy=True)

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)