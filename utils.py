import ast
from django.utils.crypto import get_random_string


def json_to_dict(json) -> dict:
    return ast.literal_eval(json)


def get_secret():
    return get_random_string(20)

def format_field_name(field_name: str) -> str:
    return field_name.replace("_", " ").title()
def trigger(object):
    # this function is for debugging purposes.
    print(f"trigger function hit for {object.id} {object.getattr("name","")}{object.getattr("title","")}.")    

def empty_dict(dictionary: dict) -> bool:
    return [val for val in dictionary.values() if val] == []


def get_data_from_path(path: str) -> tuple[str]:
    parts = path.split("&")
    state = parts[0][8:]
    code = parts[1][5:]
    scope = parts[2][6:].split("%20")
    return (state, code, scope)


def get_field_names(raw_string: str) -> list[str]:
    """
    Returns list of field names from a string version of the code defining a Django model.
    """
    lines = data.split("\n")
    lines = [line.strip() for line in lines]
    print(lines)
    field_names = [line.split("= models")[0].strip() for line in lines]
    field_names = [name for name in field_names if name]
    print(field_names)


def empty_dict(dictionary: dict) -> bool:
    return [val for val in dictionary.values() if val] == []


def produce_url_code(**kwargs) -> str:
    for key, value in kwargs.items():
        if type(value) not in {int, str}:
            raise ValueError(f"{value} is not an integer or a string")
        if type(key) not in {int, str}:
            raise ValueError(f"{key} is not an integer or a string")
    data = {str(key): str(value) for key, value in kwargs.items()}
    url_code = ""
    for key, value in data.items():
        url_code += key + "=" + value + "&"
    url_code = url_code[:-1]
    return url_code




