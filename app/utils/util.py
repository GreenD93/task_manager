import json

def get_json_value(jsonData, key, default_value):
    result = default_value

    if key in jsonData:
        result = jsonData[key]

    if result is None:
        result = default_value

    return result

def file_to_json(path):
    result = {}
    with open(path) as data_file:
        result = json.load(data_file)
    return result