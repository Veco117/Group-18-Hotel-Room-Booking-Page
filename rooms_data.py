# rooms_data.py
# I keep information about the different room types here and provide
# a simple filter_rooms function that I can call from the filter page.
# In this version I read the room information from a JSON file so that
# we can store many physical rooms without hard coding everything.

import json
import os
import sys

from booking_storage import count_confirmed_by_room_type, get_unavailable_room_numbers

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOMS_DB_FILE = os.path.join(BASE_DIR, "rooms_db.json")


def _load_rooms_db():
    """
    I load the raw room records from the JSON file.

    I always try to return a list. When something goes wrong I just
    fall back to an empty list so the rest of the code does not crash.
    """
    rooms = []

    if os.path.exists(ROOMS_DB_FILE):
        try:
            with open(ROOMS_DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            data = []

        if isinstance(data, list):
            for item in data:
                # I only keep items that look like dicts.
                if isinstance(item, dict):
                    rooms.append(item)

    return rooms


def _build_capacity(all_rooms):
    """
    I count how many physical rooms we have for each short_type.

    This information is used together with the bookings JSON file to
    make sure a room type is not overbooked.
    """
    capacity = {}

    for room in all_rooms:
        short_type = str(room.get("short_type", ""))

        if not short_type:
            continue

        if short_type not in capacity:
            capacity[short_type] = 0

        capacity[short_type] = capacity[short_type] + 1

    return capacity


# I load the JSON once when the module is imported.
ROOMS = _load_rooms_db()
# ROOMS now keeps ALL physical rooms (one row per physical room)

# ROOM_CAPACITY tells me how many physical rooms each type has.
ROOM_CAPACITY = _build_capacity(ROOMS)

# As a safety net I keep the old hard-coded data in case the JSON file
# is missing when somebody runs the project.
if not ROOMS:
    ROOMS = [
        {
            "code": "SUNSET_TWIN",
            "name": "Sunset Twin Room",
            "short_type": "Twin",
            "price": 190.0,
            "floor": "Low",
            "pet_friendly": False,
            "smoking": False,
            "breakfast_available": True,
            "shuttle_available": False,
            "room_number": "101"
        },
        {
            "code": "SEAVIEW_TWIN",
            "name": "Seaview Twin Room",
            "short_type": "Twin",
            "price": 210.0,
            "floor": "High",
            "pet_friendly": False,
            "smoking": False,
            "breakfast_available": False,
            "shuttle_available": False,
            "room_number": "201"
        },
        {
            "code": "CLASSIC_DOUBLE",
            "name": "Classic King Room",
            "short_type": "Double",
            "price": 230.0,
            "floor": "Low",
            "pet_friendly": False,
            "smoking": False,
            "breakfast_available": False,
            "shuttle_available": False,
            "room_number": "102"
        },
        {
            "code": "CORAL_SUITE",
            "name": "Coral Family Suite",
            "short_type": "Suite",
            "price": 260.0,
            "floor": "High",
            "pet_friendly": True,
            "smoking": False,
            "breakfast_available": True,
            "shuttle_available": True,
            "room_number": "501"
        },
    ]
    ROOM_CAPACITY = {
        "Twin": 5,
        "Double": 4,
        "Suite": 3,
    }


def filter_rooms(filters_dict, stay_info=None):
    """
    I apply a simple set of filters to the ROOMS list.

    filters_dict keys:
    - Room: list of short_type values like ["Twin", "Suite"]
    - Floor: "Low" or "High" or ""
    - Pet: bool
    - Smoke: bool
    - Shuttle: bool
    - Breakfast: bool
    - MinPrice: string or ""
    - MaxPrice: string or ""

    stay_info is a dict that may contain:
    - check_in
    - check_out
    - nights

    Updated Logic:
    1. Get occupied room numbers.
    2. Iterate through ALL physical rooms.
    3. Skip occupied rooms.
    4. Apply preferences.
    5. Return all matching physical rooms (no aggregation/deduplication),
       so users can see specific available room numbers (e.g., 101, 102).
    """
    results = []

    # 1. Get blocked rooms if dates are known
    blocked_rooms = set()
    if stay_info and "check_in" in stay_info and "check_out" in stay_info:
        blocked_rooms = get_unavailable_room_numbers(
            stay_info["check_in"],
            stay_info["check_out"]
        )

    # I try to convert the price range into numbers.
    min_price = None
    max_price = None
    if filters_dict.get("MinPrice"):
        try:
            min_price = float(filters_dict["MinPrice"])
        except ValueError:
            min_price = None

    if filters_dict.get("MaxPrice"):
        try:
            max_price = float(filters_dict["MaxPrice"])
        except ValueError:
            max_price = None

    for room in ROOMS:
        # --- Availability Check ---
        # If this specific physical room is booked, skip it.
        if str(room.get("room_number", "")) in blocked_rooms:
            continue

        match = True

        wanted_types = filters_dict.get("Room") or []
        if wanted_types:
            if room["short_type"] not in wanted_types:
                match = False

        floor_pref = filters_dict.get("Floor", "")
        if floor_pref:
            if room.get("floor", "") != floor_pref:
                match = False

        if filters_dict.get("Pet"):
            if not room.get("pet_friendly", False):
                match = False

        if filters_dict.get("Smoke"):
            if not room.get("smoking", False):
                match = False

        if filters_dict.get("Shuttle"):
            if not room.get("shuttle_available", False):
                match = False

        if filters_dict.get("Breakfast"):
            if not room.get("breakfast_available", False):
                match = False

        price = float(room.get("price", 0.0))
        if min_price is not None and price < min_price:
            match = False
        if max_price is not None and price > max_price:
            match = False

        # No need to check generic capacity here because we checked specific availability above.

        if match:
            # Make a copy to modify the name for display purposes
            # showing the room number clearly to the user.
            room_copy = room.copy()
            room_number = room.get("room_number", "N/A")
            room_copy["name"] = f"{room['name']} ({room_number})"
            results.append(room_copy)

    return results