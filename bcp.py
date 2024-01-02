from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from datetime import datetime

from constants import bcp_states

async def bcp(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"] = {}

  await update.message.reply_text(
    "You are now starting a Base Command Post (BCP) clearance request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return bcp_states.RANK_NAME

async def bcp_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["rank_name"] = update.message.text

  await update.message.reply_text(
    f"Rank/name is {update.message.text}.\n" # TODO: remove after deployment
    "When will your BCP clearance start? (E.g. 010125 1200H)"
  )

  return bcp_states.DATE_TIME

async def bcp_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # TODO: use validate_datetime_string
  try:
    # # ensures message is 2 strings separated by a space
    # bcp_date, bcp_time = update.message.text.split(" ")

    # assert len(bcp_date) == 6 and bcp_date.isdecimal()
    # day, month, year = int(bcp_date[:2]), int(bcp_date[2:4]), 2000 + int(bcp_date[4:])
    
    # assert len(bcp_time) == 5 and bcp_time.endswith("H") and bcp_time[:-1].isdecimal()
    # bcp_time = bcp_time[:-1]

    # hour, minute = int(bcp_time[:2]), int(bcp_time[2:])
    
    # below line will raise exception if date is invalid
    # if datetime.now() > datetime(day=day, month=month, year=year, hour=hour, minute=minute):
    #   raise ValueError

    if datetime.now() > datetime.strptime(update.message.text, "%d%m%y %H%MH"):
      raise ValueError
  except:
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return bcp_states.DATE_TIME
  
  bcp_date, bcp_time = update.message.text.split(" ")
  bcp_time = bcp_time[:-1]

  context.user_data["bcp"]["date"] = bcp_date
  context.user_data["bcp"]["time"] = bcp_time

  await update.message.reply_text(
    f"Date is {bcp_date}, time is {bcp_time}.\n" # TODO: remove after deployment
    "What is the purpose of your BCP clearance request?"
  )

  return bcp_states.PURPOSE

async def bcp_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["purpose"] = update.message.text

  await update.message.reply_text(
    f"BCP purpose is {update.message.text}.\n" # TODO: remove after deployment
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )

  return bcp_states.ADDITIONAL_INFO

async def bcp_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["additional_info"] = update.message.text

  bcp_fields = context.user_data["bcp"]
  await update.message.reply_text(
    "BCP clearance request complete.\n"
    f"Rank/name: {bcp_fields['rank_name']}\n"
    f"Clearance date and time: {bcp_fields['date']} {bcp_fields['time']}H\n"
    f"Purpose: {bcp_fields['purpose']}\n"
    f"Additional info: {bcp_fields['additional_info']}"
  )
  
  return ConversationHandler.END

async def bcp_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # not necessary to delete context.user_data["bcp"]
  # because it will only be read after all fields are filled out
  await update.message.reply_text(
    "BCP clearance request cancelled.\n"
    "Send /help for a list of commands."
  )
  return ConversationHandler.END

def add_bcp_handlers(application: Application):
  bcp_handler = ConversationHandler(
    entry_points=[CommandHandler("bcp", bcp)],
    states={
      bcp_states.RANK_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_rank_name)],
      bcp_states.DATE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_date_time)],
      bcp_states.PURPOSE: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_purpose)],
      bcp_states.ADDITIONAL_INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_additional_info)]
    },
    fallbacks=[CommandHandler("cancel", bcp_cancel)],
  )
  application.add_handler(bcp_handler)
