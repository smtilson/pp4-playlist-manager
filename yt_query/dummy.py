from yt_api_utils import YT
from profiles.models import Profile
import os
import googleapiclient.discovery
from yt_auth.token_auth import refresh_tokens, retrieve_creds
from yt_auth.utils import json_to_dict

SEAN = Profile.objects.all().first()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
yt = YT(SEAN)

# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/youtube',]

credentials = SEAN.google_credentials
#print(SEAN.credentials.to_dict())
#refresh_tokens(SEAN)
#print(SEAN.credentials.to_dict())
#input()
#credentials = retrieve_creds()
youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)


request = youtube.channels().list(part="snippet,contentDetails",mine=True)



response = request.execute()
print(response)
#with open("sean_data.txt","a") as f:
#    for key, value in response.items():
#        f.write(f"{key=}:{value}")
#        f.write("\n")


