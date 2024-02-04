from telegram import Update, MessageEntity
from telegram.error import TelegramError
from telegram.ext import filters, Application, CommandHandler, ContextTypes, ConversationHandler
import time

from utility.constants import HOTOConversationState

from sqlalchemy import select, func
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import SDOLogEntry

# FIXME: things will break if some incoming SDO has no username

def get_current_sdos():
  with DBSession(engine) as db_session:
    latest_hoto_time = db_session.scalar(select(func.max(SDOLogEntry.time)))
    return db_session.execute(
      select(
        SDOLogEntry.sdo_id,
        SDOLogEntry.sdo_info,
      ).where(SDOLogEntry.time == latest_hoto_time)
    )

async def sdo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  sdo_usernames_and_info = []
  for row in get_current_sdos():
    try:
      sdo_usernames_and_info.append((
        (await context.bot.get_chat(row.sdo_id)).username,
        row.sdo_info,
      ))
    except TelegramError:
      # No user with that ID. Account was probably deleted.
      pass
  
  if sdo_usernames_and_info:
    await update.message.reply_text(
      "Current SDOs:\n" +
      "\n".join(
        f"{sdo_info}: @{sdo_username}"
        for sdo_username, sdo_info in sdo_usernames_and_info
      )
    )
  else:
    await update.message.reply_text("No SDOs are on duty.")

async def hoto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.chat_data.get("in_conversation"):
    return ConversationHandler.END

  if not context.args or \
     not all(len(username) > 1 and username[0] == "@" for username in context.args):
    await update.message.reply_text(
      "To hand over duty, send /hoto followed by the usernames "
      "of all incoming SDOs separated by spaces.\n"
      "Example: /hoto @user1 @user2"
    )
    return ConversationHandler.END

  context.chat_data["hoto"] = {}
  context.chat_data["hoto"]["acknowledged"] = {}
  context.chat_data["hoto"]["not_acknowledged"] = set(
    username[1:] for username in context.args
  )
  
  await update.message.reply_text(
    f"HOTO initiated by @{update.effective_user.username}. Send /cancel to cancel.\n\n"
    "Incoming SDOs:\n" +
    "\n".join(f"@{username}" for username in context.chat_data['hoto']['not_acknowledged']) +
    "\n\nTo complete the HOTO process, all incoming SDOs must send /hoto followed by their rank and name. "
    "Additional details like shift timing may be included.\n"
    "Example: /hoto (AM) OCT EUGENE ONG"
  )

  context.chat_data["in_conversation"] = True
  return HOTOConversationState.IN_PROGRESS

async def hoto_acknowledge(update: Update, context: ContextTypes.DEFAULT_TYPE):
  hoto_data = context.chat_data["hoto"]
  
  if update.effective_user.username not in hoto_data["not_acknowledged"]:
    if update.effective_user.id in hoto_data["acknowledged"]:
      await update.message.reply_text("You have already acknowledged this HOTO request.")
    else:
      await update.message.reply_text(
        "You are not an incoming SDO. Only incoming SDOs can acknowledge a HOTO request."
      )

    return HOTOConversationState.IN_PROGRESS
  
  if not context.args:
    await update.message.reply_text(
      "To acknowledge the HOTO request, send /hoto followed by your rank and name. "
      "Additional details like shift timing may be included.\n"
      "Example: /hoto (AM) OCT EUGENE ONG"
    )
    return HOTOConversationState.IN_PROGRESS

  hoto_data["not_acknowledged"].remove(update.effective_user.username)
  # don't use context.args because consecutive whitespace chars are lost
  hoto_data["acknowledged"][update.effective_user.id] = \
    update.message.text.split(maxsplit=1)[1]

  if hoto_data["not_acknowledged"]:
    await update.message.reply_text(
      "Acknowledgement received.\n\n"
      f"{len(hoto_data['not_acknowledged'])} incoming SDO(s) have yet to acknowledge:\n" +
      "\n".join(f"@{username}" for username in hoto_data['not_acknowledged'])
    )
    return HOTOConversationState.IN_PROGRESS
  
  hoto_time = time.time()
  with DBSession(engine) as db_session:
    for sdo_id, sdo_info in hoto_data["acknowledged"].items():
      incoming_sdo = SDOLogEntry(time=hoto_time, sdo_id=sdo_id, sdo_info=sdo_info)
      db_session.add(incoming_sdo)  

    db_session.commit()

  await update.message.reply_text(
    "All incoming SDOs have acknowledged. HOTO complete.\n"
    "To list the current SDOs, send /sdo."
  )
  del context.chat_data["hoto"]
  context.chat_data["in_conversation"] = False
  return ConversationHandler.END

async def hoto_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "HOTO cancelled.\n"
    "Send /help for a list of commands."
  )

  context.chat_data["in_conversation"] = False
  return ConversationHandler.END

def add_handlers(app: Application):
  app.add_handler(CommandHandler(command="sdo", callback=sdo))
  app.add_handler(ConversationHandler(
    # allows the ConversationHandler to listen to more than one user's commands at once
    per_user=False,

    entry_points=[
      CommandHandler(
        command="hoto",
        callback=hoto_start,
        filters=filters.ChatType.GROUPS,
      ),
    ],

    states={
      HOTOConversationState.IN_PROGRESS: [
        CommandHandler(
          command="hoto",
          callback=hoto_acknowledge,
          filters=filters.ChatType.GROUPS,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=hoto_cancel,
        filters=filters.ChatType.GROUPS,
      ),
    ],
  ))
