import json

def token_print():
    file_path = "auth.json"

    # Read and parse the JSON file
    with open(file_path, "r") as file:
        data = json.load(file)

    # Display the JSON data
    return json.dumps(data)
