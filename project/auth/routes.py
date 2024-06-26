from flask import render_template, redirect, url_for, request, flash, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from project.forms import LoginForm, RegistrationForm
from project.models import User, Profile
from flask_login import login_required, login_user, logout_user
from project.auth import auth
from project.extensions import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
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
            flash('The email address does not exist, please try again', 'danger')
            return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

        if not check_password_hash(user.password, password):
            print("Invalid password")
            flash('Please check your password and try again.', 'danger')
            return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)

        if user.role == 'coach':
            return redirect(url_for('coach.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

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

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        role='swimmer')
        new_profile = Profile(height=height, weight=weight, gender=gender, date_of_birth=dob)
        new_user.profile = new_profile

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been successfully registered.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
