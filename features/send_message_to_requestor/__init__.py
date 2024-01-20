from telegram.ext import Application
from . import commands

def init(app: Application):
  commands.add_handlers(app)
