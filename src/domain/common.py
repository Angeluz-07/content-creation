import json


def read_json(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        result = json.load(file)
    return result

def save_json(data, output_path: str):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
