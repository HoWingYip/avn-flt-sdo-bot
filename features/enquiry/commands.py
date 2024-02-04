from telegram import Update
from telegram.ext import filters, Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler

from features.shared import complete_request

from utility.summarize_request import summarize_request
from utility.string_casing import uppercase_first_letter
from utility.constants import EnquiryConversationState, PRIVATE_MESSAGE_FILTER

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import Request

REQUEST_TYPE = "enquiry"

async def enquiry_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.user_data.get("in_conversation"):
    return ConversationHandler.END
  
  context.user_data[REQUEST_TYPE] = {}
  context.user_data["in_conversation"] = True
  
  await update.message.reply_text(
    "You are now submitting an enquiry to the SDO. To cancel, send /cancel at any time.\n"
    "What is your rank and name? (E.g. REC Ken Chow)"
  )

  return EnquiryConversationState.RANK_NAME

async def enquiry_rank_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["rank_name"] = update.message.text
  
  await update.message.reply_text(
    "What course are you enrolled in? If you are not currently enrolled in a course, simply send 'Nil'."
  )
  return EnquiryConversationState.COURSE

async def enquiry_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["course"] = update.message.text

  await update.message.reply_text("What is your enquiry?")
  return EnquiryConversationState.ENQUIRY

async def enquiry_enquiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["enquiry"] = update.message.text
  
  await update.message.reply_text(
    "Do you have any additional information? If not, simply send 'Nil'."
  )
  return EnquiryConversationState.INFO

async def enquiry_additional_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data[REQUEST_TYPE]["additional_info"] = update.message.text

  await update.message.reply_text(
    f"{uppercase_first_letter(REQUEST_TYPE)} summary:\n"
    f"{summarize_request(request_type=REQUEST_TYPE, fields=context.user_data[REQUEST_TYPE])}\n\n"
    "To confirm the above information and submit the enquiry, send /confirm. To cancel, send /cancel."
  )
  return EnquiryConversationState.CONFIRM

async def enquiry_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await complete_request(
    request_type=REQUEST_TYPE,
    update=update,
    context=context,
    additional_completion_text="The SDO will contact you shortly to assist you."
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

async def resolve_enquiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    request_id = int(context.args[0])
  except:
    await update.message.reply_text(
      text="Syntax error.\n"
           "To resolve an enquiry, use:\n"
           "<code>/resolve [request reference no.]</code>",
      parse_mode="HTML",
    )
    return
  
  with DBSession(engine) as db_session:
    request = db_session.scalar(
      select(Request).where(Request.id == request_id)
    )

    if not request or request.info["type"] != "enquiry":
      await update.message.reply_text(f"No enquiry with reference no. {request_id}.")
      return
    
    if "resolved" in request.info and request.info["resolved"]:
      await update.message.reply_text(f"Enquiry already resolved.")
      return
    
    request.info["resolved"] = True
    db_session.add(request)
    db_session.commit()

    await update.message.reply_text("Enquiry marked as resolved. User has been notified.")
    await context.bot.send_message(
      chat_id=request.sender_id,
      text=f"Your enquiry (ref. {request_id}) has been marked as resolved.",
    )

def add_handlers(app: Application):
  app.add_handler(ConversationHandler(
    entry_points=[
      CommandHandler(
        command="enquiry",
        callback=enquiry_start,
        filters=filters.ChatType.PRIVATE,
      ),
    ],

    states={
      EnquiryConversationState.RANK_NAME: [
        MessageHandler(callback=enquiry_rank_name, filters=PRIVATE_MESSAGE_FILTER),
      ],
      EnquiryConversationState.COURSE: [
        MessageHandler(callback=enquiry_course, filters=PRIVATE_MESSAGE_FILTER),
      ],
      EnquiryConversationState.ENQUIRY: [
        MessageHandler(callback=enquiry_enquiry, filters=PRIVATE_MESSAGE_FILTER),
      ],
      EnquiryConversationState.INFO: [
        MessageHandler(callback=enquiry_additional_info, filters=PRIVATE_MESSAGE_FILTER),
      ],
      EnquiryConversationState.CONFIRM: [
        CommandHandler(
          command="confirm",
          callback=enquiry_confirm,
          filters=filters.ChatType.PRIVATE,
        ),
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

  app.add_handler(CommandHandler(
    command="resolve",
    callback=resolve_enquiry,
    filters=filters.ChatType.GROUPS,
  ))
