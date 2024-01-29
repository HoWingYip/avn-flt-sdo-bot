from inspect import cleandoc
from enum import Enum
from telegram.ext import filters

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /ippt - Request to book an IPPT session
  /rso - Inform the SDO that you will report sick outside
  /mc - Inform the SDO of your medical certificate
  /sdo - List the current Student Duty Officers
  /help - Display this list of commands
""")

PRIVATE_MESSAGE_FILTER = filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE

FIELD_NAME_MAPPINGS = {
  # Illegal names are: "in_conversation"
  "BCP clearance request": {
    "rank_name": "Rank/name",
    "date": "Date",
    "location": "Location",
    "course": "Course(s)",
    "vehicle_number": "Vehicle plate number",
    "purpose": "Purpose",
    "additional_info": "Additional info",
  },
  "RSO notification": {
    "rank_name": "Rank/name",
    "location": "RSO location",
    "time": "RSO date and time",
    "reason": "RSO reason",
    "additional_info": "Additional info",
  },
  "IPPT booking request": {
    "rank_name": "Rank/name",
    "date": "Date",
    "participants": "Participants",
    "additional_info": "Additional considerations",
  },
  "MC notification": {
    "rank_name": "Rank/name",
    "start_date": "Start date",
    "end_date": "End date",
    "reason": "Reason",
    "additional_info": "Additional info",
  },
  "Enquiry": {
    "enquiry": "Enquiry",
  },
}

REQUEST_TYPE_REQUIRES_APPROVAL = {
  "BCP clearance request": True,
  "RSO notification": True,
  "MC notification": True,
  "IPPT booking request": True,
  "Enquiry": False,
}

REQUEST_TYPE_REQUIRES_INDEPENDENT_APPROVAL = {
  "BCP clearance request": True,
  "RSO notification": False,
  "MC notification": False,
  "IPPT booking request": True,
  "Enquiry": False,
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
  "PERIOD",
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

EnquiryConversationState = Enum("EnquiryConversationState", [
  "ENQUIRY_RECEIVED",
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
