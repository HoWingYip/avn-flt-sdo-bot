from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CallbackQueryHandler
from enum import Enum

from utility.constants import BCPCallbackType
from utility.callback_data import match_callback_type

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db.init_db import engine
from db.classes import BCPRequest

async def bcp_acknowledge(update: Update, context: CallbackContext):
  query = update.callback_query
  bcp_request_id = query.data.split("__")[1]

  with DBSession(engine) as db_session:
    select_bcp_id_stmt = \
      select(BCPRequest.sender_id).where(BCPRequest.id == bcp_request_id)
    chat_id = db_session.scalars(select_bcp_id_stmt).first()
    await context.bot.send_message(
      chat_id=chat_id,
      text=f"Your BCP request (ref. BCP{bcp_request_id}) has been acknowledged. "
           f"You will be notified when it is accepted or denied."
    )

  await query.answer()

  # TODO: change button in all chats so each BCPCR can only be acknowledged once
  # make Acknowledge button a no-op
  inline_keyboard = list(list(row) for row in query.message.reply_markup.inline_keyboard)
  inline_keyboard[0][0] = InlineKeyboardButton(text="☑️ Acknowledged", callback_data="noop")
  await query.edit_message_reply_markup(InlineKeyboardMarkup(inline_keyboard))

def add_handlers(app: Application):
  app.add_handler(CallbackQueryHandler(
    bcp_acknowledge,
    pattern=match_callback_type(BCPCallbackType.ACKNOWLEDGE)
  ))
