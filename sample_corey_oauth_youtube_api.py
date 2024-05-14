# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

credentials = None

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly', # given the above, this may not be necessary as well
    'https://www.googleapis.com/auth/youtubepartner' # I don't think this is necessary
    ]

if os.path.exists("token.pickle"):
    print("Loading Credentials from file...")
    # "rb" means read bytes
    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Refreshing access token...")
        credentials.refresh(Request())
    else:
        print("Fetching new tokens...")
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json",
                                                 scopes=SCOPES)
        # prompt='consent' should not be necessary
        # authorization_prompt_message='' means that the prompt won't be printed to the console
        flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
        credentials = flow.credentials

        # "wb" is write bytes
        with open("token.pickle", "wb") as f:
            print("Saving credentials ...")
            pickle.dump(credentials, f)


# the below uses a dev api key for finding public things
# yt = build(serviceName='youtube', version='v3',developerKey=API_KEY)
yt = build(serviceName = 'youtube', version='v3', credentials = credentials)

request = yt.playlistItems().list(part="status",
                             playlistId="UUCezIgC97PvUuR4_gbFUs5g")

response = request.execute()

print(response)


yt.close()
