from secrets import token_urlsafe
from uuid import UUID
from io import BytesIO

from quart import request, jsonify, current_app, send_file
from quart.blueprints import Blueprint

from datetime import datetime

from extensions.serializer import serializer

from utils.validation import validate_email, validate_telephone
from typing import NamedTuple, TypeVar, Any

from vobject import vCard, vcard


contact = Blueprint('contact', __name__)



@contact.route('/contacts', methods=['POST'])
async def create_contact():
    data = await request.get_json()
    n = data.get('name')
    fn = data.get('fname')
    tel = data.get('tel')
    email = data.get('email')

    required = ['fn']
    if any(x is None for x in required):
        return jsonify({'error': 'Missing required fields'}), 400

    if not tel and not email:
        return jsonify({'error': 'Must pass either an email or a phone number'}), 400

    if not validate_telephone(tel) and not validate_email(email):
        return jsonify({'error': 'Must pass either a valid email or a phone number'}), 400

    card = vCard()
    card.add('fn')
    card.fn.value = fn

    # if validate_telephone(tel):
    #     card.add('tel')
    #     card.tel.value = tel

    if validate_email(email):
        card.add('email')
        card.email.value = email
        card.email.type_param = 'WORK'

    vcard_text = card.serialize()
    buffer = BytesIO()
    buffer.write(bytes(vcard_text, 'utf-8'))
    buffer.seek(0)
    return await send_file(
        buffer,
        as_attachment=True,
        attachment_filename='temp.vcf',
        mimetype='application/octet-stream'
    )