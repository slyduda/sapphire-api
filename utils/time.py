from datetime import datetime, timedelta, time
from datetimerange import DateTimeRange
from pytz import timezone, UTC


# WILL DELETE LATER USED FOR TESTING TIME


LOCALTZ = timezone('America/Los_Angeles')
EVENT_START = time(hour=9, minute=0, second=0, microsecond=0)
EVENT_RANGE = 60
EVENT_SLOT_RANGE = 30

def datetime_range(start, end, delta, tzinfo):
    current = start
    while current < end:
        last = current
        yield current
        current += delta
        #if tzinfo:
            #print(current.astimezone(LOCALTZ))
            #if last != current:
                #print('fixing current!')

def get_all_time_slots(start:time, event_duration:timedelta, slot_duration:timedelta, day_delta_load:int=14):
    all_dts = []
    for i in range(day_delta_load):
        i = i + 1
        now = datetime.now()
        now = now.astimezone(LOCALTZ).replace(hour=start.hour, minute=start.minute, second=start.second, microsecond=start.microsecond).astimezone(UTC)
        print(i)
        dts = [
            DateTimeRange(dt, dt + slot_duration) for dt in 
            datetime_range(
                datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond) + timedelta(days=i), 
                datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond) + timedelta(days=i) + event_duration, 
                slot_duration,
                LOCALTZ
            )]
        all_dts.extend(dts)
    return all_dts

time_slots = get_all_time_slots(EVENT_START, timedelta(minutes=EVENT_RANGE), timedelta(minutes=EVENT_SLOT_RANGE), 7)
print(time_slots)