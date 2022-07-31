import json

with open("dictionary.json", "r") as file:
    data = json.load(file)

sorted = {word: 0 for word in data if len(word) == 5}

with open("../dictSorted.json", "w") as file:
    file.write(json.dumps(sorted))