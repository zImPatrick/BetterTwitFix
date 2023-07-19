IS_DEBUG = False
from flask import  request
def generic(message):
    invocation_id = None
    try:
        if 'serverless.context' in request.environ:
            invocation_id = request.environ['serverless.context'].aws_request_id
    except:
        pass
    if invocation_id is None:
        invocation_id = ""
    else:
        invocation_id = str(invocation_id)+" "
    message = str(f"{invocation_id}{message}")
    print(message)

def info(message):
    message = str(message)
    generic(f" > [ I ] {message}")

def success(message):
    message = str(message)
    generic(f" > [ ✔ ] {message}")

def error(message):
    message = str(message)
    generic(f" > [ ✘ ] {message}")

def warn(message):
    message = str(message)
    generic(f" > [ ! ] {message}")

def debug(message):
    if IS_DEBUG:
        message = str(message)
        generic(f" > [ D ] {message}")