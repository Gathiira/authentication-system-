from datetime import datetime
from datetime import timedelta
from dateutil import parser
import time


def get_current_timestamp():
    return datetime.now()


def add_time_to_date(timetype, systime, length):
    timetype = str(timetype)
    if timetype == 'seconds':
        new_time = systime + timedelta(seconds=length)
        return new_time


def check_date_expiry(current_date, end_date):
    new_current_date = parser.parse(current_date)
    new_end_date = parser.parse(end_date)

    if new_current_date > new_end_date:
        return True
    return False


def convert_to_timestamp(input_date):
    date_time_obj = datetime.strptime(input_date, '%Y-%m-%d %H:%M:%S')
    _tuple = date_time_obj.timetuple()
    tuple_x = time.mktime(_tuple)
    return tuple_x
