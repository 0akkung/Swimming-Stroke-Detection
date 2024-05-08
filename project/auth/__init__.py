from flask import Blueprint

auth = Blueprint('auth', __name__)

from project.auth import routes
