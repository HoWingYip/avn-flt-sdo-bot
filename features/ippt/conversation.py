from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

from utility.constants import IPPTConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_datetime_string
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
    f"Rank/name is {update.message.text}.\n"
    "At what date and time do you want your IPPT to be held? (E.g. 010125 1200H)"
  )

  return IPPTConversationState.DATE_TIME

async def ippt_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    datetime_obj = validate_datetime_string(update.message.text)
    context.user_data[REQUEST_TYPE]["time"] = datetime_obj
  except Exception as err:
    print("Error when validating datetime:", err)
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return IPPTConversationState.DATE_TIME
  
  await update.message.reply_text(
    f"Date is {datetime_obj.strftime('%d%m%y')}, time is {datetime_obj.strftime('%H%MH')}.\n"
    "What are the ranks and full names of all IPPT participants? Enter one name per line."
  )

  return IPPTConversationState.PARTICIPANTS

async def ippt_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
  names = [name.strip() for name in update.message.text.split("\n") if name.strip()]
  
  if len(names) == 0:
    await update.message.reply_text("No names were entered. Please try again.")
    return IPPTConversationState.PARTICIPANTS
  
  await update.message.reply_text(
    f"You have entered {len(names)} names:\n" + 
    "".join(f"{i+1}. {name}\n" for i, name in enumerate(names)) +
    "\nAre there any further considerations you would like us to cater for? If not, simply send 'Nil'."
  )

  context.user_data[REQUEST_TYPE]["participants"] = names
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
      IPPTConversationState.DATE_TIME: [
        MessageHandler(callback=ippt_date_time, filters=PRIVATE_MESSAGE_FILTER),
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
