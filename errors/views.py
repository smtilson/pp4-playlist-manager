from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import reverse
from django.contrib import messages
from .utils import process_response


def error_handler(request, response):
    status, msg, msg_type = process_response(response)
    status = str(status)[0]
    if status in {'2', '3'}:
        return response
    elif status == '4':
        messages.add_message(request, msg_type, msg)
        return HttpResponse(status=404)
    else:
        messages.add_message(request, msg_type, msg)
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("profile"))
    else:
        return HttpResponseRedirect(reverse("index"))
