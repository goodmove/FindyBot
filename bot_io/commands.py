import requests

def send_message(url, token, chat_id, text):
    url = "{0}{1}/sendMessage".format(url, token)
    payload = {"chat_id" : chat_id, "text" : text}
    response = requests.get(url , params=payload)
    if int(response.status_code) == 200:
        return True
    return False
