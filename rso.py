from telegram import Update
from telegram.ext import filters, Application, ConversationHandler, CommandHandler, MessageHandler, ContextTypes
from datetime import datetime

from constants import rso_states
from utility.validate_datetime_string import validate_datetime_string

async def rso(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"] = {}

  await update.message.reply_text(
    "You are now starting a Report Sick Outside (RSO) request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return rso_states.RANK_NAME

async def rso_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["rank_name"] = update.message.text

  await update.message.reply_text(
    f"Rank/name is {update.message.text}.\n" # TODO: remove after deployment
    "Where will you RSO? (E.g. Ang Mo Kio Polyclinic)"
  )

  return rso_states.LOCATION

async def rso_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["location"] = update.message.text,

  await update.message.reply_text(
    f"RSO location is {update.message.text}.\n"
    "When will you RSO? (E.g. 010125 0800H)\n"
    # TODO: tell user about RSO timing rules
    # (e.g. can't request to RSO more than 24h in the future)
  )

  return rso_states.DATE_TIME

async def rso_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    if datetime.now() > datetime.strptime(update.message.text, "%d%m%y %H%MH"):
      raise ValueError
  except:
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return rso_states.DATE_TIME
  
  context.user_data["rso"]["date"], context.user_data["rso"]["time"] = \
    validate_datetime_string(update.message.text)
  
  await update.message.reply_text(
    f"Date is {context.user_data['rso']['date']}, time is {context.user_data['rso']['time']}.\n" # TODO: remove after deployment
    "What is your reason for reporting sick outside?"
  )

  return rso_states.REASON
  
async def rso_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["reason"] = update.message.text

  await update.message.reply_text(
    f"RSO reason is {update.message.text}.\n"
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )

  return rso_states.ADDITIONAL_INFO

async def rso_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["additional_info"] = update.message.text

  rso_fields = context.user_data["rso"]
  await update.message.reply_text(
    "RSO request complete.\n"
    f"Rank/name: {rso_fields['rank_name']}\n"
    f"RSO date and time: {rso_fields['date']} {rso_fields['time']}H\n"
    f"RSO reason: {rso_fields['reason']}\n"
    f"Additional info: {rso_fields['additional_info']}"
  )

  return ConversationHandler.END

async def rso_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "RSO request cancelled.\n"
    "Send /help for a list of commands."
  )
  return ConversationHandler.END

def add_rso_handlers(application: Application):
  rso_handler = ConversationHandler(
    entry_points=[CommandHandler("rso", rso)],
    states={
      rso_states.RANK_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_rank_name)],
      rso_states.LOCATION: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_location)],
      rso_states.DATE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_date_time)],
      rso_states.REASON: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_reason)],
      rso_states.ADDITIONAL_INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_additional_info)],
    },
    fallbacks=[CommandHandler("cancel", rso_cancel)],
  )
  application.add_handler(rso_handler)
