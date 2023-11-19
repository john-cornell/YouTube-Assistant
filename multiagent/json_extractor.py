import json

def extract_json(text, output_key):
    if '{' not in text:
        return get_error_json("No { character found, unable to proces as JSON", output_key=output_key)

    start_idx = text.index('{')
    try:
        data = json.loads(text[start_idx:])
        return json.dumps(data)
    except json.JSONDecodeError:
        return get_error_json(f"Unable to decode JSON from {text}", output_key=output_key)

def get_error_json(error, output_key):
    error_json = {"thinking": "error_occured", "process": error}
    return json.dumps(error_json)