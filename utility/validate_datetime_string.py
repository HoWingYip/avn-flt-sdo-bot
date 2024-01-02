from datetime import datetime

def validate_datetime_string(datetime_string, allow_before_now=False):
  if not allow_before_now and datetime.now() > datetime.strptime(datetime_string, "%d%m%y %H%MH"):
    raise ValueError
  
  date, time = datetime_string.split(" ")
  return date, time[:-1] # remove "H" from end of time
