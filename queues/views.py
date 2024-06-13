from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import QueueForm, EntryForm
from .models import Queue, Entry
from profiles.models import make_user
from yt_query.yt_api_utils import YT

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
            # add feedback that a queue was successfully created
            return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    queue_form = QueueForm()
    context = {"queue_form": queue_form}
    return render(request, "queues/create_queue.html", context)


def publish(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    if user == queue.owner:
        msg = queue.publish()
    # add message to the request or whatever.
    # does that work with a redirect response.
    return HttpResponseRedirect(reverse("profile"))


def edit_queue(request, queue_id):
    # write authorization fucntion taking a queue and a user and returning a boolean
    queue = Queue.find_queue(queue_id)
    request.session["queue"] = queue.serialize()
    user = make_user(request)
    is_owner = queue.owner == user
    last_search = request.session.get("last_search_request","")
    if request.method == "POST":
        recent_search = request.POST.get("searchQuery", "")
        yt = YT(user)
        search_results = yt.search_videos(recent_search)
        request.session["last_search_request"] = recent_search
    elif last_search:
        recent_search = last_search
        yt = YT(user)
        search_results = yt.search_videos(last_search)
    else:
        recent_search = ""
        search_results = []
    entry_form = EntryForm()
    entries = Entry.objects.all().filter(queue=queue.id)
    context = {
        "queue": queue,
        "entry_form": entry_form,
        "entries": entries,
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
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def swap(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    queue = get_object_or_404(Queue,id=queue_id)
    query = "other_number-entry_" + str(entry.id)
    other_entry_number = request.POST[query]
    other_entry = queue.entries.filter(number=other_entry_number).first()
    entry.swap(other_entry)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def later(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    entry.later()
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def add_entry(request, queue_id, video_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    video_data = YT(user).find_video_by_id(video_id)
    # check against video_data['status'] == private, then redirect with message
    # saying it isn't available.
    del video_data["status"]
    entry = Entry(**video_data)
    entry.queue = queue
    queue.length += 1
    entry.number = queue.length
    entry.user = user.name if user.name else user.email
    queue.save()
    entry.save()
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def delete_entry(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    # add appropriate feedback messages
    if user == queue.owner:
        queue.remove_entry(entry)
    return HttpResponseRedirect(reverse("edit_queue", args=[queue_id]))


def delete_queue(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = make_user(request)
    # there should be a modal to double check on the front end
    # there should also be a message for feedback
    if queue.owner == user:
        queue.delete()
    return HttpResponseRedirect(reverse("profile"))


def gain_access(request, queue_secret, owner_secret):
    queue = get_object_or_404(Queue, secret=queue_secret)
    # I am not sure if this particular change from request.user to make_user(request)) was relevant/necessary
    user = make_user(request)
    request.session["queue_id"] = queue.id
    request.session["queue_secret"] = queue_secret
    request.session["owner_secret"] = owner_secret
    if owner_secret == queue.owner.secret:
        if user.is_authenticated:
            user.other_queues.add(queue)
            queue.save()
            user.save()
            return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
        else:
            return HttpResponseRedirect(reverse("guest_sign_in"))
    # need to add feedback here
    return HttpResponseRedirect(reverse("index"))
