from flask import Blueprint

main = Blueprint('main', __name__)

from project.main import routes