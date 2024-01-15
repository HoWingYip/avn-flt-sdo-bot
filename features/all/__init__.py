from telegram.ext import Application

from . import callbacks
from .complete_request import complete_request

def init(app: Application):
  callbacks.add_handlers(app)
