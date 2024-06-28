# Utility functions for error processing
from django.contrib import messages


def process_path(path: str) -> str:
    if "error" not in path:
        return "There is no error in the path."
    error, _ = path.split("&")
    error_msg = error.split("=")[1]
    error_msg = ERROR_DICTIONARY.get(
        error_msg, f"The unknown error {error_msg} has occurred."
    )
    return error_msg



ERROR_DICTIONARY = {
    "access_denied": "In order to utilize the app fully, you will need to give it write permissions for a YouTube account."
}

def process_response(response):
    status_code = response.status_code
    if status_code == 404:
        msg = "The page you requested does not exist."
        msg_type = messages.ERROR
    elif status_code not in {200, 302}:
        msg = "An unknown error seems to have occurred."
        msg_type = messages.ERROR
    elif status_code == 302:
        msg = 'You have been redirected.'
        msg_type = messages.INFO
    else:
        msg = 'Everything proceeded normally.'
        msg_type = messages.SUCCESS
    return status_code, msg, msg_type