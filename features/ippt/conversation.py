from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

from utility.constants import IPPTConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_date_string
from utility.summarize_request import summarize_request

from features.shared import complete_request

REQUEST_TYPE = "IPPT booking"

async def ippt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END

  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True

  await update.message.reply_text(
    "You are now starting an IPPT booking request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )
  return IPPTConversationState.RANK_NAME

async def ippt_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text

  await update.message.reply_text(
    "On what date do you want your IPPT to be held? (E.g. 010125)"
  )
  return IPPTConversationState.DATE

async def ippt_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    date_obj = validate_date_string(update.message.text, "%d%m%y")
    context.user_data[REQUEST_TYPE]["date"] = date_obj
  except Exception as err:
    print("Error when validating date:", err)
    await update.message.reply_text(
      "Invalid date. Example of expected format: 010125\n"
      "Note that date entered cannot be before today.\n"
      "Please try again."
    )
    return IPPTConversationState.DATE

  await update.message.reply_text(
    "What are the ranks and full names of all IPPT participants you are registering for? Enter one name per line."
  )
  return IPPTConversationState.PARTICIPANTS

async def ippt_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
  names = [name.strip() for name in update.message.text.split("\n") if name.strip()]
  
  if len(names) == 0:
    await update.message.reply_text("No names were entered. Please try again.")
    return IPPTConversationState.PARTICIPANTS

  context.user_data[REQUEST_TYPE]["participants"] = names
  
  await update.message.reply_text(
    "Are there any further considerations you would like us to cater for? If not, simply send 'Nil'."
  )
  return IPPTConversationState.INFO

async def ippt_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{REQUEST_TYPE} request summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )
  return IPPTConversationState.CONFIRM

async def ippt_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(request_type=REQUEST_TYPE, update=update, context=context)

  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def ippt_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    f"{REQUEST_TYPE} request cancelled.\n"
    "Send /help for a list of commands."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

def add_handlers(app: Application):
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="ippt",
        callback=ippt_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      IPPTConversationState.RANK_NAME: [
        MessageHandler(callback=ippt_rank_name, filters=PRIVATE_MESSAGE_FILTER),        
      ],
      IPPTConversationState.DATE: [
        MessageHandler(callback=ippt_date, filters=PRIVATE_MESSAGE_FILTER),
      ],
      IPPTConversationState.PARTICIPANTS: [
        MessageHandler(callback=ippt_participants, filters=PRIVATE_MESSAGE_FILTER),
      ],
      IPPTConversationState.INFO: [
        MessageHandler(callback=ippt_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      IPPTConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=ippt_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=ippt_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))
