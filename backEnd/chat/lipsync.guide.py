import os
import requests
import json
from voicetotextalt import VTT

GOOEY_API_KEY = "sk-tAufDXcTCURSxuCc0vwmhP9nOZUhLTsOpvsSBnfobOq7eEQP"

text = VTT()
print("Now Speak")
userText = text.speak()

files = [
    ("input_face", open("fakeface.jpg", "rb")),
    ("text_prompt", userText),
]
payload = {}

response = requests.post(
    "https://api.gooey.ai/v2/Lipsync/form/?run_id=fecsii61rs6e&uid=fm165fOmucZlpa5YHupPBdcvDR02",
    headers={
        "Authorization": "Bearer " + GOOEY_API_KEY,
    },
    files=files,
    data={"json": json.dumps(payload)},
)
assert response.ok, response.content

result = response.json()
print(response.status_code, result)
