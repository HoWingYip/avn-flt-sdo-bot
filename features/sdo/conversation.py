from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes

current_sdos = set()
incoming_sdos = {}

async def sdo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  pass

async def hoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # incoming_sdos = {username[1:] for username in update.message.text.split(" ")[1:]}
  if len(incoming_sdos) > 0:
    # attempt to start new HOTO
    if context.chat_data["hoto"] is None and update.effective_user.username in current_sdos:
      # start new HOTO
      pass
    elif context.chat_data["hoto"] is not None:
      # HOTO already in progress
      pass
    else:
      # not allowed to initiate HOTO because user not currently an SDO
      pass
  else:
    # /hoto with no args is only sent by incoming SDOs
    if context.chat_data["hoto"] is not None and update.effective_user.username in incoming_sdos:
      # success - incoming SDO has acknowledged
      pass
    elif context.chat_data["hoto"] is None:
      # no HOTO in progress, so can't acknowledge
      # display help message - "No HOTO is in progress. To hand over duty to the incoming SDOs, send '/hoto @incoming_sdo_1 @incoming_sdo_2 ...'"
      pass
    else:
      # user who sent /hoto is not an incoming SDO; ignore
      pass

  await update.message.reply_text(update.message.text)

def add_handlers(app: Application):
  app.add_handler(CommandHandler(command="sdo", callback=sdo))
  app.add_handler(CommandHandler(
    command="hoto",
    callback=hoto,
    filters=filters.ChatType.GROUPS,
  ))
