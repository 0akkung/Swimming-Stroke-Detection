from flask import Flask, render_template, redirect, url_for, request, flash, Response, send_file
from swimming_detector import SwimmingDetector
from datetime import datetime
from io import BytesIO
from models import db, User, SwimmingRecord

from flask_login import LoginManager, login_required, current_user

from main import main as main_blueprint
from auth import auth as auth_blueprint
from swimmer import swimmer as swimmer_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)

with app.app_context():
    db.create_all()

counter = SwimmingDetector()

login_manager = LoginManager()  # Login manage for flask-login
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(swimmer_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
