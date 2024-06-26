from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from .models import Queue, Entry, has_authorization
from profiles.models import make_user
from django.contrib import messages
from yt_query.yt_api_utils import YT
from requests.exceptions import HTTPError
from utils import abbreviate
from errors.views import error_handler


def create_queue(request):
    """
    Renders the create queue form if the request method is GET. Creates a new
    queue if the user is authenticated and the request method is POST.
    Args: request (HttpRequest)
    Returns: Redirects to edit_queue if successful.
    """
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to create a queue."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    elif request.method == "POST":
        if not request.POST.get("queue-title"):
            msg = "Queue title cannot be empty."
            msg_type = messages.ERROR
        else:
            queue_title = request.POST["queue-title"]
            queue_description = request.POST.get("queue-description")
            queue = Queue(title=queue_title, description=queue_description,
                          owner=user)
            queue.save()
            msg = f"{queue.title} has been created."
            msg_type = messages.SUCCESS
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    else:
        response = render(request, "queues/create_queue.html")
    response = error_handler(request, response)
    return response


def edit_queue(request, queue_id):
    """
    Retrieves and processes queue information based on the given request
    and queue ID.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the appropriate page after editing the queue.
    """
    user = make_user(request)
    queue = get_object_or_404(Queue, id=queue_id)
    is_owner = user == queue.owner
    recent_search = request.POST.get("searchQuery", None)
    search_results = []
    has_auth = has_authorization(user, queue_id)
    if not has_auth:
        msg = "You do not have authorization to edit this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        if user.is_authenticated:
            response = HttpResponseRedirect(reverse("profile"))
        else:
            response = HttpResponseRedirect(reverse("account_login"))
    else:
        yt = YT(user)
        if request.method == "GET":
            recent_search, search_results = yt.get_last_search(request,
                                                               queue_id)
        elif request.method == "POST" and recent_search:
            try:
                search_results = yt.search_videos(recent_search)
            except HTTPError as e:
                msg = f"The following error occurred: {e}"
                msg_type = messages.ERROR
                search_results = []
                messages.add_message(request, msg_type, msg)
            else:
                request = yt.save_search(
                    request, queue_id, recent_search, search_results
                )
        if recent_search == "None":
            recent_search = "Search YouTube"
        if queue.length == 1:
            num_entries = " Entry"
        else:
            num_entries = " Entries"
        if search_results:
            for result in search_results:
                result['title'] = abbreviate(result['title'], 30)
        context = {
            "queue": queue,
            "recent_search": recent_search,
            "search_results": search_results,
            "user": user,
            "is_owner": is_owner,
            "num_entries": num_entries
        }
        response = render(request, "queues/edit_queue.html", context)
    response = error_handler(request, response)
    return response


def delete_queue(request, queue_id):
    """
    Checks for authorization and then deletes the queue. Deletion of playlists
    on YouTube is temporarily disabled due to API rate limits.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the profile page.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if queue.owner == user:
        queue.delete()
        msg = f"{queue.title} has been deleted. If the queue was published"
        msg += " on YouTube, it will remain there. To remove the playlist from"
        msg += " YouTube, click the Unpublish button."
        msg_type = messages.SUCCESS
        response = HttpResponseRedirect(reverse("profile"))
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    messages.add_message(request, msg_type, msg)
    response = error_handler(request, response)
    return response


def unpublish(request, queue_id):
    """
    Checks for authorization and then deletes the playlist from YouTube.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the eqit_queue page.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if queue.owner == user:
        msg, msg_type = queue.unpublish()
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    response = error_handler(request, response)
    return response


def publish(request, queue_id):
    """
    Publishes a queue to YouTube. Checks if the user has permission and an
    associated YouTube channel.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the edit_queue page.
    """
    user = make_user(request)
    queue = get_object_or_404(Queue, id=queue_id)
    if not queue.owner.youtube_channel:
        msg = "There is no channel associated with this queue. It can not be"\
              "published. The queue owner must add a valid YouTube account."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    elif user == queue.owner:
        msg, msg_type = queue.publish()
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    else:
        msg = "Only the queue owner can publish the queue."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    messages.add_message(request, msg_type, msg)
    response = error_handler(request, response)
    return response


