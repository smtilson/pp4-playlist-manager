import google.oauth2.credentials as g_oa2_creds
from google_auth_oauthlib.flow import Flow
from utils import get_data_from_path, json_to_dict
import pickle
import os
import requests
from .models import Credentials
from profiles.models import Profile, make_user
from google.auth.transport.requests import Request


if os.path.isfile("env.py"):
    import env

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]

LOCAL = eval(os.environ.get("LOCAL"))
if LOCAL:
    REDIRECT_URI = "http://localhost:8000/"
else:
    REDIRECT_URI = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/"


def get_authorization_url():
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    # the second return value is state, which is not used currently.
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return authorization_url


def get_tokens(authorization_path):
    state = get_data_from_path(authorization_path)[0]
    flow = Flow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI
    authorization_response = REDIRECT_URI + authorization_path
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials


# Gotten from the YouTubeAPI documentation
def revoke_tokens(user):
    # this seems to be working but is returning an invalid service code.
    if not user.has_tokens:
        return f"This app does not currently have authorization for {user.nickname}"
    else:        
        credentials = user.google_credentials
        requests.post('https://oauth2.googleapis.com/revoke',
    params={'token': credentials.token},
    headers = {'content-type': 'application/x-www-form-urlencoded'})
    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    #print(revoke)


    status_code = getattr(revoke, "status_code")
    return status_code
    

def refresh_tokens(user):
    credentials = user.google_credentials
    #old_dict = json_to_dict(credentials.to_json())
    #new_dict = {}
    credentials.refresh(Request())
    #new_dict = json_to_dict(credentials.to_json())
    user.set_credentials(credentials)
    #print(old_dict == new_dict)

