import os
import time
from flask import render_template, jsonify, request
from flask_login import login_required, current_user

import base64
import http.client
import json

from . import agora_rtm
from ..models import User
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from .agora_key.RtmTokenBuilder import RtmTokenBuilder, Role_Rtm_User


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
    uid = auth_user['id']
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithUid(
        appID, appCertificate, channelName, uid, Role_Attendee, privilegeExpiredTs)

    rtm_token = RtmTokenBuilder.buildToken(
        appID, appCertificate, userAccount, Role_Rtm_User, privilegeExpiredTs)

    return jsonify({'token': token, 'rtm_token': rtm_token, 'appID': appID})


def generate_base64_credential():
    # Customer ID
    customer_key = os.environ.get('AGORA_CUSTOMER_ID')
    # Customer secret
    customer_secret = os.environ.get('AGORA_CUSTOMER_SECRET')

    # Concatenate customer key and customer secret and use base64 to encode the concatenated string
    credentials = customer_key + ":" + customer_secret
    # Encode with base64
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")

    return credential


@agora_rtm.route('/agora-rtm/resource-id', methods=['POST'])
def generate_resource_id():
    auth_user = current_user.to_json()
    userId = auth_user['id']
    channelName = request.json['channelName']

    # Get the base64 credential for making requests
    credential = generate_base64_credential()

    # Create connection object with basic URL
    conn = http.client.HTTPSConnection("api.agora.io")
    params = json.dumps({
        "cname": channelName,
        "uid": str(userId),
        "clientRequest": {
            "resourceExpiredHour": 24,
            "scene": 0
        }
    })

    # Create Header object
    headers = {
        "Content-type": "application/json;charset=utf-8",
        "Authorization": "Basic "+credential
    }

    app_id = os.environ.get('AGORA_APP_ID')
    resource_url_path = '/v1/apps/'+app_id+'/cloud_recording/acquire'

    # Send request
    conn.request("POST", resource_url_path, params, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")


@agora_rtm.route('/agora-rtm/start-recording', methods=['POST'])
def start_recording():
    auth_user = current_user.to_json()
    userId = auth_user['id']
    channelName = request.json['channelName']
    token = request.json['token']
    storage_vendor = os.environ.get('STORAGE_VENDOR')
    storage_region = os.environ.get('STORAGE_REGION')
    storage_bucket = os.environ.get('STORAGE_BUCKET')
    storage_access_key = os.environ.get('STORAGE_ACCESS_KEY')
    storage_secret_key = os.environ.get('STORAGE_SECRET_KEY')

    # Get the base64 credential for making requests
    credential = generate_base64_credential()

    conn = http.client.HTTPSConnection("api.agora.io")

    params = json.dumps({
        "cname": channelName,
        "uid": str(userId),
        "clientRequest": {
            "token": token,
            "recordingConfig": {
                "channelType": 0,
                "streamTypes": 2,
                "audioProfile": 1,
                "videoStreamType": 0,
                "maxIdleTime": 120,
                "transcodingConfig": {
                    "width": 1920,
                    "height": 1080,
                    "fps": 60,
                    "bitrate": 4780,
                    "maxResolutionUid": "1",
                    "mixedVideoLayout": 1
                }
            },
            "recordingFileConfig": {
                "avFileType": [
                    "hls",
                    "mp4"
                ]
            },
            "storageConfig": {
                "vendor": int(storage_vendor),
                "region": int(storage_region),
                "bucket": storage_bucket,
                "accessKey": storage_access_key,
                "secretKey": storage_secret_key
            }
        }
    })

    # Create Header object
    headers = {
        "Content-type": "application/json;charset=utf-8",
        "Authorization": "Basic "+credential
    }
    app_id = os.environ.get('AGORA_APP_ID')
    resource_id = request.json['resourceId']
    resource_url_path = '/v1/apps/'+app_id + \
        '/cloud_recording/resourceid/'+resource_id+'/mode/mix/start'

    # Send request
    conn.request("POST", resource_url_path, params, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")


@agora_rtm.route('/agora-rtm/stop-recording', methods=['POST'])
def stop_recording():
    auth_user = current_user.to_json()
    userId = auth_user['id']
    channelName = request.json['channelName']
    token = request.json['token']

    # Get the base64 credential for making requests
    credential = generate_base64_credential()

    conn = http.client.HTTPSConnection("api.agora.io")

    params = json.dumps({
        "cname": channelName,
        "uid": str(userId),
        "clientRequest": {
            "token": token
        }
    })

    # Create Header object
    headers = {
        "Content-type": "application/json;charset=utf-8",
        "Authorization": "Basic "+credential
    }
    app_id = os.environ.get('AGORA_APP_ID')
    resource_id = request.json['resourceId']
    sid = request.json['sid']
    resource_url_path = '/v1/apps/'+app_id + \
        '/cloud_recording/resourceid/'+resource_id+'/sid/'+sid+'/mode/mix/stop'

    # Send request
    conn.request("POST", resource_url_path, params, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")
