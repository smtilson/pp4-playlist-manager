from django.shortcuts import render, reverse, get_object_or_404
from django.http import HttpResponseRedirect
from .forms import QueueForm, EntryForm
from .models import Queue, Entry
from yt_query.yt_api_utils import YT

# Create your views here.


def create_queue(request):
    if request.method == "POST":
        queue_form = QueueForm(data=request.POST)
        if queue_form.is_valid():
            queue = queue_form.save(commit=False)
            owner =  request.user
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
    user = request.user
    if user == queue.owner:
        msg = queue.publish()
    # add message to the request or whatever.
    # does that work with a redirect response.
    return HttpResponseRedirect(reverse("profile"))

def edit_queue(request, queue_id):
    # write authorization fucntion taking a queue and a user and returning a boolean
    queue = Queue.find_queue(queue_id)
    request.session['queue'] = queue.serialize()
    user = request.user
    recent_search = request.POST.get("searchQuery", "")
    search_results = []
    is_owner = queue.owner == user
    if recent_search:
        yt = YT(user)
        search_results = yt.search_videos(recent_search)
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
        "is_guest": user.is_guest
    }
    return render(request, "queues/edit_queue.html", context)

def add_entry(request, queue_id, video_id):
    queue = get_object_or_404(Queue,id=queue_id)
    user = request.user
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
    user = request.user
    # add appropriate feedback messages
    if user == queue.owner:
        entry.delete()
    return HttpResponseRedirect(reverse('edit_queue', args=[queue_id]))

def delete_queue(request, queue_id):
    queue = get_object_or_404(Queue, id=queue_id)
    user = request.user
    #there should be a modal to double check on the front end
    # there should also be a message for feedback
    if queue.owner == user:
        queue.delete()
    return HttpResponseRedirect(reverse("profile"))

def gain_access(request, queue_secret, owner_secret):
    queue = get_object_or_404(Queue,secret=queue_secret)
    user = request.user
    request.session['queue_id'] = queue.id
    request.session['queue_secret'] = queue_secret
    request.session['owner_secret'] = owner_secret
    if owner_secret == queue.owner.secret:
        if user.is_authenticated:
            user.other_queues.add(queue)
            queue.save()
            user.save()
            return HttpResponseRedirect(reverse("edit_queue",args=[queue.id]))
        else:
            return HttpResponseRedirect(reverse('guest_sign_in'))
    # need to add feedback here
    return HttpResponseRedirect(reverse('index'))

