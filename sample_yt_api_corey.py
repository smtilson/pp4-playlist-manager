# This code is related to the youtube tutorial
# https://www.youtube.com/watch?v=th5_9woFJmk

from googleapiclient.discovery import build
from env import ytp_api_key, seans_yt_channel_id, seans_yt_user_id


key = ytp_api_key
channel = seans_yt_channel_id
user_id = seans_yt_user_id
yt_service = build('youtube','v3', developerKey=key)
request1 = yt_service.channels().list(
        part="statistics,contentDetails",
        forHandle="seantilson8728"
    )
response1 = request1.execute()
print(response1['items'])
request2 = yt_service.channels().list(
        part="statistics,contentDetails",
        id=channel
    )
response2 = request2.execute()
print(response2['items'])
request3 = yt_service.channels().list(
        part="statistics,contentDetails",
        forUsername="seantilson8728"
    )
response3 = request3.execute()
print(response3['items'])

# note part argument specifies what information we want returned

yt_service.close()