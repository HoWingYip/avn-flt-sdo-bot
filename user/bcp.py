from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from utility.constants import bcp_states
from utility.validate_datetime_string import validate_datetime_string

from sqlalchemy.orm import Session as DBSession
from db.init_db import engine
from db.classes import BCPRequest

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
    f"Rank/name is {update.message.text}.\n"
    "When will your BCP clearance start? (E.g. 010125 1200H)"
  )

  return bcp_states.DATE_TIME

async def bcp_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    datetime_obj = validate_datetime_string(update.message.text)
    context.user_data["bcp"]["time"] = datetime_obj
  except Exception as err:
    print("Error when validating datetime:", err)
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return bcp_states.DATE_TIME
  
  await update.message.reply_text(
    f"Date is {datetime_obj.strftime('%d%m%y')}, time is {datetime_obj.strftime('%H%MH')}.\n"
    "What is the purpose of your BCP clearance request?"
  )

  return bcp_states.PURPOSE

async def bcp_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["purpose"] = update.message.text

  await update.message.reply_text(
    f"BCP purpose is {update.message.text}.\n"
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )

  return bcp_states.INFO

async def bcp_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["info"] = update.message.text

  bcp_fields = context.user_data["bcp"]
  await update.message.reply_text(
    "BCP clearance request summary:\n"
    f"Rank/name: {bcp_fields['rank_name']}\n"
    f"Clearance date and time: {bcp_fields['time'].strftime('%d%m%y %H%MH')}\n"
    f"Purpose: {bcp_fields['purpose']}\n"
    f"Additional info: {bcp_fields['info']}\n\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )
  
  return bcp_states.CONFIRM

async def bcp_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  bcp_fields = context.user_data["bcp"]

  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    bcp_request = BCPRequest(
      rank_name=bcp_fields["rank_name"],
      time=bcp_fields["time"].timestamp(),
      purpose=bcp_fields["purpose"],
      info=bcp_fields["info"],
    )

    db_session.add(bcp_request)
    db_session.commit()

    await update.message.reply_text(
      f"BCP clearance request submitted, reference code is BCP{bcp_request.id}.\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )

    # TODO: send BCPCR info to all group chats
    
  
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
  # FIXME: handler should only listen to messages in private chats
  bcp_handler = ConversationHandler(
    entry_points=[CommandHandler("bcp", bcp)],
    states={
      bcp_states.RANK_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_rank_name)],
      bcp_states.DATE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_date_time)],
      bcp_states.PURPOSE: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_purpose)],
      bcp_states.INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_info)],
      bcp_states.CONFIRM: [CommandHandler("confirm", bcp_confirm)],
    },
    fallbacks=[CommandHandler("cancel", bcp_cancel)],
  )
  application.add_handler(bcp_handler)
