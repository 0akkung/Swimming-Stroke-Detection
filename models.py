from flask_login import UserMixin
from app import db
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    """Create columns to store our data"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    swimming_records = db.relationship('SwimmingRecord', backref='user', lazy=True)

    def calculate_age(self):
        today = datetime.now()
        age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return age

    def __repr__(self):
        return '<User %r>' % self.username


class SwimmingRecord(db.Model):
    __tablename__ = 'swimming_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    stroke = db.Column(db.Integer, nullable=False)
    style = db.Column(db.String(20), nullable=False)
    strokes_per_minute = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
