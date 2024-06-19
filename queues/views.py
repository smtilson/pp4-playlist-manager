from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from errors.models import RequestReport
from .models import Queue, Entry, has_authorization
from profiles.models import make_user
from django.contrib import messages
from yt_query.yt_api_utils import YT
from urllib.error import HTTPError
from collections import defaultdict

# Create your views here.

def default():
    return 10

def debug_template(request):
    context ={}
    context["queue"]=Queue.objects.first() 
    context["is_owner"] = True
    return render(request, "queues/owner_buttons_from_scratch.html", context)

def create_queue(request):
    user = make_user(request)
    if not user.is_authenticated:
        msg = "You must be logged in to create a queue."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    if request.method == "POST":
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
        context = {"user": make_user(request)}
        response = render(request, "queues/create_queue.html", context)
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    return response


def publish(request, queue_id):
    user = make_user(request)
    queue = get_object_or_404(Queue, id=queue_id)
    if not has_authorization(user, queue) and user.is_authenticated:
        msg = "You must be logged in and be authorized in order to publish a queue."
        messages.add_message(request, messages.INFO, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    if not queue.yt_id:
        msg = "There is no channel associated with this queue. It can not be published. Please connect your account to a valid YouTube account in order to prevent this from happening in the future."
        msg_type = messages.ERROR
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    if user == queue.owner:
        try:
            msg = queue.publish()
        except HTTPError as e:
            print(e)
            print("HTTPError hit on publish")
            msg = e
        print(msg)
        messages.add_message(request, messages.SUCCESS, msg)
    else:
        msg = "Only the queue owner can publish the queue."
        messages.add_message(request, messages.ERROR, msg)
    # does that work with a redirect response.
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    return response

def edit_queue(request, queue_id):
    user = make_user(request)
    queue = get_object_or_404(Queue, id=queue_id)
    is_owner = user == queue.owner
    if not has_authorization(user, queue):
        msg = "You do not have authorization to edit this queue."
        msg_type = messages.INFO
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("account_login"))
    yt = YT(user)
    if request.method == "POST":
        recent_search = request.POST.get("searchQuery")
        if recent_search:
            search_results = yt.search_videos(recent_search)
            request = yt.save_search(request, queue_id, recent_search, search_results)
    elif request.method == "GET":
        recent_search, search_results = yt.get_last_search(request, queue_id)
    context = {
        "queue": queue,
        "recent_search": recent_search,
        "search_results": search_results,
        "user": user,
        "is_owner": is_owner,
    }
    response = render(request, "queues/edit_queue.html", context)
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
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
    print("swap hit")
    print(f"{entry_id=}")
    print(f"{other_entry_position=}")
    entry = get_object_or_404(Entry, id=entry_id)
    entry, other_entry = entry.swap_entry_positions(other_entry_position)
    msg = f"Entries in positions {entry.position} and {other_entry_position} have been swapped."
    messages.add_message(request, messages.INFO, msg)
    entry_data = {
        "id": entry.id,
        "title": entry.title,
        "position": entry.position,
        "addedBy": entry.username,
        "duration": entry.duration,
    }
    print(f"{entry.position=}")
    print(f"{other_entry.position=}")
    other_entry_data = {
        "id": other_entry.id,
        "title": other_entry.title,
        "position": other_entry.position,
        "user": other_entry.username,
        "duration": other_entry.duration,
    }
    response_dict = {
        "entry1": entry_data,
        "entry2": other_entry_data,
        "msg": msg,
        "level": "messages.INFO",
        "level2": messages.ERROR,
    }
    print("swap hit")
    print(f"{response_dict['entry1']['position']=}")
    return JsonResponse(response_dict)


def sync(request, queue_id):
    """
    Updates the corresponding YouTube playlist to match the queue.
    Args: reques (HttpRequest)
          queue_id (int)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if queue.synced:
        msg = "This queue is already synced with YouTube."
        msg_type = messages.INFO
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    else:
        if not user == queue.owner:
            msg = "You must be the owner of the queue in order to sync it with YouTube."
            msg_type = messages.ERROR
        else:
            try:
                msg = queue.sync()
                msg_type = messages.SUCCESS
            except HTTPError as e:
                msg = e
                msg_type = messages.ERROR
            print(msg)
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
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
        video_data = YT(user).find_video_by_id(video_id)
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
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    return response


def delete_entry(request, queue_id, entry_id):
    """
    Checks for authorization and then deletes an entry from a queue.
    Args: request (HttpRequest)
          queue_id (int)
          entry_id (int)
    Returns: Redirects to the "edit_queue" page of the relevant queue.
    """
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
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


def delete_queue(request, queue_id):
    """
    Checks for authorization and then deletes the queue. Deletion of playlists
    on YouTube is temporarily disabled due to API rate limits.
    Args: request (HttpRequest)
          queue_id (int)
    Returns: Redirects to the profile page.
    """
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    # there should be a modal to double check on the front end
    if queue.owner == user:
        try:
            # commented out due to rate limit issues.
            # msg = queue.unpublish()
            queue.delete()
            msg = f"{queue.title} has been deleted. If the queue was published"
            msg += " on YouTube, it will remain there. Deletion of playlists"
            msg += " on YouTube is temporarily disabled due to API rate limits."
            msg_type = messages.SUCCESS
        except HTTPError as e:
            msg = "An error occurred.\n" + e
            msg_type = messages.ERROR
        print(msg)
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("profile"))


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
    success, msg, msg_type = RequestReport.process(response)
    if not success:
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("404"))
    queue = get_object_or_404(Queue, secret=queue_secret)
    # I am not sure if this particular change from request.user to make_user(request)) was relevant/necessary
    user = make_user(request)
    request.session["queue_id"] = queue.id
    request.session["redirect_action"] = {"action": "edit_queue", "args": [queue.id]}
    if owner_secret != queue.owner.secret:
        msg = f"This link is no longer valid. Please request a new one from the {queue.owner.nickname}."
        msg_type = messages.ERROR
        messages.add_message(request, msg_type, msg)
        response = HttpResponseRedirect(reverse("account_signup"))
    elif not user.is_authenticated and not user.is_guest:
        response = HttpResponseRedirect(reverse("guest_sign_in"))
    elif user.is_authenticated:
        user.other_queues.add(queue)
        queue.save()
        user.save()
        msg = f"{queue.title} has been added to your list of queues."
    # This means that there is already a guest stored in the session
    elif user.is_guest:
        msg = f"Welcome back {user.nickname}."
    msg += f"{queue.owner.nickname} has given you access to {queue.title}."
    msg_type = messages.SUCCESS
    messages.add_message(request, msg_type, msg)
    response = HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
