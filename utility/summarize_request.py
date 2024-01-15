from copy import deepcopy
from datetime import datetime

from utility.constants import FIELD_NAME_MAPPINGS

def summarize_request(request_type, fields):
  fields = deepcopy(fields)
  if "time" in fields:
    fields["time"] = datetime.strftime(fields["time"], "%d%m%y %H%MH")

  return "\n".join(
    f"{FIELD_NAME_MAPPINGS[request_type][field_name]}: {fields[field_name]}" for field_name in fields
  )
