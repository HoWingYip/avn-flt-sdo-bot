from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler

from features.shared import complete_request

from utility.constants import MCConversationState, PRIVATE_MESSAGE_FILTER
from utility.validate_datetime_string import validate_date_string
from utility.summarize_request import summarize_request

REQUEST_TYPE = "MC notification"

async def mc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END

  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True

  await update.message.reply_text(
    "You are now starting a Medical Certificate (MC) notification. To cancel, send /cancel at any time.\n"
    "What is your rank and full name? (E.g. PTE Jay Chou)"
  )

  return MCConversationState.RANK_NAME

async def mc_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text

  await update.message.reply_text("Over what time period will you be on MC? (E.g. 010125-020125)")
  return MCConversationState.PERIOD

async def mc_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    start_date_text, end_date_text = update.message.text.split("-")
    start_date_obj = validate_date_string(start_date_text, "%d%m%y")
    end_date_obj = validate_date_string(end_date_text, "%d%m%y")
    
    assert start_date_obj <= end_date_obj, "Start date cannot be before end date"
  except Exception as err:
    print("Error when validating dates:", err)
    await update.message.reply_text(
      "Invalid date(s) or format. Example of expected format: 010125-020125\n"
      "Note that start date cannot be before end date, and both dates cannot be before today.\n"
      "Please try again."
    )
    return MCConversationState.PERIOD
  
  context.user_data[REQUEST_TYPE]["start_date"] = start_date_obj
  context.user_data[REQUEST_TYPE]["end_date"] = end_date_obj

  await update.message.reply_text("What is the reason for your MC?")
  return MCConversationState.REASON

async def mc_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["reason"] = update.message.text

  await update.message.reply_text(
    "Do you have any additional information or queries? If not, simply send 'Nil'."
  )
  return MCConversationState.INFO

async def mc_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{REQUEST_TYPE} request summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n"
    "To confirm the above information and submit the request, send /confirm. To cancel, send /cancel."
  )
  return MCConversationState.CONFIRM

async def mc_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="Do remember to update the movement charts as well."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def mc_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    f"{REQUEST_TYPE} cancelled.\n"
    "Send /help for a list of commands."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

def add_handlers(app: Application):
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="mc",
        callback=mc_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      MCConversationState.RANK_NAME: [
        MessageHandler(callback=mc_rank_name, filters=PRIVATE_MESSAGE_FILTER),
      ],
      MCConversationState.PERIOD: [
        MessageHandler(callback=mc_period, filters=PRIVATE_MESSAGE_FILTER),
      ],
      MCConversationState.REASON: [
        MessageHandler(callback=mc_reason, filters=PRIVATE_MESSAGE_FILTER),
      ],
      MCConversationState.INFO: [
        MessageHandler(callback=mc_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      MCConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=mc_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=mc_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))

