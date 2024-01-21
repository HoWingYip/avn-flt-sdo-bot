from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from utility.summarize_request import summarize_request
from utility.callback_data import make_callback_data
from utility.constants import RequestCallbackType, REQUEST_TYPE_REQUIRES_INDEPENDENT_APPROVAL

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import Request, RequestNotification, ChatGroup

async def complete_request(
    request_type: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    additional_completion_text: str = "",
):
  user_id = update.effective_user.id
  fields = context.user_data[request_type]

  # disable expire_on_commit so we don't need to start another transaction
  # to load request ID after commit
  with DBSession(engine, expire_on_commit=False) as db_session:
    request_info = {"type": request_type, **fields}
    if "time" in request_info:
      request_info["time"] = request_info["time"].timestamp()

    request = Request(
      sender_id=user_id,
      info=request_info,
    )

    db_session.add(request)
    db_session.commit()

    await update.message.reply_text(
      f"{request_type} request submitted; reference no. is {request.id}.\n"
      f"{additional_completion_text}\n"
      "If you wish to carry out more actions, send /help for a list of commands."
    )

    for group_id in db_session.scalars(select(ChatGroup.id)):
      sent_message = await context.bot.send_message(
        group_id,
        text=f"New {request_type} request from @{update.effective_user.username}:\n"
             f"{summarize_request(request_type, fields)}\n"
             f"<b>Reference no.: {request.id}</b>\n\n"
             "To send additional information to this requestor via the bot, use:\n"
             f"<code>/pm {request.id} [text to send]</code>.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup((
          (
            InlineKeyboardButton(
              text="Acknowledge",
              callback_data=make_callback_data(
                callback_type=RequestCallbackType.ACKNOWLEDGE
                              if REQUEST_TYPE_REQUIRES_INDEPENDENT_APPROVAL[request_type]
                              else RequestCallbackType.APPROVE,
                data=(request.id,)
              )
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
  
  
