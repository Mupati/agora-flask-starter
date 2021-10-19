from flask import Blueprint
agora_rtm = Blueprint('agora_rtm', '__init__')

from . import views  # isort:skip