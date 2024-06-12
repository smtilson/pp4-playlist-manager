from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import QueueForm, EntryForm
from .models import Queue, Entry
from profiles.models import Profile
from yt_query.yt_api_utils import YT
from utils import produce_url_code

# Create your views here.


def create_queue(request):
    if request.method == "POST":
        queue_form = QueueForm(data=request.POST)
        if queue_form.is_valid():
            queue = queue_form.save(commit=False)
            owner =  Profile.get_user_profile(request)
            queue.owner = owner
            queue.owner_yt_id = owner.youtube_id
            queue.save()
            # add feedback that a queue was successfully created
            return HttpResponseRedirect(reverse("edit_queue", args=[queue.id]))
    queue_form = QueueForm()
    context = {"queue_form": queue_form}
    return render(request, "queues/create_queue.html", context)


def publish(request, queue_id):
    queue = get_object_or_404(Queue,id=queue_id)
    user = Profile.get_user_profile(request)
    if user == queue.owner:
        msg = queue.publish()
    # add message to the request or whatever.
    # does that work with a redirect response.
    return HttpResponseRedirect(reverse("profile"))

def edit_queue(request, queue_id):
    queue = Queue.find_queue(queue_id)
    user = Profile.get_user_profile(request)
    recent_search = request.POST.get("searchQuery", "")
    search_results = []
    is_owner = queue.owner == user
    if recent_search:
        yt = YT(user)
        search_results = yt.search_videos(recent_search)
    if request.method == "POST":
        entry_form = EntryForm(data=request.POST)
        if entry_form.is_valid():

            pass
    entry_form = EntryForm()
    entries = Entry.objects.all().filter(queue=queue.id)
    context = {
        "queue":queue,
        "entry_form": entry_form,
        "entries": entries,
        "recent_search": recent_search,
        "search_results": search_results,
        "user":user,
        "is_owner": is_owner,
    }
    return render(request, "queues/edit_queue.html", context)

def add_entry(request, queue_id, video_id):
    queue = get_object_or_404(Queue,id=queue_id)
    user = Profile.get_user_profile(request)
    video_data = YT(user).find_video_by_id(video_id)
    # check against video_data['status'] == private, then redirect with message
    # saying it isn't available.
    del video_data['status']
    entry = Entry(**video_data)
    entry.queue=queue
    queue.length += 1
    entry.number = queue.length

    entry.user=user
    queue.save()
    entry.save()
    return HttpResponseRedirect(reverse('edit_queue', args=[queue_id]))

def delete_entry(request, queue_id, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    queue = get_object_or_404(Queue, id=queue_id)
    user = Profile.get_user_profile(request)
    # add appropriate feedback messages
    if user == queue.owner:
        entry.delete()
    return HttpResponseRedirect(reverse('edit_queue', args=[queue_id]))

def delete_queue(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = Profile.get_user_profile(request)
    #there should be a modal to double check on the front end
    # there should also be a message for feedback
    if queue.owner == user:
        queue.delete()
    return HttpResponseRedirect(reverse("profile"))

