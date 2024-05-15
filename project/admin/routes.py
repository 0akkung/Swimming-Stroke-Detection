from flask import render_template, redirect, url_for, request
from project.models import User
from project.forms import RegistrationForm
from project.admin import admin
from project.extensions import db


@admin.route('/create-coach', methods=["GET", "POST"])
def register_coach():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        print('validated')
        # code to validate and add user to database goes here
        email = form.email.data
        name = form.name.data
        password = form.password.data

        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        role='coach')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register-coach.html', form=form)