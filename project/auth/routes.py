from flask import render_template, redirect, url_for, request, flash, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from project.forms import RegistrationForm
from project.models import db, User
from flask_login import login_required, login_user, logout_user
from project.auth import auth


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            print("User not found")
            flash('The email address does not exist, please try again')
            return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

        if not user or not check_password_hash(user.password, password):
            print("Invalid password")
            flash('Please check your password and try again.')
            return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('swimmer.profile'))

    return render_template('login.html')


@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        print('validated')
        # code to validate and add user to database goes here
        email = form.email.data
        name = form.name.data
        password = form.password.data
        height = form.height.data
        weight = form.weight.data
        gender = form.gender.data
        dob = form.dob.data

        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('register'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        height=height, weight=weight, gender=gender, date_of_birth=dob)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
