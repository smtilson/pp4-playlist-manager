# This is for error processing

from django.http import HttpResponse, HttpRequest
from urllib.error import HTTPError


def process_path(path:str) -> str:
    if "error" not in path:
        return "There is no error in the path"
    address = path.split(' ')[1]
    error, _ = address.split('&')
    error_msg = error.split('=')[1]
    return error_msg
    
    pass