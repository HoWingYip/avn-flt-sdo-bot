from telegram.ext import Application
from . import conversation, callbacks

def init(app: Application):
  conversation.add_handlers(app)
  callbacks.add_handlers(app)
