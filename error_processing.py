# This is for error processing

from django.http import HttpResponse, HttpRequest
from urllib.error import HTTPError


def process_path(path:str) -> str:
    if "error" not in path:
        return "There is no error in the path"
    error, _ = path.split('&')
    error_msg = error.split('=')[1]
    error_msg = ERROR_DICTIONARY[error_msg]
    return error_msg
    
ERROR_DICTIONARY = {"access_denied":"In order to utilize the app fully, you will need to give it write permissions for a youtube account."}