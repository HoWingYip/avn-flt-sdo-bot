from enum import Enum
from telegram import InlineKeyboardButton

def make_callback_data(callback_type: Enum, *data):
  """
  Constructs callback data for a `telegram.InlineKeyboardButton`.
  Throws if length of resulting callback data is not within
  [InlineKeyboardButton.MIN_CALLBACK_DATA, InlineKeyboardButton.MAX_CALLBACK_DATA].
  """
  data = "__".join((str(callback_type), *(str(x) for x in data)))
  if not InlineKeyboardButton.MIN_CALLBACK_DATA <= len(data) <= InlineKeyboardButton.MAX_CALLBACK_DATA:
    raise ValueError
  return data

def match_callback_type(callback_type: Enum):
  return lambda callback_data: callback_data.split("__")[0] == str(callback_type)

