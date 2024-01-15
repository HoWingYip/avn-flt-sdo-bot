def summarize_request(fields, field_name_mapping):
  return "\n".join(
    f"{field_name_mapping[field_name]}: {fields[field_name]}" for field_name in fields
  )