def sync(request, queue_id):
    """
    Updates the corresponding YouTube playlist to match the queue.
    Args: reques (HttpRequest)
          queue_id (int)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if not user == queue.owner:
        msg = "You must be the owner of the queue to sync it with YouTube."
        msg_type = messages.ERROR
    elif not queue.published:
        msg = "This queue must be published before it can be synced with"\
              " YouTube."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
    elif queue.synced:
        msg = "This queue is already synced with YouTube."
        msg_type = messages.INFO
    else:
        msg, msg_type = queue.sync()
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    response = error_handler(request, response)
    return response


def add_entry(request, queue_id, video_id):
    """
    Adds an entry/video to the queue.
    Args: request (HttpRequest)
          queue_id (int)
          video_id (str)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    msg_type = messages.ERROR
    if not user.is_authenticated and not user.is_guest:
        msg = "You do not have authorization to add entries to this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    elif not has_authorization(user, queue.id):
        msg = "You do not have authorization to add entries to this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("profile"))
    else:
        if queue.full:
            msg = "This queue is at max capacity."
            if user == queue.owner:
                msg += "Remove some entries if you would like to add more."
            else:
                msg += "Ask the owner to remove some entries."
            msg_type = messages.ERROR
        else:
            try:
                yt = YT(user)
                video_data = yt.find_video_by_id(video_id)
            except HTTPError as e:
                msg = f"The following error occurred: {e}"
                msg_type = messages.ERROR
            except ValueError as e:
                msg = "There were too many videos associated with that ID."\
                      " Try adding a different video."
                msg += str(e)
                msg_type = messages.ERROR
            else:
                if video_data["status"] != "private":
                    del video_data["status"]
                    entry = Entry(**video_data)
                    entry.p_queue = queue
                    # adds entry to end of list
                    entry._position = queue.length
                    entry.user = user.nickname
                    queue.save()
                    entry.save()
                    msg = f"{entry.title} has been added to the queue."
                    msg_type = messages.SUCCESS
                else:
                    msg = "This video is private. It cannot be added."
                    msg_type = messages.ERROR
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    response = error_handler(request, response)
    return response


def delete_entry(request, queue_id, entry_id):
    """
    Checks for authorization and then deletes an entry from a queue.
    Args: request (HttpRequest)
          queue_id (int)
          entry_id (int)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    entry = get_object_or_404(Entry, id=entry_id)
    if user == queue.owner:
        queue.remove_entry(entry)
        msg = f"{entry.title} has been removed from the queue."
        msg_type = messages.SUCCESS
    else:
        msg = "You do not have permission to delete this entry."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    response = error_handler(request, response)
    return response


def swap(request, entry_id, other_entry_position):
    """
    Swaps the positions of two entries in the queue in the back-end and then
    sends the updated entry data to the front-end.
    Args: request (HttpRequest)
          entry_id (int)
          other_entry_position (int)
    Returns: JSON response containing the swapped entry data.
    """
    entry = get_object_or_404(Entry, id=entry_id)
    new_entry, other_entry = entry.swap_entry_positions(other_entry_position)
    if not other_entry:
        other_entry = entry
        new_entry = entry
    entry_data = {
        "id": new_entry.id,
        "title": new_entry.title,
        "position": new_entry.position,
        "addedBy": new_entry.username
    }
    other_entry_data = {
        "id": other_entry.id,
        "title": other_entry.title,
        "position": other_entry.position,
        "user": other_entry.username
    }
    response_dict = {"entry1": entry_data, "entry2": other_entry_data}
    return JsonResponse(response_dict)


def gain_access(request, queue_secret, owner_secret):
    """
    Handles sharing of queues to both guest users and users with an account.
    Args: request (HttpRequest)
          queue_secret (str)
          owner_secret (str)
    Returns: Redirects the user to a guest sign in page if appropriate, or the
             edit page for the relevant queue. If the user is already logged
             in, it adds the queue to their list of collaborative queues.
    """
    queue = get_object_or_404(Queue, secret=queue_secret)
    user = make_user(request)
    msg = ""
    if owner_secret != queue.owner.secret:
        msg += "This link is not valid. Please request another one from the"\
               f"{queue.owner.nickname}."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("index"))
    else:
        request.session["queue_id"] = queue.id
        request.session["redirect_action"] = "edit_queue"
        if not user.is_authenticated and not user.is_guest:
            msg = "Please sign in or create a guest account to gain access to"\
                  "this queue."

            msg_type = messages.INFO
            response = HttpResponseRedirect(reverse("guest_sign_in"))
        else:
            msg_type = messages.SUCCESS
            response = HttpResponseRedirect(reverse("edit_queue",
                                                    args=[queue.id]))
            # If there is already a guest stored in the session
            if user.is_guest:
                user.queue_id = queue.id
                request.session["guest_user"] = user.serialize()
                msg = f"Welcome back {user.nickname}."
                msg += f"{queue.owner.nickname} has given you access to"\
                       f"{queue.title}."
            elif queue not in user.all_queues:
                user.other_queues.add(queue)
                queue.save()
                user.save()
                msg = f"{queue.title} has been added to your list of queues."
            else:
                msg = f"{queue.title} is already in your list of queues."
    messages.add_message(request, msg_type, msg)
    response = error_handler(request, response)
    return response
