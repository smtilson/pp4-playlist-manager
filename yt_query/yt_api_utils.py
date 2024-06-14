# Write helper functions for interacting with youtube API
# from profiles.models import Profile
from googleapiclient.discovery import build
from utils import produce_url_code
from env import YOUTUBE_API_KEY
from django.shortcuts import get_object_or_404


class YT:
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
        request = self.user_service.channels().list(part="snippet,contentDetails", mine=True)
        response = request.execute()
        items = response["items"][0]
        id = items["id"]
        custom_url = items["snippet"]["customUrl"]
        return id, custom_url

    def search_videos(self, query) -> list[str]:
        request = self.guest_service.search().list(
            # maxResults=5 in order to limit API usage
            part="snippet", type="video", q=query, maxResults=5
        )
        response = request.execute()
        return process_response(response)

    def find_video_by_id(self, video_id):
        # check privacy status
        # check blocked status, eventually
        request = self.guest_service.videos().list(
            part="snippet,contentDetails,player,status",
            id=video_id,
        )
        response = request.execute()
        # return response
        return process_response(response)

    def create_playlist(self, title, description) -> str:
        request = self.user_service.playlists().insert(
            part="snippet,status,id", body={"snippet": {"title": title, "description":description},"status":{"privacyStatus":"unlisted"}}
        )
        response = request.execute()
        
        #playlist_id = process_response(response)
        #return playlist_id
    
    def delete_playlist(self,playlist_id):
        request = self.user_service.playlists().delete(id=playlist_id)
        response = request.execute()
        return response

    def move_playlist_item(self,video_id,new_position,playlist_item_id,playlist_id):
        body = {"kind":"youtube#playlistItem","id":playlist_item_id,"snippet":{"playlistId":playlist_id, "position":new_position,"resourceId":{"kind":"youtube#video","videoId":video_id}}}
        request = self.user_service.playlistItems().update(part="snippet,id",body=body)
        response = request.execute()

    def add_entry_to_playlist(self,video_id,position,playlist_id):
        print("attempting to add")
        print("body",body)
        body = {"snippet":{"playlistId":playlist_id,"position":position, "resourceId":{"kind":"youtube#video","videoId":video_id}}}
        request = self.user_service.playlistItems().insert(part="snippet,id",body=body)
        print(request.uri)
        response = request.execute()
        return response

    @classmethod
    def get_last_search(cls,request,queue_id):
        last_queue_query = request.session.get(f"queue_{queue_id}",{})
        last_query = last_queue_query.get("last_query")
        last_search = last_queue_query.get("last_search")
        return last_query, last_search
    
    @classmethod
    def save_search(cls,request,queue_id,recent_search,search_results):
        last_queue_query = {"last_query":recent_search,"last_search":search_results}
        request.session[f"queue_{queue_id}"] = last_queue_query
        return request

def process_response(response: dict):
    # how can I refactor this?
    # there is the dictionary storing callables that I did...
    if response["kind"] == "youtube#searchListResponse":
        return [parse_search_result(result) for result in response["items"]]
    elif response["kind"] == "youtube#videoListResponse":
        if len(response["items"]) == 1:
            return parse_video_result(response["items"][0])
        else:
            raise ValueError("There are two many items for this request.")
    elif response["kind"] == "youtube#playlist":
        return response["id"]
    else:
        return response

def parse_search_result(result: dict) -> dict:
    # eventually this should return less data than the whole snippet and Id
    id = result["id"]["videoId"]
    search_result = result["snippet"]
    search_result["id"] = id
    return search_result


def parse_video_result(response_item: dict) -> dict:
    video_result = {
        "kind":response_item["kind"],
        "yt_id":response_item["id"],
        "video_id": response_item["id"],
        "title": response_item["snippet"]["title"],
        # thumbnail data is in response_item['snippet']['thumbnails'] then with different sizes
        "duration": response_item["contentDetails"]["duration"],
        # region restrictions is in response_item['contentDetails']['regionRestriction'] etc
        # private, public, and unlisted as possible values
        "status": response_item["status"]["privacyStatus"],
    }
    return video_result
