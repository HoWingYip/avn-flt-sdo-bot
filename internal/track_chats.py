import logging
from telegram import Update, ChatMember, Chat
from telegram.ext import Application, ContextTypes, ChatMemberHandler

from sqlalchemy.orm import Session as DBSession
from db import engine
from db.classes import ChatGroup

# TODO: in production, DISABLE ADDING BOT TO GROUPS after adding it to official groups!
# If this step is forgotten, a privacy risk will result!
# Also consider requiring the bot to be activated by password after being added to a group

logger = logging.getLogger(__name__)

async def on_membership_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat = update.effective_chat
  if chat.type == Chat.PRIVATE:
    return

  status_change = update.my_chat_member.difference().get("status")
  if status_change is None:
    return

  old_is_member, new_is_member = update.my_chat_member.difference().get("is_member", (None, None))

  old_status, new_status = status_change
  was_member = old_status in [
    ChatMember.MEMBER,
    ChatMember.OWNER,
    ChatMember.ADMINISTRATOR,
  ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)

  is_member = new_status in [
    ChatMember.MEMBER,
    ChatMember.OWNER,
    ChatMember.ADMINISTRATOR,
  ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

  # avoids instantiating DB session if bot didn't join or leave group
  if not was_member ^ is_member:
    return

  with DBSession(engine) as db_session, db_session.begin():
    if is_member and not was_member:
      logger.info(f"Bot joined group ID {chat.id}")
      newly_joined_group = ChatGroup(id=chat.id)
      db_session.add(newly_joined_group)
    elif was_member and not is_member:
      logger.info(f"Bot removed from group ID {chat.id}")
      left_group = db_session.get(ChatGroup, chat.id)
      db_session.delete(left_group)

def track_chats(app: Application):
  app.add_handler(ChatMemberHandler(on_membership_update, ChatMemberHandler.MY_CHAT_MEMBER))
