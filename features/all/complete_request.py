from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utility.summarize_request import summarize_request
from utility.callback_data import make_callback_data
from utility.constants import RequestCallbackType, FIELD_NAME_MAPPINGS

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import Request, RequestNotification, ChatGroup

async def complete_request(
    request_type: str,
    user_id: int,
    fields: dict,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    request = Request(
      sender_id=user_id,
      info={"type": request_type, **fields}
    )

    db_session.add(request)
    db_session.commit()

    await update.message.reply_text(
      f"{request_type} clearance request submitted; reference no. is {request.id}.\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )

    select_group_stmt = select(ChatGroup.id)
    for group_id in db_session.scalars(select_group_stmt):
      sent_message = await context.bot.send_message(
        group_id,
        text=f"New {request_type} request from @{update.effective_user.username}:\n"
             f"{summarize_request(fields, FIELD_NAME_MAPPINGS[request_type])}\n"
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
  
  
