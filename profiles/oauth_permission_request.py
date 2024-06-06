# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from .models import Profile
from .utils import get_user_profile


SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    #'https://www.googleapis.com/auth/youtube.readonly'
    ]

def get_creds():
    flow = InstalledAppFlow.from_client_secrets_file("oauth_creds.json", scopes=SCOPES)

    # runs a server to open a page so we can ask for credentials.
    # prompt="consent" is a fix he found online
    flow.run_local_server(port=8080,prompt="consent",
                      authorization_prompt_message='')

    credentials = flow.credentials
    return credentials.to_json()

