# booking_storage.py
# This is my small helper module for saving and loading bookings.
# I am using a plain JSON file because it matches what we did in class.

import json
import os
import uuid
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "bookings.json")


def load_bookings():
    """I load all bookings from the JSON file and always return a list."""
    if not os.path.exists(DB_FILE):
        return []

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # If something is wrong with the file I prefer to start with an empty list.
        return []

    if isinstance(data, list):
        return data
    else:
        return []


def save_bookings(bookings):
    """I save the full list of bookings back into the JSON file."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2)


def create_confirmation_code():
    """I create a short confirmation code based on uuid."""
    raw = str(uuid.uuid4())
    code = raw.split("-")[0].upper()
    return code


def add_booking(booking_data):
    """
    I add a new booking to the list and return the confirmation code.

    booking_data is expected to be a simple dict with keys like:
    first_name, last_name, email, phone, room_type, check_in, nights,
    breakfast, total_price, status, room_number ...
    """
    bookings = load_bookings()
    code = create_confirmation_code()
    booking_data["confirmation_code"] = code
    # I make sure there are some basic fields so other parts do not crash.
    booking_data.setdefault("status", "Confirmed")
    booking_data.setdefault("created_at", date.today().isoformat())
    bookings.append(booking_data)
    save_bookings(bookings)
    return code


def find_booking_by_code(last_name, code):
    """I find a booking using last name and confirmation code."""
    bookings = load_bookings()
    for booking in bookings:
        ln = str(booking.get("last_name", ""))
        stored_code = str(booking.get("confirmation_code", ""))
        if ln.lower() == last_name.lower() and stored_code.upper() == code.upper():
            return booking
    return None


def update_booking(last_name, code, new_fields):
    """
    I update an existing booking with the values from new_fields.

    I return True when something was updated and False otherwise.
    """
    bookings = load_bookings()
    updated = False

    for booking in bookings:
        ln = str(booking.get("last_name", ""))
        stored_code = str(booking.get("confirmation_code", ""))
        if ln.lower() == last_name.lower() and stored_code.upper() == code.upper():
            for key, value in new_fields.items():
                booking[key] = value
            updated = True

    if updated:
        save_bookings(bookings)
    return updated


def cancel_booking(last_name, code):
    """
    I mark a booking as cancelled.

    For this project I do not remove the record completely.
    Instead I flip the status to 'Cancelled' and save everything again.
    """
    return update_booking(last_name, code, {"status": "Cancelled"})


def count_confirmed_by_room_type(room_type):
    """
    I count how many confirmed bookings there are for a specific room_type.
    This is a small helper I can use when I want to know if a room type
    is already fully booked.
    """
    bookings = load_bookings()
    count = 0
    for booking in bookings:
        b_type = str(booking.get("room_type", ""))
        status = booking.get("status", "Confirmed")
        if b_type == room_type and status == "Confirmed":
            count += 1
    return count


def get_unavailable_room_numbers(check_in_str, check_out_str):
    """
    I check all bookings to find which room numbers are occupied
    during the requested dates.
    I return a set of room_number strings.
    """
    unavailable = set()
    bookings = load_bookings()

    try:
        req_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        req_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
    except ValueError:
        return unavailable

    for b in bookings:
        # 1. Ignore cancelled bookings
        if b.get("status") == "Cancelled":
            continue

        # 2. Check if booking has a room number
        r_num = b.get("room_number")
        if not r_num:
            continue

        # 3. Check date overlap
        # Parse booking dates
        try:
            b_in = datetime.strptime(b.get("check_in", ""), "%Y-%m-%d").date()
            b_out = datetime.strptime(b.get("check_out", ""),
                                      "%Y-%m-%d").date()
        except ValueError:
            continue

        # Overlap Logic: (StartA < EndB) and (EndA > StartB)
        # This assumes checkout date is the day you leave (room becomes free).
        if req_in < b_out and req_out > b_in:
            unavailable.add(str(r_num))

    return unavailable