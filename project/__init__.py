from flask import Flask
from project.models import db, User

from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()  # Login manage for flask-login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Import and register Blueprint
    from project.main import main as main_blueprint
    from project.auth import auth as auth_blueprint
    from project.swimmer import swimmer as swimmer_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(swimmer_blueprint)

    return app