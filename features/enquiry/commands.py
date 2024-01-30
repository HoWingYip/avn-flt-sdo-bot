from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler

from features.shared import complete_request

from utility.constants import EnquiryConversationState, PRIVATE_MESSAGE_FILTER

REQUEST_TYPE = "enquiry"

async def enquiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END
  
  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True
  
  await update.message.reply_text(
    "You are now submitting an enquiry. Send /cancel to cancel.\n"
    "Your next message will be forwarded to the SDOs. Enquire wisely."
  )

  return EnquiryConversationState.ENQUIRY_RECEIVED

async def enquiry_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["enquiry"] = update.message.text

  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="Your enquiry has been forwarded to the SDOs. "
                               "A reply will arrive soon."
  )

  context.user_data["in_conversation"] = False
  return ConversationHandler.END

async def enquiry_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "Enquiry cancelled.\n"
    "Send /help for a list of commands."
  )
  
  context.user_data["in_conversation"] = False
  return ConversationHandler.END

def add_handlers(app: Application):
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="enquiry",
        callback=enquiry,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      EnquiryConversationState.ENQUIRY_RECEIVED: [
        MessageHandler(callback=enquiry_received, filters=PRIVATE_MESSAGE_FILTER),
      ],
    },

    fallbacks=[
      CommandHandler(
        command="cancel",
        callback=enquiry_cancel,
        filters=filters.ChatType.PRIVATE,
      ),
    ],
  ))
