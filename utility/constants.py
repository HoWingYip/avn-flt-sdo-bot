from inspect import cleandoc
from enum import Enum

HELP_MESSAGE = cleandoc("""
  List of commands:
  /bcp - Request Base Command Post Clearance
  /rso - Request to report sick outside
  /phonebook - List important phone numbers
  /help - Display this list of commands
""")

bcp_states = Enum("bcp", ["RANK_NAME", "DATE_TIME", "PURPOSE", "INFO", "CONFIRM"])
rso_states = Enum("rso", ["RANK_NAME", "LOCATION", "DATE_TIME", "REASON", "INFO", "CONFIRM"])
