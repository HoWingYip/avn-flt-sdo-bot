import logging
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from user.bcp import add_bcp_handlers
from user.rso import add_rso_handlers

from utility.constants import HELP_MESSAGE

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
  with open("bot_config.json") as bot_config_file:
    bot_config = json.load(bot_config_file)

  application = ApplicationBuilder().token(bot_config["bot_token"]).build()
  
  # user-facing handlers
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("help", help))
  add_bcp_handlers(application)
  add_rso_handlers(application)

  # SDO-facing handlers
  
  
  application.run_polling()
