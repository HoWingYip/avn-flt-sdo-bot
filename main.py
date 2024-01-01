import logging
import os
from inspect import cleandoc
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler

from bcp import add_bcp_handlers

from constants import HELP_MESSAGE

logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    f"Good day! This is the AVN FLT SDO bot. How may I help you?\n\n{HELP_MESSAGE}"
  )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(HELP_MESSAGE)

if __name__ == "__main__":
  application = ApplicationBuilder() \
    .token(os.environ["BOT_TOKEN"]) \
    .build()
  
  start_handler = CommandHandler("start", start)
  application.add_handler(start_handler)

  help_handler = CommandHandler("help", help)
  application.add_handler(help_handler)

  add_bcp_handlers(application)
  
  application.run_polling()
