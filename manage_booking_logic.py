# manage_booking_logic.py
# This small file is my helper for the "Manage my booking" feature (F12).
# I keep all the data work here so the Tkinter page can stay a bit cleaner.

import booking_storage
from rooms_data import ROOMS


def get_booking(last_name, code):
    """I look up a booking by last name and confirmation code."""
    if not last_name or not code:
        return None
    # I delegate the real work to my storage module.
    booking = booking_storage.find_booking_by_code(last_name, code)
    return booking


def _get_price_for_room(room_type):
    """I find the nightly price for a given room type using the ROOMS list."""
    price = 0.0
    for room in ROOMS:
        short = str(room.get("short_type", ""))
        if short.lower() == str(room_type).lower():
            try:
                price = float(room.get("price", 0))
            except (TypeError, ValueError):
                price = 0.0
            break
    return price


def _calculate_total(room_type, nights):
    """I calculate a simple total price based on room type and nights."""
    try:
        nights_int = int(nights)
    except (TypeError, ValueError):
        nights_int = 1
    nightly = _get_price_for_room(room_type)
    total = nightly * nights_int
    return total


def apply_changes(last_name, code, new_check_in, new_nights):
    """I update the booking with a new date and/or new number of nights.

    I return (True, updated_booking) when it works and (False, None) when it fails.
    """
    # First I read the current booking so I know the old values.
    booking = booking_storage.find_booking_by_code(last_name, code)
    if not booking:
        return False, None

    changes = {}

    # I only update the date if the user typed something.
    if new_check_in:
        changes["check_in"] = new_check_in.strip()

    # For nights I also accept empty string which means keep old value.
    nights_value = booking.get("nights", 1)
    if new_nights:
        try:
            nights_value = int(new_nights)
        except ValueError:
            # If the user types something that is not a number I just keep old value.
            nights_value = booking.get("nights", 1)
    changes["nights"] = nights_value

    # Whenever nights change I recalculate the total price as well.
    room_type = booking.get("room_type", "")
    changes["total_price"] = _calculate_total(room_type, nights_value)

    ok = booking_storage.update_booking(last_name, code, changes)
    if not ok:
        return False, None

    # I load the booking again so I can show the updated version.
    updated = booking_storage.find_booking_by_code(last_name, code)
    return True, updated


def cancel_booking(last_name, code):
    """I cancel a booking by flipping its status to 'Cancelled'."""
    return booking_storage.cancel_booking(last_name, code)
