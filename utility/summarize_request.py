def summarize_request(bcp_fields):
  return (
    f"Rank/name: {bcp_fields['rank_name']}\n"
    f"Clearance date and time: {bcp_fields['time'].strftime('%d%m%y %H%MH')}\n"
    f"Purpose: {bcp_fields['purpose']}\n"
    f"Additional info: {bcp_fields['info']}"
  )
