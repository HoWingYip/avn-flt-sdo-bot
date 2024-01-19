from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes, ConversationHandler

from utility.constants import HOTOConversationState

from sqlalchemy import select, func
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import SDOLogEntry

async def sdo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "Current SDOs:\n" +
    "\n".join(f"{sdo_info}: {username}" for username, sdo_info in current_sdos)
  )

# async def hoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   global current_sdos # TODO: replace with DB lookup
#   sender_username = update.effective_user.username

#   if "hoto" not in context.chat_data: # start new HOTO
#     # if no current SDOs, allow anyone to HOTO
#     if len(current_sdos) > 0 and sender_username not in current_sdos:
#       await update.message.reply_text(
#         "You are not a current SDO. Only current SDOs may initiate a HOTO."
#       )
#       return

#     incoming_sdos = set()
#     for username in context.args:
#       if len(username) <= 1 or username[0] != "@":
#         await update.message.reply_text(
#           "Syntax error. To hand over duty, send /hoto followed by the usernames "
#           "of all incoming SDOs separated by spaces.\n"
#           "Example: /hoto @user1 @user2"
#         )
#         return

#       incoming_sdos.add(username[1:])

#     if len(incoming_sdos) == 0:
#       await update.message.reply_text(
#         "At least one incoming SDO must be mentioned.\n"
#         "To hand over duty, send /hoto followed by the usernames of all incoming "
#         "SDOs separated by spaces.\n"
#         "Example: /hoto @user1 @user2"
#       )
#       return
    
#     context.chat_data["hoto"] = {}
#     context.chat_data["hoto"]["acknowledged"] = {}
#     context.chat_data["hoto"]["not_acknowledged"] = incoming_sdos

#     await update.message.reply_text(
#       f"HOTO initiated by @{sender_username}. Send /cancel to cancel.\n\n"
#       "Incoming SDOs:\n" + "\n".join(incoming_sdos) +
#       "\n\nTo complete the HOTO process, all incoming SDOs must send /hoto followed by their rank and name. "
#       "Additional details like shift timing may be included.\n"
#       "Example: /hoto (AM) OCT EUGENE ONG"
#     )
#   else: # acknowledge ongoing HOTO
#     hoto_data = context.chat_data["hoto"]
#     if sender_username not in hoto_data["not_acknowledged"]:
#       return

#     hoto_data["not_acknowledged"].remove(sender_username)
#     hoto_data["acknowledged"][sender_username] = update.message.text.split(maxsplit=1)[1]

#     if len(hoto_data["not_acknowledged"]) == 0:
#       await update.message.reply_text(
#         "All incoming SDOs have acknowledged. HOTO complete."
#       )
#       current_sdos = hoto_data["acknowledged"]
#       del context.chat_data["hoto"]
#     else:
#       await update.message.reply_text(
#         "Acknowledgement received.\n"
#         f"{len(hoto_data['not_acknowledged'])} incoming SDOs have yet to acknowledge:\n" +
#         "\n".join(f"@{username}" for username in hoto_data['not_acknowledged'])
#       )

async def hoto_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  with DBSession(engine) as db_session:
    latest_hoto_time = db_session.scalar(select(func.max(SDOLogEntry.time)))
    select_current_sdos_stmt = select(SDOLogEntry.incoming_sdo_id) \
      .where(SDOLogEntry.time == latest_hoto_time)
    
    num_log_entries = db_session.scalar(select(func.count(SDOLogEntry)))
    if update.effective_user.id not in db_session.scalars(select_current_sdos_stmt):
      await update.message.reply_text(
        "You are not a current SDO. Only current SDOs may initiate a HOTO."
      )
      return

async def hoto_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  pass

def add_handlers(app: Application):
  app.add_handler(CommandHandler(command="sdo", callback=sdo))
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="hoto",
        callback=hoto_start,
        filters=filters.ChatType.GROUPS,
      ),
    ],

    states={
      HOTOConversationState.IN_PROGRESS: [

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
