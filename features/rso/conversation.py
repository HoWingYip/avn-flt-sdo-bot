from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import filters, Application, ConversationHandler, CommandHandler, MessageHandler, ContextTypes

from utility.constants import RSOConversationState, RSO_FIELD_NAME_MAPPING, RequestCallbackType
from utility.validate_datetime_string import validate_datetime_string
from utility.callback_data import make_callback_data
from utility.summarize_request import summarize_request

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db.init_db import engine
from db.classes import Request, RequestNotification, ChatGroup

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
  context.user_data["rso"]["additional_info"] = update.message.text

  # TODO: require user to confirm input before final submission
  # by sending /confirm after this summary is displayed
  rso_fields = context.user_data["rso"]
  await update.message.reply_text(
    "RSO request summary:\n"
    f"{summarize_request(rso_fields, RSO_FIELD_NAME_MAPPING)}\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )

  return RSOConversationState.CONFIRM

# TODO: refactor out to general request completion function
async def rso_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  rso_fields = context.user_data["rso"]
  
  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    user_id = update.effective_user.id
    request = Request(
      sender_id=user_id,
      info={
        "type": "RSO",
        "rank_name": rso_fields["rank_name"],
        "location": rso_fields["location"],
        "time": rso_fields["time"].timestamp(),
        "reason": rso_fields["reason"],
        "additional_info": rso_fields["additional_info"],
      }
    )

    db_session.add(request)
    db_session.commit()

    await update.message.reply_text(
      f"RSO request submitted, reference no. is {request.id}.\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )

    select_group_stmt = select(ChatGroup.id)
    for group_id in db_session.scalars(select_group_stmt):
      sent_message = await context.bot.send_message(
        group_id,
        text=f"New RSO request from @{update.effective_user.username}:\n"
             f"{summarize_request(rso_fields, RSO_FIELD_NAME_MAPPING)}\n"
             f"Reference no.: {request.id}",
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Acknowledge",
              callback_data=make_callback_data(RequestCallbackType.ACKNOWLEDGE, request.id)
            ),
          ),
        )),
      )

      db_message = RequestNotification(
        chat_id=group_id,
        message_id=sent_message.id,
        request=request,
      )
      db_session.add(db_message)

    db_session.commit()
  
  return ConversationHandler.END

async def rso_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "RSO request cancelled.\n"
    "Send /help for a list of commands."
  )
  return ConversationHandler.END

def add_handlers(app: Application):
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
  app.add_handler(rso_handler)
