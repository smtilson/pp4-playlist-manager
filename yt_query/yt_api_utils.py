# Write helper functions for interacting with youtube API
# from profiles.models import Profile
from googleapiclient.discovery import build
import os
from errors.models import RequestReport

if os.path.isfile("env.py"):
    import env


YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")


class YT:
    MAX_QUEUE_LENGTH = 20

    def __init__(self, user: "Profile") -> None:
        self.user = user
        self.api_key = YOUTUBE_API_KEY
        self.user_service = self.connect_oauth()
        self.guest_service = self.connect_simple()

    def connect_oauth(self) -> "Service":
        if self.user.has_tokens:
            credentials = self.user.google_credentials
            return build("youtube", "v3", credentials=credentials)
        return ""

    def connect_simple(self) -> "Service":
        return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def find_user_youtube_data(self):
        request = self.user_service.channels().list(part="snippet", mine=True)
        return RequestReport.process_request(request,self.user)
        
    def search_videos(self, query) -> list[str]:
        request = self.guest_service.search().list(
            # maxResults=5 in order to limit API usage
            part="snippet",
            type="video",
            q=query,
            maxResults=5,
        )
        return RequestReport.process_request(request,self.user)

    def find_video_by_id(self, video_id):
        # check blocked status, eventually
        request = self.guest_service.videos().list(
            part="snippet,contentDetails,status",
            id=video_id,
        )
        return RequestReport.process_request(request,self.user)
    
    def create_playlist(self, title, description) -> str:
        body = {
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "unlisted"},
        }
        request = self.user_service.playlists().insert(
            part="snippet,status,id", body=body
        )
        return RequestReport.process_request(request,self.user)
    
    def delete_playlist(self, playlist_id):
        request = self.user_service.playlists().delete(id=playlist_id)
        return RequestReport.process_request(request,self.user)

    def move_playlist_item(self, entry: "Entry"):
        request = self.user_service.playlistItems().update(
            part="snippet,id", body=entry.body
        )
        return RequestReport.process_request(request,self.user)

    def add_entry_to_playlist(self, body):
        request = self.user_service.playlistItems().insert(part="snippet,id", body=body)
        return RequestReport.process_request(request,self.user)

    def remove_playlist_item(self, playlist_item_id):
        request = self.user_service.playlistItems().delete(id=playlist_item_id)
        return RequestReport.process_request(request,self.user)

    @classmethod
    def get_last_search(cls, request, queue_id):
        last_queue_query = request.session.get(f"queue_{queue_id}", {})
        last_query = last_queue_query.get("last_query")
        last_search = last_queue_query.get("last_search")
        return last_query, last_search

    @classmethod
    def save_search(cls, request, queue_id, recent_search, search_results):
        last_queue_query = {"last_query": recent_search, "last_search": search_results}
        request.session[f"queue_{queue_id}"] = last_queue_query
        return request


