import os
import time
from flask import render_template, jsonify, request
from flask_login import login_required, current_user

from agora_token_builder import RtcTokenBuilder, RtmTokenBuilder

from . import agora_rtm
from ..models import User


ROLE_RTM_USER = 1
ROLE_PUBLISHER = 1


@agora_rtm.route('/agora-rtm')
@login_required
def index():
    users = User.query.all()
    all_users = [user.to_json() for user in users]
    return render_template('agora_rtm/index.html', title='Agora Video Call with RTM', allUsers=all_users, agoraAppID=os.environ.get('AGORA_APP_ID'))


@agora_rtm.route('/users')
def fetch_users():
    users = User.query.all()
    all_users = [user.to_json() for user in users]
    return jsonify(all_users)


@agora_rtm.route('/agora-rtm/token',  methods=['POST'])
def generate_agora_token():
    auth_user = current_user.to_json()
    appID = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = request.json['channelName']
    userAccount = auth_user['username']
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, ROLE_PUBLISHER, privilegeExpiredTs)

    rtm_token = RtmTokenBuilder.buildToken(
        appID, appCertificate, userAccount, ROLE_RTM_USER, privilegeExpiredTs)
    return jsonify({'token': token, 'rtm_token': rtm_token, 'appID': appID})
