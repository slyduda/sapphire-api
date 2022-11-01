import sys
import uuid
import email, smtplib, ssl
from datetime import datetime, timedelta

from typing import Union, Tuple

from caldav import DAVClient
from icalendar import Calendar, Event

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ATTENDEES = [('Sylvester Duda', "me@slyduda.com")]

class User():
    def __init__(self, name:str, username:str, password:str, url:str, calendar:str):
        self.client = DAVClient(url=url, username=username, password=password)
        self.principal = self.client.principal()
        self.calendar = self.principal.calendar(name=calendar)
        self.vcal = self.principal.get_vcal_address()
        self.email = username
        self.name = name


def format_header_address(address=Union[str, tuple]):
    if type(address) is tuple:
        return f"{address[0]} <{address[1]}>"
    return address


def create_message(sender:Union[str, Tuple], receiver:[str, Tuple], plain=str, html=str, ical=None) -> MIMEMultipart:
    message = MIMEMultipart()
    message["From"] = format_header_address(sender)
    message["To"] = format_header_address(receiver)
    message["Subject"] = "Meeting Scheduled"
    message.attach(MIMEText(plain, "plain"))
    message.attach(MIMEText(html, "html"))
    
    if ical:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(ical)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment; filename= event.ics",
        )
        message.attach(part)

    return message


def create_meeting(start:datetime, end:datetime, summary:str, location:str, description:str) -> Calendar:
    caldata = Calendar()
    caldata.add("prodid", "-//tobixen//python-icalendar//en_DK")
    caldata.add("version", "2.0")

    event = Event()
    event.add("dtstamp", datetime.now())
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("uid", uuid.uuid4())
    event.add("summary", summary)
    event.add("location", location)
    event.add("description", description)

    caldata.add_component(event)

    return caldata
    

def save_event(host:str, port:int, username:str, password:str, caluser:User, caldata:Calendar, attendees:list[Union[str, Tuple]], body:str, html:str):
    
    # Connect to SMTP
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(host, port)
        server.starttls(context=context)
        server.login(username, password)
        
        print('Saving to User\'s calendar')
        caluser.calendar.save_with_invites(caldata, attendees=[caluser.vcal, *attendees])
        
        print('Sending out invites to Attendees')
        for attendee in attendees:
            message = create_message((caluser.name, caluser.email), attendee, body, html, ical=caldata.to_ical()).as_string()
            if type(attendee) is tuple:
                attendee = attendee[1]
            server.sendmail(caluser.email, attendee, message)

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        print('Closing SMTP connection')
        server.quit()

    print('Closing CalDav Client Connection')
    caluser.client.close()