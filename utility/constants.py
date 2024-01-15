from inspect import cleandoc
from enum import Enum

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /rso - Request to report sick outside
  /phonebook - List important phone numbers
  /help - Display this list of commands
""")

BCPConversationState = Enum("BCPConversationState", [
  "RANK_NAME",
  "DATE_TIME",
  "PURPOSE",
  "INFO",
  "CONFIRM",
])

BCP_FIELD_NAME_MAPPING = {
  "rank_name": "Rank/name",
  "time": "Time",
  "purpose": "Purpose",
  "additional_info": "Additional info",
}

RSOConversationState = Enum("RSOConversationState", [
  "RANK_NAME",
  "LOCATION",
  "DATE_TIME",
  "REASON",
  "INFO",
  "CONFIRM",
])

RSO_FIELD_NAME_MAPPING = {
  "rank_name": "Rank/name",
  "location": "RSO location",
  "time": "RSO date and time",
  "reason": "RSO reason",
  "additional_info": "Additional info",
}

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
