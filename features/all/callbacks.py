from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CallbackQueryHandler

from utility.constants import RequestCallbackType, RequestStatus
from utility.callback_data import match_callback_type, make_callback_data, parse_callback_data

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db import engine
from db.classes import Request

async def acknowledge(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_request_stmt = select(Request).where(Request.id == request_id)
    request = db_session.scalars(select_request_stmt).first()
    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been acknowledged and the relevant approving party has been notified. "
           f"You will be notified when your request is accepted or rejected."
    )

    request.acknowledged = True
    db_session.commit()

    # update inline keyboards of all notification messages associated with this request
    for message in request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Accept",
              callback_data=make_callback_data(RequestCallbackType.ACCEPT, request.id)
            ),
            InlineKeyboardButton(
              text="Reject",
              callback_data=make_callback_data(RequestCallbackType.REJECT, request.id)
            ),
          ),
        )),
      )

  await query.answer()

async def accept(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_request_stmt = select(Request).where(Request.id == request_id)
    request = db_session.scalars(select_request_stmt).first()
    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been accepted."
    )

    request.status = RequestStatus.ACCEPTED
    db_session.commit()

    # TODO: allow undoing acceptance (need to delete private message sent to user)
    for message in request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text=f"Accepted by @{update.effective_user.username}. Click to undo.",
              callback_data=make_callback_data(RequestCallbackType.UNDO_ACCEPT, request.id)
            ),
          ),
        )),
      )

  await query.answer()

async def reject(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    select_request_stmt = select(Request).where(Request.id == request_id)
    request = db_session.scalars(select_request_stmt).first()
    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been rejected."
    )

    request.status = RequestStatus.REJECTED
    db_session.commit()

    # TODO: allow undoing rejection (need to delete private message sent to user)
    for message in request.messages:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text=f"Rejected by @{update.effective_user.username}. Click to undo.",
              callback_data=make_callback_data(RequestCallbackType.UNDO_REJECT, request.id)
            ),
          ),
        )),
      )

  await query.answer()

def add_handlers(app: Application):
  app.add_handler(CallbackQueryHandler(
    acknowledge,
    pattern=match_callback_type(RequestCallbackType.ACKNOWLEDGE),
  ))
  app.add_handler(CallbackQueryHandler(
    accept,
    pattern=match_callback_type(RequestCallbackType.ACCEPT),
  ))
  app.add_handler(CallbackQueryHandler(
    reject,
    pattern=match_callback_type(RequestCallbackType.REJECT),
  ))
