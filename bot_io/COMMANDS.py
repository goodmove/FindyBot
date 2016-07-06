import requests

def send_message(url, token, chat_id, text):
    method_name = "/sendMessage"
    response = requests.get(url + token + method_name, {"chat_id" : chat_id, "text" : text})
    if int(response.status_code) == 200:
        print("success")
        return True
    return False