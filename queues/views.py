from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .forms import QueueForm, EntryForm
from .models import Queue, Entry
from profiles.models import Profile

# Create your views here.


def create_queue(request):
    if request.method == "POST":
        queue_form = QueueForm(data=request.POST)
        if queue_form.is_valid():
            queue = queue_form.save(commit=False)
            queue.owner = Profile.get_user_profile(request)
            queue.save()
            # add feedback that a queue was successfully created
    queue_form = QueueForm()
    context = {"queue_form": queue_form}
    return render(request, "queues/create_queue.html", context)


def edit_queue(request, queue_id):
    queue = Queue.find_queue(queue_id)
    if request.method == "POST":
        entry_form = EntryForm(data=request.POST)
        if entry_form.is_valid():
            entry = entry_form.save(commit=False)
            entry.queue = queue
            queue.length += 1
            entry.number = queue.length
            queue.save()
            entry.save()
    entry_form = EntryForm()
    entries = Entry.objects.all().filter(queue=queue.id)
    context = {"entry_form": entry_form, "entries": entries}
    return render(request, "queues/edit_queue.html", context)
