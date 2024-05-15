from flask import Blueprint

admin = Blueprint('admin', __name__)

from project.admin import routes