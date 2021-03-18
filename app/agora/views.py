from flask import render_template
from flask_login import login_required

from . import agora


@agora.route('/')
@agora.route('/agora')
@login_required
def index():
    return render_template('agora/index.html', title='Video Chat')
