# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

import os
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .models import Profile



SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    # 'https://www.googleapis.com/auth/youtube.readonly'
    ]

def retrieve_creds(user:'Profile') -> dict[str,str]:
    if user.tokens_valid:
        return user.get_credentials()
    credentials = get_creds()
    user.add_credentials(credentials)
    return credentials

def get_creds():
    credentials = None
    flow = InstalledAppFlow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES)

    # runs a server to open a page so we can ask for credentials.
    # prompt="consent" is a fix he found online
    flow.run_local_server(port=8080)

    credentials = flow.credentials
    return credentials.to_json()

def get_creds_url():
    flow = Flow.from_client_secrets_file("oauth_creds.json",
                                         scopes=SCOPES,
                                         redirect_uri="http://localhost:8000/")

    auth_url, state = flow.authorization_url(prompt='consent')
    print(auth_url)
    print(state)
    fetch_result = flow.fetch_token()
    credentials = flow.credentials
    print(fetch_result)
    print(credentials)
    return auth_url

