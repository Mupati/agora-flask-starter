from flask import Blueprint

auth = Blueprint('auth', '__init__')

from . import views  # isort:skip