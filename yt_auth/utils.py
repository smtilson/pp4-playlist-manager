
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


    