# The code in this file is taken from the oauth tutorial and the youtube api tutorial
# remember to give credit in the project. At approximately 32 minutes

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

yt = build(serviceName = 'youtube', version='v3', credentials = credentials)

request = yt.playlistItems().list(part="status",
                             playlistId="UUCezIgC97PvUuR4_gbFUs5g")

response = request.execute()

print(response)

