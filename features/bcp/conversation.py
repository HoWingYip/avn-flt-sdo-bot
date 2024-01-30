from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from features.shared import complete_request

from utility.constants import BCPConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_date_string
from utility.summarize_request import summarize_request
from utility.string_casing import uppercase_first_letter

REQUEST_TYPE = "BCP clearance request"

async def bcp_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END

  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True

  await update.message.reply_text(
    "You are now starting a Base Command Post (BCP) clearance request. To cancel, send /cancel at any time.\n"
    "Please enter your rank and full name. You may enter multiple names or a whole course (e.g. 201 BWC)."
  )

  return BCPConversationState.RANK_NAME

async def bcp_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text

  await update.message.reply_text(
    "On what date will your BCP clearance start? (E.g. 010125)"
  )
  return BCPConversationState.DATE

async def bcp_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    return BCPConversationState.DATE

  await update.message.reply_text("What location will you be accessing? (E.g. 7SD)")
  return BCPConversationState.LOCATION

async def bcp_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["location"] = update.message.text

  await update.message.reply_text(
    "What is/are the course(s) under which you are requesting clearance?"
  )
  return BCPConversationState.COURSE

async def bcp_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["course"] = update.message.text

  await update.message.reply_text(
    "What is your vehicle plate number? If not applicable, simply send 'Nil'."
  )
  return BCPConversationState.VEHICLE_NUMBER

async def bcp_vehicle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["vehicle_number"] = update.message.text

  await update.message.reply_text(
    "What is the purpose of your BCP clearance request?"
  )
  return BCPConversationState.PURPOSE

async def bcp_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["purpose"] = update.message.text

  await update.message.reply_text(
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )
  return BCPConversationState.INFO

async def bcp_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{uppercase_first_letter(REQUEST_TYPE)} request summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )
  
  return BCPConversationState.CONFIRM

async def bcp_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="This is not to be confused with the BCP clearance number, "
                               "which you will receive later."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def bcp_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # not necessary to delete context.user_data[REQUEST_TYPE]
  # because it will only be read after all fields are filled out
  await update.message.reply_text(
    f"{uppercase_first_letter(REQUEST_TYPE)} cancelled.\n"
    "Send /help for a list of commands."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

def add_handlers(app: Application):
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="bcp",
        callback=bcp_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      BCPConversationState.RANK_NAME: [
        MessageHandler(callback=bcp_rank_name, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.DATE: [
        MessageHandler(callback=bcp_date, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.LOCATION: [
        MessageHandler(callback=bcp_location, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.COURSE: [
        MessageHandler(callback=bcp_course, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.VEHICLE_NUMBER: [
        MessageHandler(callback=bcp_vehicle_number, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.PURPOSE: [
        MessageHandler(callback=bcp_purpose, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.INFO: [
        MessageHandler(callback=bcp_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      BCPConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=bcp_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=bcp_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))
