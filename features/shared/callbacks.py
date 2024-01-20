from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CallbackQueryHandler
import logging

from utility.constants import RequestCallbackType, RequestStatus
from utility.callback_data import match_callback_type, make_callback_data, parse_callback_data

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from db import engine
from db.classes import Request, RequestVerdictNotification

logger = logging.getLogger(__name__)

async def acknowledge(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    request = db_session.scalar(select(Request).where(Request.id == request_id))
    request.status = RequestStatus.ACKNOWLEDGED
    db_session.commit()

    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been acknowledged by the SDO. "
           "You will be notified when the relevant approving party has been informed."
    )

    # update inline keyboards of all notification messages associated with this request
    for message in request.notifications:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Notify requestor that approving party has been informed",
              callback_data=make_callback_data(RequestCallbackType.APPROVER_NOTIFIED, request.id),
            ),
          ),
          (
            InlineKeyboardButton(
              text="Reject without notifying approver",
              callback_data=make_callback_data(RequestCallbackType.REJECT, request.id),
            ),
          ),
        ))
      )

  await query.answer()

async def approver_notified(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    request = db_session.scalar(select(Request).where(Request.id == request_id))
    request.status = RequestStatus.APPROVER_NOTIFIED
    db_session.commit()

    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"The relevant approving party has been informed of your {request.info['type']} request (ref. {request_id}). "
           "You will be notified when it is accepted or rejected."
    )

    # update inline keyboards of all notification messages associated with this request
    for message in request.notifications:
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
    request = db_session.scalar(select(Request).where(Request.id == request_id))
    verdict_notification = await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been accepted."
    )

    request.status = RequestStatus.ACCEPTED
    request.verdict_notification = RequestVerdictNotification(
      chat_id=request.sender_id,
      message_id=verdict_notification.id,
      request=request,
    )
    db_session.add(request.verdict_notification)
    db_session.commit()

    for message in request.notifications:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text=f"Accepted by @{update.effective_user.username}. Click to undo.",
              callback_data=make_callback_data(RequestCallbackType.UNDO_ACCEPT, request_id)
            ),
          ),
        )),
      )

  await query.answer()

async def undo_accept(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    request = db_session.scalar(select(Request).where(Request.id == request_id))

    try:
      assert request.status == RequestStatus.ACCEPTED, \
        f"Tried to undo acceptance of request {request_id} but it was not accepted"
      assert request.verdict_notification is not None, \
        f"Tried to undo acceptance of request {request_id} but verdict_notification was null"
    except AssertionError as err:
      logger.error(err)

    await context.bot.delete_message(
      chat_id=request.verdict_notification.chat_id,
      message_id=request.verdict_notification.message_id,
    )
    request.status = RequestStatus.ACCEPTANCE_REVOKED
    db_session.delete(request.verdict_notification)
    request.verdict_notification = None
    
    db_session.commit()

    # TODO: exact same code appears in acknowledge(). Extract to separate function?
    for message in request.notifications:
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

async def reject(update: Update, context: CallbackContext):
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    request = db_session.scalar(select(Request).where(Request.id == request_id))
    verdict_notification = await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your {request.info['type']} request (ref. {request_id}) has been rejected."
    )

    request.status = RequestStatus.REJECTED
    request.verdict_notification = RequestVerdictNotification(
      chat_id=request.sender_id,
      message_id=verdict_notification.id,
      request=request,
    )
    db_session.add(request.verdict_notification)
    db_session.commit()

    for message in request.notifications:
      await context.bot.edit_message_reply_markup(
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text=f"Rejected by @{update.effective_user.username}. Click to undo.",
              callback_data=make_callback_data(RequestCallbackType.UNDO_REJECT, request_id)
            ),
          ),
        )),
      )

  await query.answer()

async def undo_reject(update: Update, context: CallbackContext):
  print("Undoing rejection")
  query = update.callback_query
  request_id = parse_callback_data(query.data)[0]

  with DBSession(engine) as db_session:
    request = db_session.scalar(select(Request).where(Request.id == request_id))

    try:
      assert request.status == RequestStatus.REJECTED, \
        f"Tried to undo rejection of request {request_id} but it was not rejected"
      assert request.verdict_notification is not None, \
        f"Tried to undo rejection of request {request_id} but verdict_notification was null"
    except AssertionError as err:
      logger.error(err)

    await context.bot.delete_message(
      chat_id=request.verdict_notification.chat_id,
      message_id=request.verdict_notification.message_id,
    )
    request.status = RequestStatus.REJECTION_REVOKED
    db_session.delete(request.verdict_notification)
    request.verdict_notification = None

    db_session.commit()

    # TODO: exact same code appears in acknowledge(). Extract to separate function?
    for message in request.notifications:
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

def add_handlers(app: Application):
  app.add_handler(CallbackQueryHandler(
    acknowledge,
    pattern=match_callback_type(RequestCallbackType.ACKNOWLEDGE),
  ))
  app.add_handler(CallbackQueryHandler(
    approver_notified,
    pattern=match_callback_type(RequestCallbackType.APPROVER_NOTIFIED),
  ))
  app.add_handler(CallbackQueryHandler(
    accept,
    pattern=match_callback_type(RequestCallbackType.ACCEPT),
  ))
  app.add_handler(CallbackQueryHandler(
    reject,
    pattern=match_callback_type(RequestCallbackType.REJECT),
  ))
  app.add_handler(CallbackQueryHandler(
    undo_accept,
    pattern=match_callback_type(RequestCallbackType.UNDO_ACCEPT),
  ))
  app.add_handler(CallbackQueryHandler(
    undo_reject,
    pattern=match_callback_type(RequestCallbackType.UNDO_REJECT),
  ))
  app.add_handler(CallbackQueryHandler(
    lambda update, context: logger.warning(
      f"Unhandled callback message. Data: {update.callback_query.data!r}"
    ),
  ))
