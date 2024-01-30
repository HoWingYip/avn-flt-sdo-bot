import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

import features
from internal.track_chats import track_chats
from utility.constants import HELP_MESSAGE

logging.basicConfig(
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "Good day! This is the AVN FLT SDO bot.\n"
    "The purpose of this bot is to handle requests from trainees in AVN FLT, "
    "and assist the SDO with completing tasks more efficiently.\n"
    "This bot is currently in its first trial phase, which will last from 22/1 to 26/1. "
    "We seek your understanding as we work to resolve possible teething issues. Thank you!\n\n" +
    HELP_MESSAGE
  )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(HELP_MESSAGE)

if __name__ == "__main__":
  with open("bot_config.json") as bot_config_file:
    bot_config = json.load(bot_config_file)

  app = ApplicationBuilder().token(bot_config["bot_token"]).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("help", help))

  features.shared.init(app)
  features.bcp.init(app)
  features.report_sick.init(app)
  features.mc.init(app)
  features.ippt.init(app)
  features.sdo.init(app)
  features.enquiry.init(app)
  features.send_message_to_requestor.init(app)

  # internal stuff
  track_chats(app)

  app.run_polling()
