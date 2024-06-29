import ast
from django.utils.crypto import get_random_string


def json_to_dict(json) -> dict:
    """
    Convert a JSON string to a Python dictionary.
    Args: json (str)
    Returns: dict
    """
    return ast.literal_eval(json)


def get_secret():
    """
    Generates a random secret string of length 20 using.
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
    print(f"trigger function hit for {object.id}"
          f"{object.getattr("name", "")}{object.getattr("title", "")}.")


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
        return string[:cutoff]+"..."
    return string
