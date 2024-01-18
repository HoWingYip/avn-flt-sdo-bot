from inspect import cleandoc
from enum import Enum
from telegram.ext import filters

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /rso - Request to report sick outside
  /phonebook - List important phone numbers
  /help - Display this list of commands
""")

PRIVATE_MESSAGE_FILTER = filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE

FIELD_NAME_MAPPINGS = {
  # Illegal names are: "in_conversation"
  "BCP clearance": {
    "rank_name": "Rank/name",
    "time": "Time",
    "purpose": "Purpose",
    "additional_info": "Additional info",
  },
  "RSO": {
    "rank_name": "Rank/name",
    "location": "RSO location",
    "time": "RSO date and time",
    "reason": "RSO reason",
    "additional_info": "Additional info",
  },
  "IPPT booking": {
    "rank_name": "Rank/name",
    "time": "Time",
    "participants": "Participants",
    "additional_info": "Additional info",
  }
}

BCPConversationState = Enum("BCPConversationState", [
  "RANK_NAME",
  "DATE_TIME",
  "PURPOSE",
  "INFO",
  "CONFIRM",
])

RSOConversationState = Enum("RSOConversationState", [
  "RANK_NAME",
  "LOCATION",
  "DATE_TIME",
  "REASON",
  "INFO",
  "CONFIRM",
])

IPPTConversationState = Enum("IPPTConversationState", [
  "RANK_NAME",
  "DATE_TIME",
  "PARTICIPANTS",
  "INFO",
  "CONFIRM",
])

# RequestCallbackType types must not contain "#"
# because callback data parsers split by that string
# I don't think an enum member containing that char would even be legal
# but just in case
RequestCallbackType = Enum("RSOCallbackType", [
  "ACKNOWLEDGE",
  "ACCEPT",
  "REJECT",
  "UNDO_ACCEPT",
  "UNDO_REJECT",
])

RequestStatus = Enum("RequestStatus", [
  "ACCEPTED",
  "REJECTED",
  "PENDING",
])
