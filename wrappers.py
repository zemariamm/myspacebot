from google.appengine.ext import db 
from model import *

def require_user(f):
    def load_or_die(obj,message=None):
        user = User.search_by_name(message.sender)
        if user:
            obj.user = user
            return f(obj,message)
        else:
            message.reply("You have to register first!!")
    return load_or_die

def require_link(f):
    def check_link(obj,message=None):
        content = message.arg
        if not content:
            message.reply("That link is not valid!!")
        else:
            obj.content = content
            return f(obj,message)
    return check_link

def require_valid_number(f):
    def check_number(obj,message=None):
        content = message.arg
        if not content:
            message.reply("That number is not valid!!")
        else:
            try:
                index = int(content)
                index = index - 1
                obj.index = index
                return f(obj,message)
            except Exception:
                message.reply("That number is not valid!!")
    return check_number            
