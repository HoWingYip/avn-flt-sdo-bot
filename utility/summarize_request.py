from copy import deepcopy
from datetime import datetime

def summarize_request(fields, field_name_mapping):
  fields = deepcopy(fields)
  if "time" in fields:
    fields["time"] = datetime.strftime(fields["time"], "%d%m%y %H%MH")

  return "\n".join(
    f"{field_name_mapping[field_name]}: {fields[field_name]}" for field_name in fields
  )
