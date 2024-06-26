from django.shortcuts import render
from profiles.models import make_user
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import reverse
from django.contrib import messages
from .models import RequestReport
from .utils import process_path

# Create your views here.

def error_handler(request, response):
    user = make_user(request)
    status, msg, msg_type = RequestReport.process(response)
    status = str(status)[0]
    if status in {'2', '3'}:
        return response
    elif status == '4':
        messages.add_message(request, msg_type, msg)
        return HttpResponse(status=404)
    else:
        messages.add_message(request, msg_type, msg)
    if user.is_authenticated:
        return HttpResponseRedirect(reverse("profile"))
    else:
        return HttpResponseRedirect(reverse("index"))
    