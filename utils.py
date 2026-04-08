import ast
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import reverse

from typing import Callable, Optional, Union, Literal, TYPE_CHECKING
from functools import wraps
from errors.views import error_handler


if TYPE_CHECKING:
    from profiles.models import Profile

def json_to_dict(json) -> dict:
    """
    Convert a JSON string to a Python dictionary.
    Args: json (str)
    Returns: dict
    """
    return ast.literal_eval(json)


def get_secret():
    """
    Generates a random secret string of length 20 using random modulepyt.
    Returns: str
    """
    return get_random_string(20)


def trigger(object):
    """
    This function is used for debugging purposes. It prints a message
    indicating that the trigger function has been hit for a specific object.
    Args: object
    Returns: None
    """
    print(
        f"trigger function hit for {object.id}"
        f"{object.getattr('name', '')}{object.getattr('title', '')}."
    )


def get_data_from_path(path: str) -> tuple[str]:
    """
    Extracts data from a given path string in the format of
    "state=...&code=...&scope=...".
    Args: path (str)
    Returns: tuple[str]
    """
    parts = path.split("&")
    state = parts[0][8:]
    code = parts[1][5:]
    scope = parts[2][6:].split("%20")
    return (state, code, scope)


def check_valid_redirect_action(request) -> bool:
    """
    Check if the redirect action in the session is valid. Currently only one
    redirect action is implemented.
    Args: request (HttpRequest)
    Returns: bool
    """
    # Currently only one redirect action is implemented
    return request.session.get("redirect_action") == "edit_queue"


def abbreviate(string: str, cutoff: int) -> str:
    """
    Abbreviates a given string to a specified length.
    Args: string (str)
          cutoff (int)
    Returns: str
    """
    if len(string) > cutoff:
        return string[:cutoff] + "..."
    return string




def check_auth(
    request, msg: str
) -> Union[tuple['Profile', Literal[True], None], tuple[None, Literal[False], HttpResponseRedirect]]:
    """
    Check if the user has valid credentials.
    Args: user (User)
    Returns: bool
    """
    user = request.user
    # redirects if user is not authenticated
    if not getattr(user, "is_authenticated", False):
        messages.info(request, msg)
        response = HttpResponseRedirect(reverse("account_login"))
        return None, False, response
    return user, True, None



def require_auth(msg: str):
    """
    Decorator factory that:
    1) runs check_auth(request, msg)
    2) short-circuits with redirect if not authenticated
    3) injects auth_user into wrapped view via kwargs
    """
    def decorator(view_func: Callable[..., HttpResponse]) -> Callable[..., Optional[HttpResponse]]:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs) -> Optional[HttpResponse]:
            user, auth_status, redirect_response = check_auth(request, msg)
            if not auth_status:
                # Keep same behavior as your current views
                return redirect_response 

            # Pass user into wrapped view
            kwargs["auth_user"] = user
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator

def with_error_handling(view_func: Callable[..., Optional[HttpResponse]]) -> Callable[..., Optional[HttpResponse]]:
    """
    Decorator that wraps a view function with error handling logic.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs) -> Optional[HttpResponse]:
        response = view_func(request, *args, **kwargs)
        return error_handler(request, response)
    return wrapper
