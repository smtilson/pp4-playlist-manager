import google.oauth2.credentials as g_oa2_creds
from google_auth_oauthlib.flow import Flow
from utils import get_data_from_path, json_to_dict
import pickle
import os
import requests
from .models import Credentials
from profiles.models import Profile, make_user
from google.auth.transport.requests import Request

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]

# this should be changed to an environment variable
REDIRECT_URI = "http://localhost:8000/"


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
    if not user.has_tokens:
        return f"This app does not currently have authorization."
    else:
        credentials = user.google_credentials
    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")
    if status_code == 200:
        return "Credentials successfully revoked."
    else:
        return "An error occurred."


def refresh_tokens(user):
    # maybe this should be called when we already know the tokens are expired so we can get authorization again.
    credentials = user.google_credentials
    print(credentials.valid)
    print(credentials.expired)
    old_dict = json_to_dict(credentials.to_json())
    new_dict = {}
    credentials.refresh(Request())
    new_dict = json_to_dict(credentials.to_json())
    user.set_credentials(credentials)
    print(old_dict == new_dict)


def save_creds(credentials):
    # "wb" is write bytes
    with open("token.pickle", "wb") as f:
        print("Saving credentials ...")
        pickle.dump(credentials, f)


def retrieve_creds():
    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)
    return credentials
