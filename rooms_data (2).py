# rooms_data.py
# I keep information about the different room types here and provide
# a simple filter_rooms function that I can call from the filter page.
# In this version I read the room information from a JSON file so that
# we can store many physical rooms without hard-coding everything.

import json
import os

from booking_storage import count_confirmed_by_room_type

ROOMS_DB_FILE = "rooms_db.json"


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


def _build_room_types(all_rooms):
    """
    From the full list of physical rooms I build a smaller list that
    only contains one record per room type.

    The rest of the project already expects a ROOMS list with one
    entry per type (Twin, Double, Suite, ...) so I keep that idea
    and simply pick the first room of each type as the "representative".
    """
    result = []
    seen_types = []

    for room in all_rooms:
        short_type = str(room.get("short_type", ""))

        if not short_type:
            # If I cannot read the type I simply skip this record.
            continue

        if short_type in seen_types:
            # I already have a representative for this type.
            continue

        # I copy the fields I care about into a new dict.
        # This keeps the data shape very close to the original ROOMS list.
        room_type = {
            "code": room.get("code", ""),
            "name": room.get("name", ""),
            "short_type": short_type,
            "price": float(room.get("price", 0.0)),
            "floor": room.get("floor", ""),
            "pet_friendly": bool(room.get("pet_friendly", False)),
            "smoking": bool(room.get("smoking", False)),
            "breakfast_available": bool(room.get("breakfast_available", False)),
            "shuttle_available": bool(room.get("shuttle_available", False)),
        }

        result.append(room_type)
        seen_types.append(short_type)

    return result


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
_ALL_ROOMS = _load_rooms_db()

# ROOMS keeps one example per room type so the UI still shows one row
# per type in the search results.
ROOMS = _build_room_types(_ALL_ROOMS)

# ROOM_CAPACITY tells me how many physical rooms each type has.
ROOM_CAPACITY = _build_capacity(_ALL_ROOMS)

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

    For now I do not use stay_info here, because member C owns F3.
    I only use JSON and the ROOM_CAPACITY data to avoid overbooking
    a room type.
    """
    results = []

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

        # Simple capacity check based on existing JSON bookings.
        current_count = count_confirmed_by_room_type(room["short_type"])
        capacity = ROOM_CAPACITY.get(room["short_type"], 100)
        if current_count >= capacity:
            match = False

        if match:
            results.append(room)

    return results
