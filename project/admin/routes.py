from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash
from project.models import User
from project.forms import CoachRegistrationForm
from project.admin import admin
from project.extensions import db


@admin.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')


@admin.route('/create-coach', methods=["GET", "POST"])
def register_coach():
    form = CoachRegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        print('validated')
        # code to validate and add user to database goes here
        email = form.email.data
        name = form.name.data
        password = form.password.data

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_coach = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        role='coach')

        # add the new user to the database
        db.session.add(new_coach)
        db.session.commit()

        return redirect(url_for('admin.dashboard'))

    return render_template('admin/register-coach.html', form=form)
