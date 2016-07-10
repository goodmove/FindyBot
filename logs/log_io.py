import time

def log_requests(log_file, type, user, chat, msg):
    log_file.write("*"*15 + "\n")
    log_file.write(time.strftime("Timestamp: %d-%m-%Y %H:%M:%S\n"))
    log_file.write("Type: {0}\n".format(type))
    if user.id:
        log_file.write(str(user) + "\n")
    else:
        log_file.write("\\No user info\\" + "\n")
    if msg.text:
        log_file.write(u"Message: {0}\n\n".format(msg.text.encode("utf_8")))
    else:
        log_file.write(u"Message: {0}\n\n".format("\\No text provided\\".encode("utf_8")))
