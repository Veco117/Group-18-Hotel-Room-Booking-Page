# rooms_data.py
# I keep information about the different room types here and provide
# a simple filter_rooms function that I can call from the filter page.

from booking_storage import count_confirmed_by_room_type

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
        "shuttle_available": True,
    },
    {
        "code": "SEAVIEW_TWIN",
        "name": "Seaview Twin Room",
        "short_type": "Twin",
        "price": 200.0,
        "floor": "High",
        "pet_friendly": False,
        "smoking": False,
        "breakfast_available": True,
        "shuttle_available": True,
    },
    {
        "code": "CLASSIC_DOUBLE",
        "name": "Classic Double Room",
        "short_type": "Double",
        "price": 220.0,
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

# This is a very rough idea of how many rooms we have in each type.
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
    - nights

    For now I do not use guests info here, because member C owns F3.
    I only use JSON to avoid overbooking a room type.
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
            if room["floor"] != floor_pref:
                match = False

        if filters_dict.get("Pet"):
            if not room["pet_friendly"]:
                match = False

        if filters_dict.get("Smoke"):
            if not room["smoking"]:
                match = False

        if filters_dict.get("Shuttle"):
            if not room["shuttle_available"]:
                match = False

        if filters_dict.get("Breakfast"):
            if not room["breakfast_available"]:
                match = False

        price = float(room["price"])
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
