from flask import Blueprint

swimmer = Blueprint('swimmer', __name__)

from project.swimmer import routes