
from requests import request
import json
from datetime import datetime
from env import oauth_creds
from authlib.integrations.django_client import OAuth

# constants
SPACE = " "
credentials = oauth_creds['web']
CLIENT_ID = credentials['client_id']
CLIENT_SECRET = credentials['client_secret']
EVENT_ID = "some event id from lup here"

# obtain access token
auth_url = credentials['auth_uri']
token_url = credentials["token_uri"]

oauth = OAuth()
yt_auth = oauth.create_client('yt_auth')
token = oauth.yt_auth.authorize_access_token(request)