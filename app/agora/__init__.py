from flask import Blueprint
agora = Blueprint('agora', '__init__')

from . import views  # isort:skip