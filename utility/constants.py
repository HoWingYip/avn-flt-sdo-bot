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

BCPCallbackType = Enum("BCPCallbackType", [
  "ACKNOWLEDGE",
  "ACCEPT",
  "DENY",
  "UNDO_ACCEPT",
  "UNDO_DENY",
])

RSOConversationState = Enum("RSOConversationState", [
  "RANK_NAME",
  "LOCATION",
  "DATE_TIME",
  "REASON",
  "INFO",
  "CONFIRM",
])

RSOCallbackType = Enum("RSOCallbackType", [
  "ACKNOWLEDGE",
  "ACCEPT",
  "DENY",
  "UNDO_ACCEPT",
  "UNDO_DENY",
])

RequestStatus = Enum("RequestStatus", [
  "ACCEPTED",
  "REJECTED",
  "PENDING",
])
