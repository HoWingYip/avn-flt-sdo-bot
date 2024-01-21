from telegram import Update
from telegram.ext import filters, Application, ConversationHandler, CommandHandler, MessageHandler, ContextTypes

from features.shared import complete_request

from utility.constants import RSOConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_datetime_string
from utility.summarize_request import summarize_request

REQUEST_TYPE = "RSO"

async def rso_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END

  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True

  await update.message.reply_text(
    "You are now starting a Report Sick Outside (RSO) request. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return RSOConversationState.RANK_NAME

async def rso_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text

  await update.message.reply_text("Where will you RSO? (E.g. Ang Mo Kio Polyclinic)")
  return RSOConversationState.LOCATION

async def rso_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["location"] = update.message.text

  await update.message.reply_text("When will you RSO? (E.g. 010125 0800H)\n")
  return RSOConversationState.DATE_TIME

async def rso_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):  
  try:
    datetime_obj = validate_datetime_string(update.message.text, "%d%m%y %H%MH")
    context.user_data[REQUEST_TYPE]["time"] = datetime_obj
  except Exception as err:
    print("Error when validating datetime:", err)
    await update.message.reply_text(
      "Invalid date or time. Example of expected format: 010125 1200H\n"
      "Note that date and time entered must be after the current time.\n"
      "Please try again."
    )
    return RSOConversationState.DATE_TIME
  
  await update.message.reply_text("What is your reason for reporting sick outside?")
  return RSOConversationState.REASON
  
async def rso_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["reason"] = update.message.text

  await update.message.reply_text(
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )
  return RSOConversationState.INFO

async def rso_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{REQUEST_TYPE} request summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )

  return RSOConversationState.CONFIRM

async def rso_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="Do remember to update the movement charts as well."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def rso_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        command="rso",
        callback=rso_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      RSOConversationState.RANK_NAME: [
        MessageHandler(callback=rso_rank_name, filters=PRIVATE_MESSAGE_FILTER),
      ],
      RSOConversationState.LOCATION: [
        MessageHandler(callback=rso_location, filters=PRIVATE_MESSAGE_FILTER),
      ],
      RSOConversationState.DATE_TIME: [
        MessageHandler(callback=rso_date_time, filters=PRIVATE_MESSAGE_FILTER),
      ],      
      RSOConversationState.REASON: [
        MessageHandler(callback=rso_reason, filters=PRIVATE_MESSAGE_FILTER),
      ],
      RSOConversationState.INFO: [
        MessageHandler(callback=rso_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      RSOConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=rso_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=rso_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))
