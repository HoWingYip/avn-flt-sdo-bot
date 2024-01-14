from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CallbackQueryHandler

from utility.constants import BCPCallbackType, RequestStatus
from utility.callback_data import match_callback_type, make_callback_data, parse_callback_data
from utility.summarize_request import summarize_request

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db.init_db import engine
from db.classes import BCPRequest

async def bcp_acknowledge(update: Update, context: CallbackContext):
  query = update.callback_query
  bcp_request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_bcp_request_stmt = select(BCPRequest).where(BCPRequest.id == bcp_request_id)
    bcp_request = db_session.scalars(select_bcp_request_stmt).first()
    await context.bot.send_message(
      chat_id=bcp_request.sender_id,
      text=f"Your BCP request (ref. BCP{bcp_request_id}) has been acknowledged and the relevant approving party has been emailed. "
           f"You will be notified when your request is accepted or denied."
    )

    bcp_request.acknowledged = True
    db_session.commit()

    # update inline keyboards of all notification messages associated with this BCP request
    for message in bcp_request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Accept",
              callback_data=make_callback_data(BCPCallbackType.ACCEPT, bcp_request.id)
            ),
            InlineKeyboardButton(
              text="Deny",
              callback_data=make_callback_data(BCPCallbackType.DENY, bcp_request.id)
            ),
          ),
        )),
      )

  await query.answer()

async def bcp_accept(update: Update, context: CallbackContext):
  query = update.callback_query
  bcp_request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_bcp_request_stmt = select(BCPRequest).where(BCPRequest.id == bcp_request_id)
    bcp_request = db_session.scalars(select_bcp_request_stmt).first()
    await context.bot.send_message(
      chat_id=bcp_request.sender_id,
      text=f"Your BCP request (ref. BCP{bcp_request_id}) has been accepted."
    )

    bcp_request.status = RequestStatus.ACCEPTED
    db_session.commit()

    # TODO: allow undoing acceptance (need to delete private message sent to user)
    for message in bcp_request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Undo acceptance",
              callback_data=make_callback_data(BCPCallbackType.UNDO_ACCEPT, bcp_request.id)
            ),
          ),
        )),
      )

  await query.answer()

async def bcp_deny(update: Update, context: CallbackContext):
  query = update.callback_query
  bcp_request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_bcp_request_stmt = select(BCPRequest).where(BCPRequest.id == bcp_request_id)
    bcp_request = db_session.scalars(select_bcp_request_stmt).first()
    await context.bot.send_message(
      chat_id=bcp_request.sender_id,
      text=f"Your BCP request (ref. BCP{bcp_request_id}) has been denied."
    )

    bcp_request.status = RequestStatus.REJECTED
    db_session.commit()

    # TODO: allow undoing denial (need to delete private message sent to user)
    for message in bcp_request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Undo denial",
              callback_data=make_callback_data(BCPCallbackType.UNDO_DENY, bcp_request.id)
            ),
          ),
        )),
      )

  await query.answer()

def add_handlers(app: Application):
  app.add_handler(CallbackQueryHandler(
    bcp_acknowledge,
    pattern=match_callback_type(BCPCallbackType.ACKNOWLEDGE),
  ))
  app.add_handler(CallbackQueryHandler(
    bcp_accept,
    pattern=match_callback_type(BCPCallbackType.ACCEPT),
  ))
  app.add_handler(CallbackQueryHandler(
    bcp_deny,
    pattern=match_callback_type(BCPCallbackType.DENY),
  ))
