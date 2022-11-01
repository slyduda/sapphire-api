from secrets import token_hex

from quart import request, jsonify, current_app
from quart.blueprints import Blueprint

from datetime import datetime, timedelta

from extensions.mail import create_meeting, save_event, User

event = Blueprint('event', __name__)


@event.route('/event', methods=['POST'])
async def create_event():
    data = await request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    date = data.get('date')
    note = data.get('note')
    
    required = [name, email, date]
    if any(x is None for x in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # simple email validation
    # simple name and note length checks (large requests should be filtered by quart)

    # Validate date
    start = datetime.fromtimestamp(date / 1000.0)
    # If start is not after return error
    # If start is not within the expected meeting time return error
    end = start + timedelta(minutes=15)
    # If start to end overlaps any other meetings return error
    
    caluser = User(
        name=current_app.config.get('SMTP_NAME'), 
        username=current_app.config.get('SMTP_USERNAME'), 
        password=current_app.config.get('SMTP_PASSWORD'), 
        url=current_app.config.get('CALDAV_URL'), 
        calendar=current_app.config.get('CALDAV_CALENDAR')
    )

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
    caldata = create_meeting(start, end, event_name, event_location, event_description)
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