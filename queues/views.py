from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from .forms import QueueForm
from .models import Queue, Entry
from profiles.models import make_user
from django.contrib import messages
from yt_query.yt_api_utils import YT
from urllib.error import HTTPError

# Create your views here.


def create_queue(request):
    if request.method == "POST":
        queue_form = QueueForm(data=request.POST)
        if queue_form.is_valid():
            queue = queue_form.save(commit=False)
            owner = make_user(request)
            queue.owner = owner
            queue.owner_yt_id = owner.youtube_id
            queue.save()
            msg = f"{queue.title} has been created."
            messages.add_message(request, messages.SUCCESS, msg)
            # add feedback that a queue was successfully created
            return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    queue_form = QueueForm()
    context = {"queue_form": queue_form}
    return render(request, "queues/create_queue.html", context)


def publish(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
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
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def edit_queue(request, queue_id):
    # write authorization fucntion taking a queue and a user and returning a boolean
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    is_owner = queue.owner_yt_id == user.youtube_id
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
        "is_guest": user.is_guest,
    }
    return render(request, "queues/edit_queue.html", context)


def earlier(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    entry.earlier()
    msg = f"{entry.title} has been moved earlier in the queue."
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def swap(request, queue_id, entry_id):
    # refactor to use a class method
    entry = get_object_or_404(Entry, id=entry_id)
    # I don't think this is necessary here.
    queue = get_object_or_404(Queue, id=queue_id)
    query = "other_position-entry_" + str(entry.id)
    other_entry_position = int(request.POST[query])
    other_entry = queue.all_entries[other_entry_position - 1]
    Entry.swap_entries(entry_id, other_entry.id)
    msg = f"{entry.title} and {other_entry.title} have been swapped in the queue."
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def swap_js(request, queue_id, entry_id, other_entry_position):
    entry = get_object_or_404(Entry, id=entry_id)
    entry, other_entry = entry.swap_entry_positions(other_entry_position)
    msg = f"Entries in positions {entry.position} and {other_entry_position} have been swapped."
    messages.add_message(request, messages.INFO, msg)
    entry_data = {
        "id": entry.id,
        "title": entry.title,
        "position": entry.position,
        "addedBy": entry.user,
        "duration": entry.duration,
    }
    other_entry_data = {
        "id": other_entry.id,
        "title": other_entry.title,
        "position": other_entry.position,
        "user": other_entry.user,
        "duration": other_entry.duration,
    }
    response_dict = {
        "entry1": entry_data,
        "entry2": other_entry_data,
        "msg": msg,
        "level": "messages.INFO",
        "level2": messages.ERROR,
    }
    return JsonResponse(response_dict)


def later(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    entry.later()
    msg = f"{entry.title} has been moved later in the queue."
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def sync(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if user == queue.owner:
        try:
            msg = queue.sync()
            msg_type = messages.SUCCESS
        except HTTPError as e:
            msg = e
            msg_type = messages.ERROR
        print(msg)
    else:
        msg = "Only the queue owner can sync the queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def add_entry(request, queue_id, video_id):
    queue = get_object_or_404(Queue, id=queue_id)
    if queue.full:
        msg = "This queue is at max capacity. Remove some tracks if you would like to add more."
        msg_type = messages.ERROR
        messages.add_message(request, msg_type, msg)
        HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    user = make_user(request)
    video_data = YT(user).find_video_by_id(video_id)
    if video_data["status"] == "private":
        msg = "This video is private. It cannot be added to the queue."
        messages.add_message(request, messages.ERROR, msg)
        HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))
    del video_data["status"]
    entry = Entry(**video_data)
    entry.p_queue = queue
    # adds entry to end of list
    entry._position = queue.length
    entry.user = user.name if user.name else user.email
    queue.save()
    entry.save()
    request.session["queue"] = queue.serialize()
    msg = f"{entry.title} has been added to the queue."
    messages.add_message(request, messages.SUCCESS, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def delete_entry(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    # add appropriate feedback messages
    if user == queue.owner:
        queue.remove_entry(entry)
        msg = f"{entry.title} has been removed from the queue."
        msg_type = messages.SUCCESS
    else:
        msg = "You do not have permission to delete this entry."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def delete_queue(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    # there should be a modal to double check on the front end
    if queue.owner == user:
        try:
            # commented out due to rate limit issues.
            # msg = queue.unpublish()
            queue.delete()
            msg = (
                f"{queue.title} has been deleted. If the queue was published"
                "on YouTube, it will remain there. Deletion of playlists on YouTube"
                "is temporarily disabled due to API rate limits."
            )
            msg_type = messages.SUCCESS
        except HTTPError as e:
            msg = "An error occurred.\n" + e
            msg_type = messages.ERROR
        print(msg)
    else:
        msg = "You do not have permission to delete this queue."
        msg_type = messages.ERROR
    messages.add_message(request, msg_type, msg)
    return HttpResponseRedirect(reverse("profile"))


def gain_access(request, queue_secret, owner_secret):
    queue = get_object_or_404(Queue, secret=queue_secret)
    # I am not sure if this particular change from request.user to make_user(request)) was relevant/necessary
    user = make_user(request)
    request.session["queue_id"] = queue.id
    request.session["queue_secret"] = queue_secret
    request.session["owner_secret"] = owner_secret
    request.session["redirect_action"] = {"action": "edit_queue", "args": [queue.id]}
    if owner_secret == queue.owner.secret:
        print("secrets match")
        if user.is_authenticated:
            print("user is authenticated")
            user.other_queues.add(queue)
            queue.save()
            user.save()
            return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
        # This means that there is already a guest stored in the session
        elif user.is_guest:
            print("user is a guest")
            return HttpResponseRedirect(reverse("guest_sign_in"))
        # need to add feedback here
        # this is hit if the user is still anonymous and not a guest
        else:
            print("user is an unathenticated non guest")
            return HttpResponseRedirect(reverse("guest_sign_in"))
