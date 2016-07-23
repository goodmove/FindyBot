class Message(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.user = User(data.get("from", {}))
        self.chat = Chat(data.get("chat", {}))
        self.text = data.get("text")
        self.photo_sizes = [Photo(x) for x in data.get("photo", {})]
        # self.type = data.get("entities")

    def __repr__(self):
        return "<Message> " + str({"id" : self.id, "usr_id" : self.usr_id, "chat_id" : self.chat_id, "text" : self.text, "type" : self.type})
        
class EditedMessage(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.user = User(data.get("from", {}))
        self.chat = Chat(data.get("chat", {}))
        self.text = data.get("text")
        # self.type = data.get("entities")

    def __repr__(self):
        return "<Message> " + str({"id" : self.id, "usr_id" : self.usr_id, "chat_id" : self.chat_id, "text" : self.text, "type" : self.type})

class User(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")

    def __repr__(self):
        return "<User> " + str((self.id, self.first_name, self.last_name))

class Chat(object):
    def __init__(self, data):
        self.id = data.get("id")
        self.first_name = data.get("first_name")
        self.last_name = data.get("last_name")
        self.type = data.get("type")

    def __repr__(self):
        return "<Chat> " + str({"id" : self.id, "type" : self.type})

class Photo(object):
    def __init__(self, data):
        self.id = data.get("file_id")
        self.width = data.get("width")
        self.height = data.get("height")
        self.file_size = data.get("file_size")

class Update(object):
    types = ['message', 'edited_message', 'inline_query', 'chosen_inline_result', 'callback_query']
    def __init__(self, update_id, data):
        # Required
        self.update_id = int(update_id)
        self.type = [t for t in self.types if data.get(t)][0]
        # Optionals
        self.message = Message(data.get('message')) if data.get('message') else None
        self.edited_message = EditedMessage(data.get('edited_message')) if data.get('edited_message') else None
        # self.inline_query = data.get('inline_query')
        # self.chosen_inline_result = data.get('chosen_inline_result')
        # self.callback_query = data.get('callback_query')
