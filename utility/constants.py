from inspect import cleandoc
from enum import Enum
from telegram.ext import filters

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /ippt - Request to book an IPPT session
  /reportsick - Inform the SDOs that you will report sick inside/outside
  /mc - Inform the SDOs of your medical certificate
  /sdo - List the current Student Duty Officers
  /enquiry - Send an enquiry to the SDOs
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
  "report sick notification": {
    "rank_name": "Rank/name",
    "location": "Report sick location",
    "time": "Date and time of reporting sick",
    "reason": "Reason for reporting sick",
    "course": "Courses enrolled in",
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
    "course": "Courses enrolled in",
    "additional_info": "Additional info",
  },
  "enquiry": {
    "enquiry": "Enquiry",
  },
}

REQUEST_TYPE_REQUIRES_APPROVAL = {
  "BCP clearance request": True,
  "report sick notification": True,
  "MC notification": True,
  "IPPT booking request": True,
  "enquiry": False,
}

REQUEST_TYPE_REQUIRES_INDEPENDENT_APPROVAL = {
  "BCP clearance request": True,
  "report sick notification": False,
  "MC notification": False,
  "IPPT booking request": True,
  "enquiry": False,
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

ReportSickConversationState = Enum("ReportSickConversationState", [
  "RANK_NAME",
  "LOCATION",
  "DATE_TIME",
  "REASON",
  "COURSE",
  "INFO",
  "CONFIRM",
])

MCConversationState = Enum("MCConversationState", [
  "RANK_NAME",
  "PERIOD",
  "REASON",
  "COURSE",
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
RequestCallbackType = Enum("RequestCallbackType", [
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
