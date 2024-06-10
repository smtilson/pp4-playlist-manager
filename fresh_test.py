from profiles.models import Profile
import os
import googleapiclient.discovery
from yt_auth.token_auth import retrieve_creds
from yt_auth.models import Credentials
from yt_auth.utils import json_to_dict
from profiles.models import Profile
from google.oauth2.credentials import Credentials as gCredentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"



# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build



SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    # 'https://www.googleapis.com/auth/youtube.readonly'
    ]

CREDENTIALS = retrieve_creds()
official_creds_dict = json_to_dict(CREDENTIALS.to_json())
del official_creds_dict['expiry']
test_official_creds = gCredentials(**official_creds_dict)

test_creds = Credentials()
test_creds.set_credentials(CREDENTIALS)
test_dict = test_creds.to_dict()
del test_dict['has_tokens']
del test_dict['expiry']
print(official_creds_dict == test_dict)
#for key, value in official_cred_dict.items():
 #   print(f"{key=})
new_test_creds = test_creds.to_google_credentials()
print(type(CREDENTIALS))
print(type(new_test_creds))

def sample_query(credentials):
    youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

    request = youtube.playlistItems().list(part="snippet",playlistId="PLaPvip_wdwX1WE3uO2Ol74aCi78fZGMeZ")

    response = request.execute()

    #print(response)
    response = json_to_dict(response)
    with open("sean_data.txt","a") as f:
        for key, value in response.items():
            f.write(f"{key=}:{value}")
            f.write("\n")


