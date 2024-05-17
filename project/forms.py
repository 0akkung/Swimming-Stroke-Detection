from flask_wtf import Form
from wtforms import validators, ValidationError
from wtforms import StringField, IntegerField, PasswordField, RadioField, DateField, EmailField, SubmitField
from datetime import date
from project.models import User


class RegistrationForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Length(min=6, max=35)])
    height = IntegerField('Height (cm)', [validators.DataRequired(), validators.NumberRange(min=70, max=210)])
    weight = IntegerField('Weight (kg)', [validators.DataRequired(), validators.NumberRange(min=30, max=100)])
    gender = RadioField('Gender:', [validators.DataRequired()],
                        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    dob = DateField('Date of Birth', [validators.DataRequired()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(min=4, max=25)
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address already exists')

    def validate_dob(form, field):
        today = date.today()
        if field.data > today:
            raise ValidationError('Birthday cannot be in the future.')

        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        if age < 15:
            raise ValidationError(f'You must be at least 15 years old. (You are {age})')


class CoachRegistrationForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email Address', [validators.DataRequired(), validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(min=4, max=25)
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address already exists')
