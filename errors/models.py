from django.db import models

# Create your models here.

class RequestReport(models.Model):
    error_response = models.JSONField(null=True)
    error_msg = models.CharField(max_length=1000, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user_nickname = models.CharField(max_length=100, null=True)
    user_email = models.CharField(max_length=100 , null=True)
    is_guest = models.BooleanField(default=False)
    queue_title = models.CharField(max_length=100, null=True)
    queue_id = models.CharField(max_length=100, null=True)
    entry_title = models.CharField(max_length=100, null=True)
    entry_id = models.CharField(max_length=100, null=True)

    @classmethod
    def process_request(cls, request, user):
        try:
            response = request.execute()
            processed_response =  process_response(response)
        except Exception as e:
            error_msg = e
            new_error_report = cls(
                error_msg=error_msg,
                user=user,
                queue=None,
                entry=None,
                error_response=response,
                user_nickname=user.nickname,
            )
            new_error_report.save()
            return False, f"An error occurred: {e}."
        return True, processed_response

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
    elif kind == "youtube#channelListResponse":
        return parse_channel_result(response)
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
    items = response["items"][0]
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
        # thumbnail data is in response_item['snippet']['thumbnails'] then with different sizes
        "duration": response_item["contentDetails"]["duration"],
        # region restrictions is in response_item['contentDetails']['regionRestriction'] etc
        # private, public, and unlisted as possible values
        "status": response_item["status"]["privacyStatus"],
    }
    return video_result
