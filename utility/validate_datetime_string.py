from datetime import datetime

def validate_datetime_string(datetime_string, not_before_now=False):
  datetime_obj = datetime.strptime(datetime_string, "%d%m%y %H%MH")
  if not_before_now and datetime.now() > datetime_obj:
    raise ValueError
  
  date, time = datetime_string.split(" ")
  return date, time[:-1] # remove "H" from end of time
