# Write helper functions for interacting with youtube API
#from profiles.models import Profile
from googleapiclient.discovery import build


class YT:
    def __init__(self, user:'Profile') -> None:
        self.user = user
        self.service = self.connect()
    
    def connect(self) -> 'Service':
        credentials = self.user.google_credentials
        return build("youtube", "v3", credentials=credentials)
        
    def find_user_youtube_data(self):
        request = self.service.channels().list(part="snippet,contentDetails",mine=True)
        response = request.execute()
        items = response['items'][0]
        id = items['id']
        custom_url = items['snippet']['customUrl']
        return id, custom_url