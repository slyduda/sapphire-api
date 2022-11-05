from secrets import token_hex

from quart import request, jsonify, current_app
from quart.blueprints import Blueprint

from datetime import datetime, timedelta, time
from pytz import timezone

from extensions.mail import create_meeting, save_event
from extensions.events import User, parse_meeting_block_file, get_all_time_slots, get_available_slots

event = Blueprint('event', __name__)


MEETING_BLOCKS = parse_meeting_block_file('./events.yaml')


@event.route('/events', methods=['GET'])
async def get_events():
    LOCALTZ = timezone('America/Los_Angeles')
    CACHE_START = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    CACHE_DELTA = timedelta(weeks=4)
    CACHE_END_CORRECTION = timedelta(days=1)
    CACHE_END = CACHE_START + CACHE_DELTA + CACHE_END_CORRECTION
    CACHE_INTERVAL = timedelta(days=1)

    caluser = User(
        name=current_app.config.get('SMTP_NAME'), 
        username=current_app.config.get('SMTP_USERNAME'), 
        password=current_app.config.get('SMTP_PASSWORD'), 
        url=current_app.config.get('CALDAV_URL'), 
        calendar=current_app.config.get('CALDAV_CALENDAR')
    )

    # date_dict = caluser.get_event_dict(CACHE_START, CACHE_END) # Future use for better caching with calenders with a lot of blocked dates
    blocked_dts = caluser.get_events(CACHE_START, CACHE_END)

    available_slots = {}
    for block in MEETING_BLOCKS:
        time_slots = get_all_time_slots(block.start, timedelta(seconds=block.duration), timedelta(seconds=block.slot_duration))
        a_slots, u_slots = get_available_slots(time_slots, blocked_dts)
        
        available_slots[block.id] = {
            'id': block.id,
            'duration': block.duration,
            'slot_duration': block.slot_duration,
            'slots': [slot.start_datetime for slot in a_slots]
        }

    return jsonify(available_slots), 200


@event.route('/events', methods=['POST'])
async def create_event():
    LOCALTZ = timezone('America/Los_Angeles')
    CACHE_START = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    CACHE_DELTA = timedelta(weeks=4)
    CACHE_END_CORRECTION = timedelta(days=1)
    CACHE_END = CACHE_START + CACHE_DELTA + CACHE_END_CORRECTION
    CACHE_INTERVAL = timedelta(days=1)
    
    data = await request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    meeting_id = data.get('id')
    date = data.get('date')
    note = data.get('note')
    
    required = [name, email, date]
    if any(x is None for x in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # simple email validation
    # simple name and note length checks (large requests should be filtered by quart)

    # Validate date
    start = datetime.fromtimestamp(date / 1000.0)
    # We can do some simple validation here like making sure it is a legit datetime and not somethign silly
    
    caluser = User(
        name=current_app.config.get('SMTP_NAME'), 
        username=current_app.config.get('SMTP_USERNAME'), 
        password=current_app.config.get('SMTP_PASSWORD'), 
        url=current_app.config.get('CALDAV_URL'), 
        calendar=current_app.config.get('CALDAV_CALENDAR')
    )

    # date_dict = caluser.get_event_dict(CACHE_START, CACHE_END) # Future use for better caching with calenders with a lot of blocked dates
    blocked_dts = caluser.get_events(CACHE_START, CACHE_END)

    available_slots = {}
    # We don't need to get all meeting blocks just the id that matches
    for block in MEETING_BLOCKS:
        time_slots = get_all_time_slots(block.start, timedelta(seconds=block.duration), timedelta(seconds=block.slot_duration))
        a_slots, u_slots = get_available_slots(time_slots, blocked_dts)
        
        available_slots[block.id] = {
            'id': block.id,
            'duration': block.duration,
            'slot_duration': block.slot_duration,
            'slots': [slot.start_datetime for slot in a_slots]
        }
    

    meeting_data = available_slots.get(meeting_id)
    if not meeting_data:
        return jsonify({'error': 'meeting_id_existence'}), 400

    slots = meeting_data.get('slots')
    if not datetime.strftime(start, '%d/%m/%y %H:%M:%S.%f') in [datetime.strftime(slot, '%d/%m/%y %H:%M:%S.%f') for slot in slots]:
        return jsonify({'error': 'meeting_start_existence'}), 200

    # Else continue along with the rest

    event_name = f'{name} and Sylvester Duda'
    # Create all of the event information
    event_location = f'https://meet.jit.si/{token_hex(12)}'
    event_cancellation = "https://api.slyduda.com/v1/cancellation/serialized-payload"
    event_description = f"""\
Event Name: {event_name}

Location: {event_location}

Need to make changes to this event?
Cancel: {event_cancellation}  (Does not work right now)

Powered by slyduda.com
    """

    # Make the calendar data
    caldata = create_meeting(start.astimezone(LOCALTZ), start.astimezone(LOCALTZ) + timedelta(seconds=meeting_data['slot_duration']), event_name, event_location, event_description)
    # Make the User

    BODY = 'This is an email with attachment sent from Python\n\n' + event_description 
    HTML = """\
    """

    save_event(
        host=current_app.config.get('SMTP_HOST'),
        port=current_app.config.get('SMTP_PORT'),
        username=current_app.config.get('SMTP_USERNAME'),
        password=current_app.config.get('SMTP_PASSWORD'),
        caluser=caluser,
        caldata=caldata,
        attendees=[(name, email)],
        body=BODY,
        html=HTML,
    )

    return jsonify({'message': 'Event scheduled.'}), 200