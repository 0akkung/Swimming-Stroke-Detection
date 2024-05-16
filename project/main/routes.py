from flask import redirect, render_template, url_for
from flask_login import current_user
from project.main import main


@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'coach':
            return redirect(url_for('coach.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

    return render_template('index.html')


@main.route('/about')
def about():
    return render_template('about.html')
