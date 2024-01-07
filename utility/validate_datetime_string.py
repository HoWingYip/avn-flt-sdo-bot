from datetime import datetime, timezone, timedelta
import time

def validate_datetime_string(datetime_string, allow_before_now=False):
  datetime_obj = datetime \
    .strptime(datetime_string, "%d%m%y %H%MH") \
    .replace(tzinfo=timezone(timedelta(hours=8))) # interpret string as Singapore time (IMPORTANT IF DEPLOYED ON CLOUD!)

  if not allow_before_now and datetime_obj.timestamp() < time.time():
    raise ValueError("datetime represented by input string is before now")

  return datetime_obj
