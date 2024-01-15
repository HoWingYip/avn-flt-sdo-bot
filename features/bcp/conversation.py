from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from utility.constants import BCPConversationState, BCP_FIELD_NAME_MAPPING, RequestCallbackType
from utility.validate_datetime_string import validate_datetime_string
from utility.callback_data import make_callback_data
from utility.summarize_request import summarize_request

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db.init_db import engine
from db.classes import Request, ChatGroup, RequestNotification

# TODO: remove all echo text after deployment

async def bcp(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"] = {}

  await update.message.reply_text(
    "You are now starting a Base Command Post (BCP) clearance request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return BCPConversationState.RANK_NAME

async def bcp_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["rank_name"] = update.message.text

  await update.message.reply_text(
    f"Rank/name is {update.message.text}.\n"
    "When will your BCP clearance start? (E.g. 010125 1200H)"
  )

  return BCPConversationState.DATE_TIME

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
    return BCPConversationState.DATE_TIME
  
  await update.message.reply_text(
    f"Date is {datetime_obj.strftime('%d%m%y')}, time is {datetime_obj.strftime('%H%MH')}.\n"
    "What is the purpose of your BCP clearance request?"
  )

  return BCPConversationState.PURPOSE

async def bcp_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["purpose"] = update.message.text

  await update.message.reply_text(
    f"BCP purpose is {update.message.text}.\n"
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )

  return BCPConversationState.INFO

async def bcp_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["bcp"]["additional_info"] = update.message.text

  bcp_fields = context.user_data["bcp"]
  await update.message.reply_text(
    "BCP clearance request summary:\n"
    f"{summarize_request(bcp_fields, BCP_FIELD_NAME_MAPPING)}\n\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )
  
  return BCPConversationState.CONFIRM

# TODO: refactor out to general request completion function
async def bcp_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  bcp_fields = context.user_data["bcp"]

  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    user_id = update.effective_user.id
    request = Request(
      sender_id=user_id,
      info={
        "type": "BCP",
        "rank_name": bcp_fields["rank_name"],
        "time": bcp_fields["time"].timestamp(),
        "purpose": bcp_fields["purpose"],
        "additional_info": bcp_fields["additional_info"],
      }
    )

    db_session.add(request)
    db_session.commit()

    await update.message.reply_text(
      f"BCP clearance request submitted; reference no. is {request.id}.\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )

    select_group_stmt = select(ChatGroup.id)
    for group_id in db_session.scalars(select_group_stmt):
      sent_message = await context.bot.send_message(
        group_id,
        text=f"New BCP clearance request from @{update.effective_user.username}:\n"
             f"{summarize_request(bcp_fields, BCP_FIELD_NAME_MAPPING)}\n"
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

async def bcp_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # not necessary to delete context.user_data["bcp"]
  # because it will only be read after all fields are filled out
  await update.message.reply_text(
    "BCP clearance request cancelled.\n"
    "Send /help for a list of commands."
  )
  return ConversationHandler.END

def add_handlers(app: Application):
  # FIXME: handler should only listen to messages in private chats
  bcp_handler = ConversationHandler(
    entry_points=[CommandHandler("bcp", bcp)],
    states={
      BCPConversationState.RANK_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_rank_name)],
      BCPConversationState.DATE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_date_time)],
      BCPConversationState.PURPOSE: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_purpose)],
      BCPConversationState.INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), bcp_info)],
      BCPConversationState.CONFIRM: [CommandHandler("confirm", bcp_confirm)],
    },
    fallbacks=[CommandHandler("cancel", bcp_cancel)],
  )
  app.add_handler(bcp_handler)
