from dotenv import dotenv_values
from caldav import DAVClient
import yaml

from datetime import datetime, timedelta, time
from datetimerange import DateTimeRange
from pytz import timezone, UTC

from typing import Union, Tuple, List
from collections import OrderedDict

config = dotenv_values("../.env")

LOCALTZ = timezone('America/Los_Angeles')
CACHE_START = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
CACHE_DELTA = timedelta(weeks=4)
CACHE_END_CORRECTION = timedelta(days=1)
CACHE_END = CACHE_START + CACHE_DELTA + CACHE_END_CORRECTION
CACHE_INTERVAL = timedelta(days=1)


class MeetingBlock():
    def __init__(self, id:str, start:time, duration:int, slot_duration:int):
        self.id = id
        self.start = start
        self.duration = duration
        self.slot_duration = slot_duration


def datetime_range(start, end, delta, tzinfo):
    current = start
    while current < end:
        yield current
        current += delta


def convert_datetime_range_to_datetime_range_pairs(arr:[datetime]):
    '''
        Should come presorted
    '''
    datetime_range_pairs = []
    for i in range(len(arr)):
        dt = arr[i]
        if i + 1 >= len(arr): # We are on the last index
            break
        dt_next = arr[i + 1]
        datetime_range_pair = (dt, dt_next)
        datetime_range_pairs.append(datetime_range_pair)

    return datetime_range_pairs


def convert_datetime_range_pair_to_datetime_range_dict(arr:[Tuple]) -> OrderedDict:
    dt_dict = {}
    for a in arr:
        dt_dict[a[0]] = DateTimeRange(a[0], a[1])

    return OrderedDict(sorted(dt_dict.items()))


def get_all_time_slots(start:time, event_duration:timedelta, slot_duration:timedelta, day_delta_load:int=14):
    all_dts = []
    for i in range(day_delta_load):
        i = i + 1
        now = datetime.now() + timedelta(days=i)
        now = now.astimezone(LOCALTZ).replace(hour=start.hour, minute=start.minute, second=start.second, microsecond=start.microsecond).astimezone(UTC)
        dts = [
            DateTimeRange(dt, dt + slot_duration) for dt in 
            datetime_range(
                datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond), 
                datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond) + event_duration, 
                slot_duration,
                LOCALTZ
            )]
        all_dts.extend(dts)
    return all_dts


def get_available_slots(time_slots, blocked_dts) -> Tuple[List[DateTimeRange], List[DateTimeRange]]:
    available_slots = []
    unavailable_slots = []
    for slot in time_slots:
        available = True
        for blocked_dt in blocked_dts:
            if slot.is_intersection(blocked_dt):
                if slot.intersection(blocked_dt).get_timedelta_second() != 0:
                    available = False
                    break
        if not available:
            unavailable_slots.append(slot)
            continue
        else:
            available_slots.append(slot)
    
    return (available_slots, unavailable_slots)


def parse_meeting_block_file(filename:str):
    event_objects = []
    with open(filename, mode="rt", encoding="utf-8") as file:
        events = yaml.safe_load(file)
    
    for event in events:
        key = list(event.keys())[0]

        meeting_info = event[key]
        print(meeting_info)
        st = meeting_info['start']
        start = time(hour=st.get('hour'), minute=st.get('minute'), second=st.get('second'))
        duration = meeting_info['duration']
        slot_duration = meeting_info['slot_duration']
        print(slot_duration)

        event_objects.append( MeetingBlock(key, start, duration, slot_duration) )

    return event_objects


class User():
    def __init__(self, name:str, username:str, password:str, url:str, calendar:str):
        self.client = DAVClient(url=url, username=username, password=password)
        self.principal = self.client.principal()
        self.calendar = self.principal.calendar(name=calendar)
        self.vcal = self.principal.get_vcal_address()
        self.email = username
        self.name = name
    
    def get_events(self, start:datetime, end:datetime):
        try:
            events = self.calendar.date_search(
                start=start, end=end, expand=True
            )
        except:
            print('Your CalDav provider does not support expanded search')
            events = self.calendar.date_search(
                start=start, end=end, expand=False
            )

        # Would love to find an implicit conversion from date to datetime with tz
        event_datetime_ranges = []
        for event in events:
            dt_start = event.vobject_instance.vevent.dtstart.value
            dt_end = event.vobject_instance.vevent.dtend.value

            
            dt_start_min = datetime.combine(datetime(
                year=dt_start.year, 
                month=dt_start.month, 
                day=dt_start.day,
            ), datetime.min.time())
            dt_end_min = datetime.combine(datetime(
                year=dt_end.year, 
                month=dt_end.month, 
                day=dt_end.day,
            ), datetime.min.time())

            dt_start = dt_start.replace(tzinfo=None) if isinstance(dt_start, datetime) else datetime.combine(dt_start, datetime.min.time()) - dt_start_min.astimezone(LOCALTZ).utcoffset()
            dt_end = dt_end.replace(tzinfo=None) if isinstance(dt_end, datetime) else datetime.combine(dt_end, datetime.min.time()) - dt_end_min.astimezone(LOCALTZ).utcoffset()

            event_datetime_ranges.append(DateTimeRange(dt_start, dt_end))

        return event_datetime_ranges

    # NEED TO FIX THE GET_EVENT_DICT LOCAL REFS
    def get_event_dict(self, start:datetime, end:datetime):
        try:
            events = self.calendar.date_search(
                start=start, end=end, expand=True
            )
        except:
            print('Your CalDav provider does not support expanded search')
            events = self.calendar.date_search(
                start=start, end=end, expand=False
            )

        # Would love to find an implicit conversion from date to datetime with tz
        event_datetime_ranges = []
        for event in events:
            dt_start = event.vobject_instance.vevent.dtstart.value
            dt_end = event.vobject_instance.vevent.dtend.value

            
            dt_start_min = datetime.combine(datetime(
                year=dt_start.year, 
                month=dt_start.month, 
                day=dt_start.day,
            ), datetime.min.time())
            dt_end_min = datetime.combine(datetime(
                year=dt_end.year, 
                month=dt_end.month, 
                day=dt_end.day,
            ), datetime.min.time())

            dt_start = dt_start.replace(tzinfo=None) if isinstance(dt_start, datetime) else datetime.combine(dt_start, datetime.min.time()) - dt_start_min.astimezone(LOCALTZ).utcoffset()
            dt_end = dt_end.replace(tzinfo=None) if isinstance(dt_end, datetime) else datetime.combine(dt_end, datetime.min.time()) - dt_end_min.astimezone(LOCALTZ).utcoffset()

            event_datetime_ranges.append(DateTimeRange(dt_start, dt_end))

        dts = [dt for dt in datetime_range(CACHE_START, CACHE_END, CACHE_INTERVAL)]
        dt_pairs = convert_datetime_range_to_datetime_range_pairs(dts)
        dt_ordered_dict = convert_datetime_range_pair_to_datetime_range_dict(dt_pairs)

        # EXPONENTIAL TERRITORY
        for key, value in dt_ordered_dict.items():
            relevant_events = []
            for blocked_range in event_datetime_ranges:
                if blocked_range.is_intersection(value):
                    if blocked_range.intersection(value).get_timedelta_second() != 0:
                        relevant_events.append(blocked_range)
            dt_ordered_dict[key] = relevant_events

        return dt_ordered_dict
