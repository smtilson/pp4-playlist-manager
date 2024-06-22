from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from errors.models import RequestReport
from .models import Queue, Entry, has_authorization
from profiles.models import make_user
from django.contrib import messages
from yt_query.yt_api_utils import YT
from requests.exceptions import HTTPError
from collections import defaultdict
from errors.views import error_handler, error_in_path


# Create your views here.
def debug_template(request):
    context = {}
    context["queue"] = Queue.objects.first()
    context["is_owner"] = True
    return render(request, "queues/owner_buttons_from_scratch.html", context)


def create_queue(request):
    # finished testing
    user = make_user(request)
    request = error_in_path(request)
    if not user.is_authenticated:
        msg = "You must be logged in to create a queue."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    elif request.method == "POST":
        if not request.POST["queue-title"]:
            raise ValueError("Queue title cannot be empty.")
        queue_title = request.POST["queue-title"]
        queue_description = request.POST.get("queue-description")
        queue = Queue(title=queue_title, description=queue_description, owner=user)
        queue.save()
        msg = f"{queue.title} has been created."
        messages.add_message(request, messages.SUCCESS, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    else:
        response = render(request, "queues/create_queue.html")
    response = error_handler(request, response)
    return response


def edit_queue(request, queue_id):
    # tested
    user = make_user(request)
    request = error_in_path(request)
    queue = get_object_or_404(Queue, id=queue_id)
    is_owner = user == queue.owner
    recent_search = request.POST.get("searchQuery", None)
    search_results = []
    if not has_authorization(user, queue_id):
        msg = "You do not have authorization to edit this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    else:
        yt = YT(user)
        if request.method == "GET":
            recent_search, search_results = yt.get_last_search(request, queue_id)
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
        context = {
            "queue": queue,
            "recent_search": recent_search,
            "search_results": search_results,
            "user": user,
            "is_owner": is_owner,
        }

        response = render(request, "queues/edit_queue.html", context)
    response = error_handler(request, response)
    return response


def delete_queue(request, queue_id):
    # finished testing
    """
    Checks for authorization and then deletes the queue. Deletion of playlists
    on YouTube is temporarily disabled due to API rate limits.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the profile page.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    request = error_in_path(request)
    # there should be a modal to double check on the front end
    if queue.owner == user:
        # commented out due to rate limit issues.
        # msg = queue.unpublish()
        # add in try except block if unpublish is added back in for HttpError
        queue.delete()
        msg = f"{queue.title} has been deleted. If the queue was published"
        msg += " on YouTube, it will remain there. To remove the playlist from"
        msg += " YouTube, click the Unpublish button."
        msg_type = messages.SUCCESS
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("profile"))
    response = error_handler(request, response)
    return response


def unpublish(request, queue_id):
    """
    Checks for authorization and then unpublishes the queue. Temporarily disabled.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the eqit_queue page.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    request = error_in_path(request)
    if queue.owner == user:
        try:
            queue.unpublish()
        except HTTPError as e:
            msg = f"The following error occurred: {e}"
            msg_type = messages.ERROR
        else:
            msg = f"{queue.title} has been removed from YouTube. To delete the"
            msg += "playlist from YouTube DJ, click the Delete button."
            msg_type = messages.SUCCESS
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("profile"))
    response = error_handler(request, response)
    return response


