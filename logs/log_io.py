import time

def log_requests(log_file, user, chat, msg):
    log_file.write("*"*15 + "\n")
    log_file.write(time.strftime("Timestamp: %d-%m-%Y %H:%M:%S\n"))
    log_file.write(str(user) + "\n")
    log_file.write("Message: " + msg.text + "\n\n")