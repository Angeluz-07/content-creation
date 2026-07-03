import json


def read_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        result = json.load(file)
    return result
