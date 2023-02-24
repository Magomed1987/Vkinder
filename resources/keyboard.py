import json

def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": text
        },
        "color": color
    }

keyboard = {
    "one_time": False,
    "buttons": [
        [get_button('Начать поиск', 'primary')],
        [get_button('Вперёд', 'secondary')],
    ]
}

keyboard = str(json.dumps(keyboard, ensure_ascii=False).encode('utf-8').decode("utf-8"))