def publish(request, queue_id):
    user = make_user(request)
    request = error_in_path(request)
    queue = get_object_or_404(Queue, id=queue_id)
    if not queue.owner.youtube_channel:
        msg = "There is no channel associated with this queue. It can not be published. Please connect your account to a valid YouTube account in order."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    elif user == queue.owner:
        try:
            msg = queue.publish()
        except HTTPError as e:
            print("HTTPError hit on publish")
            msg = e
            msg_type = messages.ERROR
        else:
            msg_type = messages.SUCCESS
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    else:
        msg = "Only the queue owner can publish the queue."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    # does that work with a redirect response.
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
    request = error_in_path(request)
    if not user == queue.owner:
        msg = "You must be the owner of the queue in order to sync it with YouTube."
        msg_type = messages.ERROR
    elif not queue.published:
        msg = "This queue must be published before it can be synced with YouTube."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
    elif queue.synced:
        msg = "This queue is already synced with YouTube."
        msg_type = messages.INFO
    else:
        try:
            msg = queue.sync()
        except HTTPError as e:
            msg = f"The following error occurred: {e}"
            msg_type = messages.ERROR
        else:
            msg = f"{queue.title} has been synced with YouTube."
            msg_type = messages.SUCCESS
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
    request = error_in_path(request)
    msg_type = messages.ERROR
    if not has_authorization(user, queue):
        msg = "You do not have authorization to add entries to this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    if queue.full:
        msg = "This queue is at max capacity."
        if user == queue.owner:
            msg += "Remove some entries if you would like to add more."
        else:
            msg += "Ask the owner to remove some entries so you can add more."
        msg_type = messages.ERROR
    else:
        try:
            video_data = YT(user).find_video_by_id(video_id)
        except HTTPError as e:
            msg = f"The following error occurred: {e}"
            msg_type = messages.ERROR
        except ValueError as e:
            msg = f"There were too many videos associated with that ID. Try"
            msg += "adding a different video."
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
                msg = "This video is private. It cannot be added to the queue."
                msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    response = error_handler(request, response)
    return response


def delete_entry(request, queue_id, entry_id):
    # finished testing
    """
    Checks for authorization and then deletes an entry from a queue.
    Args: request (HttpRequest)
          queue_id (int)
          entry_id (int)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    request = error_in_path(request)
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
    # finished testing
    """
    Swaps the positions of two entries in the queue in the back-end and then
    sends the updated entry data to the front-end.
    Args: request (HttpRequest)
          entry_id (int)
          other_entry_position (int)
    Returns: JSON response containing the swapped entry data.
    """
    entry = get_object_or_404(Entry, id=entry_id)
    print("inside swap function")
    new_entry, other_entry = entry.swap_entry_positions(other_entry_position)
    if not other_entry:
        other_entry = entry
        new_entry = entry
    entry_data = {
        "id": new_entry.id,
        "title": new_entry.title,
        "position": new_entry.position,
        "addedBy": new_entry.username,
        "duration": new_entry.duration,
    }
    other_entry_data = {
        "id": other_entry.id,
        "title": other_entry.title,
        "position": other_entry.position,
        "user": other_entry.username,
        "duration": other_entry.duration,
    }
    response_dict = {"entry1": entry_data, "entry2": other_entry_data}
    print("swap done")
    return JsonResponse(response_dict)


def gain_access(request, queue_secret, owner_secret):
    # finished testing
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
    
    # I am not sure if this particular change from request.user to make_user(request)) was relevant/necessary
    user = make_user(request)
    request = error_in_path(request)
    msg = ""
    if owner_secret != queue.owner.secret:
        msg = f"This link is not valid. Please request another one from the {queue.owner.nickname}."
        msg_type = messages.ERROR
        response = HttpResponseRedirect(reverse("index"))
    else:
        request.session["queue_id"] = queue.id
        request.session["redirect_action"] = {
            "action": "edit_queue",
            "args": [queue.id],
        }
        if not user.is_authenticated and not user.is_guest:
            msg = (
                "Please sign in or create a guest account to gain access to this queue."
            )
            msg_type = messages.INFO
            response = HttpResponseRedirect(reverse("guest_sign_in"))
        else:
            msg_type = messages.SUCCESS
            response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
            # This means that there is already a guest stored in the session
            if user.is_guest:
                user.queue_id = queue.id
                request.session["guest_user"] = user.serialize()
                msg = f"Welcome back {user.nickname}."
                msg += f"{queue.owner.nickname} has given you access to {queue.title}."
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
