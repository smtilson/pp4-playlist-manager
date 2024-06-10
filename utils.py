import json
import ast


def json_to_dict(json) -> dict:
    return ast.literal_eval(json)


def empty_dict(dictionary:dict) -> bool:
    return [val for val in dictionary.values() if val]==[]


def get_data_from_path(path:str) -> tuple[str]:
    parts = path.split('&')
    state = parts[0][8:]
    code = parts[1][5:]
    scope = parts[2][6:].split('%20')
    return (state,code,scope)


def get_field_names(raw_string:str) -> list[str]:
    """
    Returns list of field names from a string version of the code defining a Django model.
    """
    lines = data.split("\n")
    lines = [line.strip() for line in lines]
    print(lines)
    field_names = [line.split("= models")[0].strip() for line in lines]
    field_names = [name for name in field_names if name]
    print(field_names)


def empty_dict(dictionary:dict) -> bool:
    return [val for val in dictionary.values() if val]==[]



    