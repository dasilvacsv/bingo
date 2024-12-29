import requests

url = "http://46.202.150.164:8080/message/sendText/hgghi"

payload = {
    "number": "584128264642",
    "options": {
        "delay": 6000,
        "presence": "composing",
        "linkPreview": False,
        "quoted": {"key": {
                "fromMe": True,
                "remoteJid": "58",
                "id": "1"
            }}
    },
    "textMessage": {"text": "mensaje enviado con script"}
}
headers = {
    "apikey": "mude-me",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)