from telegram.ext import Application
from . import callbacks

def init(app: Application):
  callbacks.add_handlers(app)
