from inspect import cleandoc
from enum import Enum
from telegram.ext import filters

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /ippt - Request to book an IPPT session
  /rso - Inform the SDO that you will report sick outside
  /phonebook - List important phone numbers
  /sdo - List the current Student Duty Officers
  /help - Display this list of commands
""")

PRIVATE_MESSAGE_FILTER = filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE

FIELD_NAME_MAPPINGS = {
  # Illegal names are: "in_conversation"
  "BCP clearance": {
    "rank_name": "Rank/name",
    "location": "Location",
    "course": "Course(s)",
    "vehicle_number": "Vehicle plate number",
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
    "participants": "Participants",
    "additional_info": "Additional considerations",
  },
}

BCPConversationState = Enum("BCPConversationState", [
  "RANK_NAME",
  "LOCATION",
  "COURSE",
  "VEHICLE_NUMBER",
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
  "PARTICIPANTS",
  "INFO",
  "CONFIRM",
])

HOTOConversationState = Enum("HOTOConversationState", [
  "IN_PROGRESS",
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
