from telegram import Update
from telegram.ext import filters, Application, ConversationHandler, CommandHandler, MessageHandler, ContextTypes

from features.shared import complete_request

from utility.constants import ReportSickConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_datetime_string
from utility.summarize_request import summarize_request
from utility.string_casing import uppercase_first_letter

REQUEST_TYPE = "report sick notification"

async def report_sick_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END

  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True

  await update.message.reply_text(
    "You are now starting a report sick notification. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return ReportSickConversationState.RANK_NAME

async def report_sick_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text

  await update.message.reply_text("Where will you report sick? (E.g. PLMC / Ang Mo Kio Polyclinic)")
  return ReportSickConversationState.LOCATION

async def report_sick_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["location"] = update.message.text

  await update.message.reply_text("When will you report sick? (E.g. 010125 0800H)\n")
  return ReportSickConversationState.DATE_TIME

async def report_sick_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE):  
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
    return ReportSickConversationState.DATE_TIME
  
  await update.message.reply_text("What is your reason for reporting sick?")
  return ReportSickConversationState.REASON
  
async def report_sick_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["reason"] = update.message.text

  await update.message.reply_text(
    "What course are you enrolled in? If you are not currently enrolled in a course, simply send 'Nil'."
  )
  return ReportSickConversationState.COURSE

async def report_sick_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["course"] = update.message.text

  await update.message.reply_text(
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )
  return ReportSickConversationState.INFO

async def report_sick_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{uppercase_first_letter(REQUEST_TYPE)} summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )

  return ReportSickConversationState.CONFIRM

async def report_sick_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="Do remember to update the movement charts as well."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def report_sick_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        command="reportsick",
        callback=report_sick_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      ReportSickConversationState.RANK_NAME: [
        MessageHandler(callback=report_sick_rank_name, filters=PRIVATE_MESSAGE_FILTER),
      ],
      ReportSickConversationState.LOCATION: [
        MessageHandler(callback=report_sick_location, filters=PRIVATE_MESSAGE_FILTER),
      ],
      ReportSickConversationState.DATE_TIME: [
        MessageHandler(callback=report_sick_date_time, filters=PRIVATE_MESSAGE_FILTER),
      ],      
      ReportSickConversationState.REASON: [
        MessageHandler(callback=report_sick_reason, filters=PRIVATE_MESSAGE_FILTER),
      ],
      ReportSickConversationState.COURSE: [
        MessageHandler(callback=report_sick_course, filters=PRIVATE_MESSAGE_FILTER),
      ],
      ReportSickConversationState.INFO: [
        MessageHandler(callback=report_sick_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      ReportSickConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=report_sick_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=report_sick_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))
