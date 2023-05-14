import json
import hashlib


with open("settings.json", "r") as f:
    settings = json.load(f)

passw = input("enter password for deleting torrents\n")

settings["PASS_HASH"] = hashlib.sha256(passw.encode()).hexdigest()


with open("settings.json", "w") as f:
    json.dump(settings, f, indent=4)