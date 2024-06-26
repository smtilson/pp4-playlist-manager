# Helper class and methods for interacting with youtube API
# from profiles.models import Profile
from googleapiclient.discovery import build
from utils import produce_url_code
#from env import YOUTUBE_API_KEY
import os
from django.shortcuts import get_object_or_404
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
        response = request.execute()
        return parse_channel_result(response)

    def search_videos(self, query) -> list[str]:
        request = self.guest_service.search().list(
            # maxResults=5 in order to limit API usage
            part="snippet",
            type="video",
            q=query,
            maxResults=5,
        )
        response = request.execute()
        with open("test_error_response.txt", "w", encoding="utf-8") as f:
            f.write(str(response))
        return process_response(response)

    def find_video_by_id(self, video_id):
        # check blocked status, eventually
        request = self.guest_service.videos().list(
            part="snippet,contentDetails,status",
            id=video_id,
        )
        response = request.execute()
        # return response
        return process_response(response)

    def create_playlist(self, title, description) -> str:
        body = {
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "unlisted"},
        }
        request = self.user_service.playlists().insert(
            part="snippet,status,id", body=body
        )
        response = request.execute()
        return response
        # return process_response(response)

    def delete_playlist(self, playlist_id):
        request = self.user_service.playlists().delete(id=playlist_id)
        response = request.execute()
        return response

    def get_published_playlist(self, playlist_id):
        request = self.guest_service.playlistItems().list(
            part="snippet,id", playlistId=playlist_id, maxResults=20
        )
        response = request.execute()
        return process_response(response)

    def move_playlist_item(self, entry: "Entry"):
        request = self.user_service.playlistItems().update(
            part="snippet,id", body=entry.body
        )
        response = request.execute()
        return process_response(response)

    def add_entry_to_playlist(self, body):
        request = self.user_service.playlistItems().insert(part="snippet,id", body=body)
        response = request.execute()
        return process_response(response)

    def remove_playlist_item(self, playlist_item_id):
        request = self.user_service.playlistItems().delete(id=playlist_item_id)
        response = request.execute()
        return response

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


def process_response(response: dict):
    # how can I refactor this?
    # there is the dictionary storing callables that I did...
    kind = response["kind"]
    if kind == "youtube#searchListResponse":
        return [parse_search_result(result) for result in response["items"]]
    elif kind == "youtube#videoListResponse":
        if len(response["items"]) == 1:
            return parse_video_result(response["items"][0])
        else:
            raise ValueError("There are two many items for this request.")
    elif kind == "youtube#channelListResponse":
        return parse_channel_result(response)
    elif kind == "youtube#playlistItemListResponse":
        return parse_playlist_result(response)
    elif kind == "youtube#playlistItem":
        return parse_playlist_item_result(response)
    else:
        return response


def parse_playlist_result(response):
    items = response["items"]
    if items:
        return [parse_playlist_item_result(item) for item in items]
    return []


def parse_playlist_item_result(item):
    snippet_keys = {"title", "playlistId", "position", "resourceId"}
    result_dict = {
        key: value for key, value in item["snippet"].items() if key in snippet_keys
    }
    result_dict.update({"kind": item["kind"], "id": item["id"]})
    return result_dict


def parse_channel_result(response):
    try:
        items = response["items"][0]
    except IndexError as e:
        print(response)
    except KeyError as e:
        print(response)
    id = items["id"]
    custom_url = items["snippet"]["customUrl"]
    return id, custom_url


def parse_search_result(result: dict) -> dict:
    # eventually this should return less data than the whole snippet and Id
    id = result["id"]["videoId"]
    search_result = result["snippet"]
    search_result["id"] = id
    return search_result


def parse_video_result(response_item: dict) -> dict:
    video_result = {
        "kind": response_item["kind"],
        "yt_id": response_item["id"],
        "video_id": response_item["id"],
        "title": response_item["snippet"]["title"],
        "status": response_item["status"]["privacyStatus"],
    }
    return video_result
