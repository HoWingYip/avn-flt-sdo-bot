from copy import deepcopy
from datetime import datetime, date

from utility.constants import FIELD_NAME_MAPPINGS

def summarize_request(request_type, fields):
  def stringify_field(value):
    if isinstance(value, datetime):
      return datetime.strftime(value, "%d%m%y %H%MH")
    elif isinstance(value, date):
      return datetime.strftime(value, "%d%m%y")
    elif isinstance(value, list):
      return "\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(value))
    else:
      return str(value)

  return "\n".join(
    f"{FIELD_NAME_MAPPINGS[request_type][field_name]}: "
    f"{stringify_field(fields[field_name])}" for field_name in fields
  )
