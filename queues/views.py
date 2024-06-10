from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .forms import QueueForm
from profiles.models import Profile

# Create your views here.

def create_queue(request):
    if request.method == "POST":
        queue_form = QueueForm(data=request.POST)
        if queue_form.is_valid():
            queue = queue_form.save(commit=False)
            queue.owner = Profile.get_user_profile(request)
            queue.save()
            #add feedback that a queue was successfully created
    queue_form = QueueForm()
    context = {"queue_form":queue_form}
    return render(request, "queues/create_queue.html", context)
    