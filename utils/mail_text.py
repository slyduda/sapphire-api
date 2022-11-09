SCHEDULED = {
    'subject': 'Meeting Scheduled',
    'body': """\
Event Name: {event_name}

Location: {location}

Note: {note}

Need to make changes to this event?
Cancel: {cancellation}  (Does not work right now)

Powered by slyduda.com
"""
}

CANCELLATION = {
    'subject': 'Cancellation Confirmed',
    'body': 'Cancelled Event'
}

HOST_NOTICE = {
    'subject': 'New Meeting Scheduled',
    'body': """\
Event Name: {event_name}

Location: {location}

Guest Name: {guest_name}

Guest Email: {guest_email}

Guest Note: {note}

Powered by slyduda.com
"""
}