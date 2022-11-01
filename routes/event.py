import uuid

from quart import request, jsonify
from quart.blueprints import Blueprint

from datetime import datetime, timedelta

from extensions.mail import create_meeting, save_event, User

event = Blueprint('event', __name__)

# Create all of the event information
EVENT_NAME = "Meeting with Sylvester Duda"
EVENT_LOCATION = f'https://meet.jit.si/{uuid.uuid4()}'
EVENT_CANCELLATION = "https://api.slyduda.com/v1/cancellation/serialized-payload"
EVENT_NOTES = f"""\
Event Name: {EVENT_NAME}

Location: {EVENT_LOCATION}

Need to make changes to this event?
Cancel: {EVENT_CANCELLATION}  (Does not work right now)

Powered by slyduda.com
"""

BODY = 'This is an email with attachment sent from Python\n\n' + EVENT_NOTES 
HTML = """\
"""

@event.route('/event', methods=['POST'])
async def create_event():
    data = await request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    date = data.get('date')
    note = data.get('note')
    
    # Validate date
    start =  datetime.fromtimestamp(date / 1000.0)
    end = start + timedelta(min=15)

    # Make the calendar data
    caldata = create_meeting(date, end, EVENT_NAME, EVENT_LOCATION, EVENT_NOTES)
    # Make the User
    caluser = User(name=CALDAV_NAME, username=CALDAV_USERNAME, password=CALDAV_PASSWORD, url=CALDAV_URL, calendar=CALDAV_CALENDAR)

    save_event(
        host=current_app.config.get('SERVER_HOST'),
        port=current_app.config.get('SERVER_PORT'),
        username=current_app.config.get('SERVER_USERNAME'),
        password=current_app.config.get('SERVER_PASSWORD'),
        caluser=caluser,
        caldata=caldata,
        attendees=(name, email),
        body=BODY,
        html=HTML,
    )

    return jsonify({'message': 'Event scheduled.'}), 200