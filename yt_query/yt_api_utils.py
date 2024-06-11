# Write helper functions for interacting with youtube API
# from profiles.models import Profile
from googleapiclient.discovery import build
from utils import produce_url_code


class YT:
    def __init__(self, user: "Profile") -> None:
        self.user = user
        self.service = self.connect()

    def connect(self) -> "Service":
        credentials = self.user.google_credentials
        return build("youtube", "v3", credentials=credentials)

    def find_user_youtube_data(self):
        request = self.service.channels().list(part="snippet,contentDetails", mine=True)
        response = request.execute()
        items = response["items"][0]
        id = items["id"]
        custom_url = items["snippet"]["customUrl"]
        return id, custom_url

    def search_videos(self, query) -> list[str]:
        request = self.service.search().list(
            part="snippet", type="video", q=query, maxResults=25
        )
        response = request.execute()
        return process_response(response)

    def find_video_by_id(self, video_id):
        # check privacy status
        # check blocked status, eventually
        request = self.service.videos().list(
            part="snippet,contentDetails,player,status",
            id=video_id,
        )
        response = request.execute()
        #return response
        return process_response(response)

def process_response(response: dict):
    if response["kind"] == "youtube#searchListResponse":
        return [parse_search_result(result) for result in response["items"]]
    elif response["kind"] == "youtube#videoListResponse":
        if len(response['items']) == 1:
            return parse_video_result(response['items'][0])
        else:
            raise ValueError("There are two many items for this request.")
    else:
        raise TypeError(
            f"process_response is not yet implemented for {response['kind']}."
        )


def parse_search_result(result: dict) -> dict:
    # eventually this should return less data than the whole snippet and Id
    id = result["id"]["videoId"]
    search_result = result["snippet"]
    search_result["id"] = id
    return search_result


def parse_video_result(response_item: dict) -> dict:
    video_result = {
        "video_id": response_item["id"],
        "title": response_item["snippet"]["title"],
        # thumbnail data is in response_item['snippet']['thumbnails'] then with different sizes
        "duration": response_item["contentDetails"]["duration"],
        # region restrictions is in response_item['contentDetails']['regionRestriction'] etc
        # private, public, and unlisted as possible values
        "status": response_item["status"]["privacyStatus"],
    }
    return video_result
