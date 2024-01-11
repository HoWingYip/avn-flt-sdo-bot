from telegram import Update
from telegram.ext import filters, Application, ConversationHandler, CommandHandler, MessageHandler, ContextTypes

from utility.constants import RSOConversationState
from utility.validate_datetime_string import validate_datetime_string

from sqlalchemy.orm import Session as DBSession
from db.init_db import engine
from db.classes import RSORequest

async def rso(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"] = {}

  await update.message.reply_text(
    "You are now starting a Report Sick Outside (RSO) request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return RSOConversationState.RANK_NAME

async def rso_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["rank_name"] = update.message.text

  await update.message.reply_text(
    f"Rank/name is {update.message.text}.\n" # TODO: remove after deployment
    "Where will you RSO? (E.g. Ang Mo Kio Polyclinic)"
  )

  return RSOConversationState.LOCATION

async def rso_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["location"] = update.message.text

  await update.message.reply_text(
    f"RSO location is {update.message.text}.\n"
    "When will you RSO? (E.g. 010125 0800H)\n"
  )

  return RSOConversationState.DATE_TIME

async def rso_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):  
  try:
    # context.user_data["rso"]["date"], context.user_data["rso"]["time"] = \
    #   validate_datetime_string(update.message.text)

    datetime_obj = validate_datetime_string(update.message.text)
    context.user_data["rso"]["time"] = datetime_obj
  except Exception as err:
    print("Error when validating datetime:", err)
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return RSOConversationState.DATE_TIME
  
  await update.message.reply_text(
    f"Date is {datetime_obj.strftime('%d%m%y')}, time is {datetime_obj.strftime('%H%MH')}.\n"
    "What is your reason for reporting sick outside?"
  )

  return RSOConversationState.REASON
  
async def rso_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["reason"] = update.message.text

  await update.message.reply_text(
    f"RSO reason is {update.message.text}.\n"
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )

  return RSOConversationState.INFO

async def rso_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["rso"]["info"] = update.message.text

  # TODO: require user to confirm input before final submission
  # by sending /confirm after this summary is displayed
  rso_fields = context.user_data["rso"]
  await update.message.reply_text(
    "RSO request summary:\n"
    f"Rank/name: {rso_fields['rank_name']}\n"
    f"RSO location: {rso_fields['location']}\n"
    f"RSO date and time: {rso_fields['time'].strftime('%d%m%y %H%MH')}\n"
    f"RSO reason: {rso_fields['reason']}\n"
    f"Additional info: {rso_fields['info']}\n\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )

  return RSOConversationState.CONFIRM

async def rso_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  rso_fields = context.user_data["rso"]
  
  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    rso_request = RSORequest(
      rank_name=rso_fields["rank_name"],
      location=rso_fields["location"],
      time=rso_fields["time"].timestamp(),
      reason=rso_fields["reason"],
      info=rso_fields["info"],
    )

    db_session.add(rso_request)
    db_session.commit()

    await update.message.reply_text(
      f"RSO request submitted, reference code is RSO{rso_request.id}.\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )
    
    # TODO: send RSO info to all group chats
  
  return ConversationHandler.END

async def rso_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "RSO request cancelled.\n"
    "Send /help for a list of commands."
  )
  return ConversationHandler.END

def add_rso_handlers(application: Application):
  # FIXME: handler should only listen to messages in private chats
  rso_handler = ConversationHandler(
    entry_points=[CommandHandler("rso", rso)],
    states={
      RSOConversationState.RANK_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_rank_name)],
      RSOConversationState.LOCATION: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_location)],
      RSOConversationState.DATE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_date_time)],
      RSOConversationState.REASON: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_reason)],
      RSOConversationState.INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), rso_info)],
      RSOConversationState.CONFIRM: [CommandHandler("confirm", rso_confirm)],
    },
    fallbacks=[CommandHandler("cancel", rso_cancel)],
  )
  application.add_handler(rso_handler)
