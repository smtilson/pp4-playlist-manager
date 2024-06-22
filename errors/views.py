from django.shortcuts import render
from profiles.models import make_user
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.contrib import messages
from .models import RequestReport

# Create your views here.

def error_handler(request, response):
    user = make_user(request)
    status, msg, msg_type = RequestReport.process(response)
    if status in {200, 302}:
        return response
    elif status == 404:
        messages.add_message(request, msg_type, msg)
        return render(request, "404.html")
    elif status not in {200, 302}:
        messages.add_message(request, msg_type, msg)
    if user.is_authenticated:
        return HttpResponseRedirect(reverse("profile"))
    else:
        return HttpResponseRedirect(reverse("index"))