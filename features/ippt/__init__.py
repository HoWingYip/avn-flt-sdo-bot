from telegram.ext import Application
from . import conversation

def init(app: Application):
  conversation.add_handlers(app)
