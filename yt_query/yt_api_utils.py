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
    """
    A Class for handling interaction with the YouTube Data API.
    """
    def __init__(self, user: "Profile") -> None:
        self.user = user
        self.api_key = YOUTUBE_API_KEY
        self.user_service = self.connect_oauth()
        self.guest_service = self.connect_simple()

    def connect_oauth(self) -> "Service":
        """
        Connects to the YouTube Data API using OAuth 2.0 authentication.
        Returns: "Service"
                 str
        """
        if self.user.has_tokens:
            credentials = self.user.google_credentials
            return build("youtube", "v3", credentials=credentials)
        return ""

    def connect_simple(self) -> "Service":
        """
        Connects to the YouTube Data API using a developer key.
        Returns: Service
        """
        return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def find_user_youtube_data(self):
        """
        Fetches YouTube Channel and Handle for an authenticated user.
        types.
        Returns: List[str,str]
        """
        request = self.user_service.channels().list(part="snippet", mine=True)
        response = request.execute()
        return parse_channel_result(response)

    def search_videos(self, query) -> list[str]:
        """
        Searches for videos on YouTube based on a given query. It returns their
        id, and title.
        Args: query (str)
        Returns: list[str]: A list of video IDs that match the search query.           
        """
        request = self.guest_service.search().list(
            part="snippet",
            type="video",
            q=query,
            maxResults=10,
        )
        response = request.execute()
        return process_response(response)

    def find_video_by_id(self, video_id):
        """
        Finds a video on YouTube based on the given video_id.
        Args: video_id (str)
        Returns: dict
        """
        request = self.guest_service.videos().list(
            part="snippet,contentDetails,status",
            id=video_id,
        )
        response = request.execute()
        return process_response(response)

    def create_playlist(self, title, description) -> str:
        """
        Creates a new playlist with the given title and description.
        Args: title (str)
              description (str)
        Returns: str
        """
        body = {
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "unlisted"},
        }
        request = self.user_service.playlists().insert(
            part="snippet,status,id", body=body
        )
        response = request.execute()
        return response

    def delete_playlist(self, playlist_id):
        """
        Deletes a playlist with the given playlist_id.
        Args: playlist_id (str)
        Returns: response (HttpResponse)
        """
        request = self.user_service.playlists().delete(id=playlist_id)
        response = request.execute()
        return response

    def move_playlist_item(self, entry: "Entry"):
        """
        Updates a playlist item with the provided entry.
        Args: entry (Entry)
        Returns: response (HttpResponse)
        """
        request = self.user_service.playlistItems().update(
            part="snippet,id", body=entry.body
        )
        response = request.execute()
        return process_response(response)

    def add_entry_to_playlist(self, body):
        """
        Inserts an entry into a playlist using the provided body.
        Args: body (dict)
        Returns: response (HttpResponse)
        """
        request = self.user_service.playlistItems().insert(part="snippet,id", body=body)
        response = request.execute()
        return process_response(response)

    def remove_playlist_item(self, playlist_item_id):
        """
        Removes a playlist item from the user's playlist.
        Args: playlist_item_id (str)
        Returns: dict
        """
        request = self.user_service.playlistItems().delete(id=playlist_item_id)
        response = request.execute()
        return response

    @classmethod
    def get_last_search(cls, request, queue_id):
        """
        Get the last search query and search results for a given queue ID.
        Args: request (HttpRequest)
              queue_id (str)
        Returns: Tuple containing the last query and last search results.
        """
        last_queue_query = request.session.get(f"queue_{queue_id}", {})
        last_query = last_queue_query.get("last_query")
        last_search = last_queue_query.get("last_search")
        return last_query, last_search

    @classmethod
    def save_search(cls, request, queue_id, recent_search, search_results):
        """
        Save the recent search and search results to the session for a given
        queue ID.
        Args: request (HttpRequest)
              queue_id (str)
              recent_search (str)
              search_results (list)
        Returns: HttpRequest
        """
        last_queue_query = {"last_query": recent_search, "last_search": search_results}
        request.session[f"queue_{queue_id}"] = last_queue_query
        return request


def process_response(response: dict):
    """
    Process the given response dictionary and return the appropriate result
    based on its kind.
    Args: response (dict)
    Returns: Union[list,dict]
    """
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
    """
    Parses the response from a playlist query and extracts the playlist items.
    Args: response (dict)
    Returns: list
    """
    items = response["items"]
    if items:
        return [parse_playlist_item_result(item) for item in items]
    return []


def parse_playlist_item_result(item):
    """
    Parses the result of a playlist item query and extracts relevant information.
    Args: item (dict)
    Returns: dict
    """
    snippet_keys = {"title", "playlistId", "position", "resourceId"}
    result_dict = {
        key: value for key, value in item["snippet"].items() if key in snippet_keys
    }
    result_dict.update({"kind": item["kind"], "id": item["id"]})
    return result_dict


def parse_channel_result(response):
    """
    Parses the response from a channel query and extracts the channel ID and
    custom URL.
    Args: response (dict)
    Returns: tuple
    """
    try:
        items = response["items"][0]
    except IndexError as e:
        print(response)
        print(e)
    except KeyError as e:
        print(response)
        print(e)
    id = items["id"]
    custom_url = items["snippet"]["customUrl"]
    return id, custom_url


def parse_search_result(result: dict) -> dict:
    """
    Parses the search result and extracts the video ID from the input dictionary.
    Args: result (dict)
    Returns: dict
    """
    id = result["id"]["videoId"]
    search_result = result["snippet"]
    search_result["id"] = id
    return search_result


def parse_video_result(response_item: dict) -> dict:
    """
    Parses the video result and extracts the relevant information from the
    input dictionary.
    Args: response_item (dict)
    Returns: dict
    """
    video_result = {
        "kind": response_item["kind"],
        "yt_id": response_item["id"],
        "video_id": response_item["id"],
        "title": response_item["snippet"]["title"],
        "status": response_item["status"]["privacyStatus"],
    }
    return video_result
