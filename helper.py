import time, datetime

def datetime_to_timestamp(d, date_format = "%Y-%m-%d"):
  return int(time.mktime(datetime.datetime.strptime(d, date_format).timetuple()))

def timestamp_to_datetime(ts):
  return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')  

