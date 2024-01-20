from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import Request

async def message_requestor(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    request_id = int(context.args[0])
    text_to_send = update.message.text.split(maxsplit=2)[2]
  except:
    await update.message.reply_text(
      text="Syntax error.\n"
           "To send additional information to a requestor via the bot, use:\n"
           "<code>/pm [request reference no.] [text to send]</code>.",
      parse_mode="HTML",
    )
    return
  
  with DBSession(engine) as db_session:
    requestor_id = db_session.scalar(
      select(Request.sender_id).where(Request.id == request_id)
    )    
    if requestor_id is None:
      await update.message.reply_text(f"No request with reference no. {request_id}.")
      return

    await context.bot.send_message(chat_id=requestor_id, text=text_to_send)

    requestor_username = (await context.bot.get_chat(requestor_id)).username
    requestor_mention_text = f"@{requestor_username}" if requestor_username else "requestor"
    await update.message.reply_text(
      # Note: no XSS risk because Telegram usernames can only include a-z, 0-9 and underscores
      text=f"Message sent to <a href='tg://user?id={requestor_id}'>{requestor_mention_text}</a>.",
      parse_mode="HTML",
    )

def add_handlers(app: Application):
  app.add_handler(CommandHandler(
    command="pm",
    callback=message_requestor,
    filters=filters.ChatType.GROUPS,
  ))
