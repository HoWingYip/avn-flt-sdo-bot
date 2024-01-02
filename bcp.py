from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from constants import bcp_states
from utility.validate_datetime_string import validate_datetime_string

# TODO: remove all echo text after deployment

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
  try:
    context.user_data["bcp"]["date"], context.user_data["bcp"]["time"] = \
      validate_datetime_string(update.message.text)
  except:
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return bcp_states.DATE_TIME
  
  await update.message.reply_text(
    f"Date is {context.user_data['bcp']['date']}, time is {context.user_data['bcp']['time']}H.\n"
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

  # TODO: require user to confirm input before final submission
  # by sending /confirm after this summary is displayed
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
