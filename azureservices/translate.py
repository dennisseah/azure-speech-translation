import requests, uuid, json, os

key = os.environ["AZURE_TRANSLATOR_KEY"]
location = os.environ["AZURE_TRANSLATOR_LOC"]
endpoint = "https://api.cognitive.microsofttranslator.com"
constructed_url = f"{endpoint}/translate"


def translate(text: str, lang_fr: str, lang_to: str):
    params = {"api-version": "3.0", "from": lang_fr, "to": [lang_to]}
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": location,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    return response[0]["translations"][0]["text"]
