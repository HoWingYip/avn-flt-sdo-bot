from inspect import cleandoc
from enum import Enum
from telegram.ext import filters

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /ippt - Request to book an IPPT session
  /rso - Inform the SDO that you will report sick outside
  /sdo - List the current Student Duty Officers
  /help - Display this list of commands
""")

PRIVATE_MESSAGE_FILTER = filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE

FIELD_NAME_MAPPINGS = {
  # Illegal names are: "in_conversation"
  "BCP clearance": {
    "rank_name": "Rank/name",
    "date": "Date",
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
    "date": "Date",
    "participants": "Participants",
    "additional_info": "Additional considerations",
  },
  "MC": {
    "rank_name": "Rank/name",
    "duration": "Duration",
    "reason": "Reason",
    "additional_info": "Additional info",
  }
}

REQUEST_TYPE_REQUIRES_INDEPENDENT_APPROVAL = {
  "BCP clearance": True,
  "RSO": False,
  "MC": False,
  "IPPT booking": True,
}

BCPConversationState = Enum("BCPConversationState", [
  "RANK_NAME",
  "DATE",
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

MCConversationState = Enum("MCConversationState", [
  "RANK_NAME",
  "DURATION",
  "REASON",
  "INFO",
  "CONFIRM",
])

IPPTConversationState = Enum("IPPTConversationState", [
  "RANK_NAME",
  "DATE",
  "PARTICIPANTS",
  "INFO",
  "CONFIRM",
])

HOTOConversationState = Enum("HOTOConversationState", [
  "IN_PROGRESS",
])

# RequestCallbackType types must not contain "#" because all callback data
# parsers split by that character.
# Enum members containing "#" are inaccessible through dot notation but this is
# just in case someone attempts to pull something stupid using getattr().
RequestCallbackType = Enum("RSOCallbackType", [
  "ACKNOWLEDGE",
  "APPROVER_NOTIFIED",
  "APPROVE",
  "REJECT",
  "UNDO_APPROVE",
  "UNDO_REJECT",
])

RequestStatus = Enum("RequestStatus", [
  "PENDING_ACKNOWLEDGEMENT",
  "ACKNOWLEDGED",
  "APPROVER_NOTIFIED",
  "APPROVED",
  "REJECTED",
  "APPROVAL_REVOKED",
  "REJECTION_REVOKED",
])
