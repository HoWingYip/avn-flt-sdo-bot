from inspect import cleandoc
from enum import Enum

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /rso - Request to report sick outside
  /phonebook - List important phone numbers
  /help - Display this list of commands
""")

bcp_states = Enum("bcp", ["RANK_NAME", "DATE_TIME", "PURPOSE", "ADDITIONAL_INFO"])
rso_states = Enum("rso", ["LOCATION", "DATE_TIME", "REASON", "ADDITIONAL_INFO"])
