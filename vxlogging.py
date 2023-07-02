IS_DEBUG = False

def info(message):
    message = str(message)
    print(f" > [ I ] {message}")

def success(message):
    message = str(message)
    print(f" > [ ✔ ] {message}")

def error(message):
    message = str(message)
    print(f" > [ ✘ ] {message}")

def warn(message):
    message = str(message)
    print(f" > [ ! ] {message}")

def debug(message):
    if IS_DEBUG:
        message = str(message)
        print(f" > [ D ] {message}")