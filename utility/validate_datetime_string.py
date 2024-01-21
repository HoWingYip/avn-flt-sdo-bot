from datetime import datetime, timezone, timedelta
import time

def validate_datetime_string(datetime_string, format, allow_before_now=False):
  datetime_obj = datetime \
    .strptime(datetime_string, format) \
    .replace(tzinfo=timezone(timedelta(hours=8))) # interpret string as Singapore time (IMPORTANT IF DEPLOYED ON CLOUD!)

  if not allow_before_now and datetime_obj.timestamp() < time.time():
    raise ValueError("datetime represented by input string is before now")

  return datetime_obj

def validate_date_string(date_string, format, allow_before_today=False):
  date_obj = datetime \
    .strptime(date_string, format) \
    .replace(tzinfo=timezone(timedelta(hours=8))) \
    .date()
  
  date_in_singapore = datetime \
    .fromtimestamp(time.time(), tz=timezone(timedelta(hours=8))) \
    .date()

  if not allow_before_today and date_obj < date_in_singapore:
    raise ValueError("date represented by input string is before today")
  
  return date_obj
