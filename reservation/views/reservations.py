import datetime

from flask import Blueprint, jsonify, request, make_response, abort
from sqlalchemy.exc import SQLAlchemyError

from reservation.models import Reservation, Person, db

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')


@reservations.route('', methods={'GET'})
def get_all_reservations():
    """ Retrieves all reservations available in the service.

    Only an abstract view of each reservation is provided by this call for efficiency.

    :return: application/JSON response  [{ "id" : <id>, "name" : <name>, "size" : <size>, "time" : <ISO time>}, ...]
    """
    try:
        reservation_list = Reservation.query.all()
    except SQLAlchemyError:
        return abort(500, "Unable to complete the request. Try again later.")

    response = [{
        'id': res.id,
        'name': res.client.name,
        'size': res.party_size,
        'time': res.start_datetime.isoformat()
    } for res in reservation_list]

    return make_response(jsonify(response), 200)


@reservations.route('/<int:reservation_id>', methods={'GET'})
def get_reservation_by_id(reservation_id):
    """ Retrieves the details of a specific reservation.

    :param reservation_id: The reservation id
    :return: application/JSON response with full details.
    """
    try:
        reservation = Reservation.query.get(reservation_id)
    except SQLAlchemyError:
        return abort(500, 'Unable to complete the request. Try again later.')

    if not reservation:
        abort(404, 'This reservation id does not exists.')

    response = {
        'id': reservation.id,
        'name': reservation.client.name,
        'email': reservation.client.email,
        'size': reservation.party_size,
        'time': reservation.start_datetime.isoformat(),
        'note': reservation.note
    }

    return make_response(jsonify(response), 200)


@reservations.route('', methods={'POST'})
def create_reservation():
    """ Creates a new reservation.

    This handler expects a JSON request body with the following fields: name, email, size, time (in ISO format).
    Optionally a note text field can be given as well.

    :return: application/JSON success or failure message { "error" : <bool>, "msg" : <msg>, "code" : <code> }
    """
    fields_req = ['name', 'email', 'size', 'time']

    body = request.get_json()
    # Validate fields exists and are not empty
    if not body \
            or not all(field in body for field in fields_req) \
            or not all(val for field, val in body.items() if field in fields_req):
        abort(400, f'Required field must not be null or empty. Required: {", ".join(fields_req)}')

    # Validate the date and time
    try:
        start_datetime = datetime.datetime.fromisoformat(body['time'])
    except (ValueError, TypeError):
        return abort(400, 'Invalid date format, use: <date: YYYY-MM-DD>T<time: hh:mm>')

    if start_datetime < datetime.datetime.now():
        return abort(400, 'The reservation must be in the future.')

    # Validate the party size
    try:
        party_size = int(body['size'])
    except ValueError:
        return abort(400, 'Invalid party size format, it must be a valid number.')

    if party_size < 1:
        return abort(400, 'Your party size must be of at least 1.')

    # Load any existing client or create a new one
    client = Person.query.filter(Person.name.ilike(body['name']), Person.email.ilike(body['email'])).first()
    if not client:
        client = Person(name=body['name'], email=body['email'])

    reservation = Reservation(
        client=client,
        start_datetime=start_datetime,
        party_size=party_size,
        note=body['note'] if ('note' in body and body['note']) else ''
    )

    try:
        db.session.add(reservation)
        db.session.commit()
        return make_response(jsonify({
            'error': False,
            'msg': 'Created',
            'code': 201
        }), 201)
    except SQLAlchemyError:
        abort(500, 'Unable to complete your transaction, try again later.')
