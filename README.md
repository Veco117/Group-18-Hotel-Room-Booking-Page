# TVXK Hotel Booking System - Group 18

## Project Overview
The **TVXK Hotel Booking System** is a desktop GUI application built with Python and Tkinter. It provides a comprehensive interface for users to browse hotel rooms, check availability, make reservations, and manage existing bookings. The system uses local JSON storage to persist booking and room data.

## Features

### New Booking
* **Date Selection:** Interactive calendar widget for selecting check-in and check-out dates.
* **Room Filtering:** Filter rooms by type (Twin, Double, Suite), floor preference, pet-friendliness, smoking policies, and amenities (Breakfast, Shuttle).
* **Search Results:** View available rooms with calculated total prices based on the length of stay.
* **Guest Details:** Collects guest information with validation logic (e.g., adult/child count rules).
* **Payment Simulation:** detailed payment form with validation for card details.
* **Confirmation:** Generates a unique confirmation code and saves the booking.

### Manage Booking
* **Login:** Access bookings using a combination of Last Name and Confirmation Code.
* **View Details:** Display full reservation details including payment breakdown.
* **Modify Booking:** Update contact information (email, phone), guest counts, and add-on services.
* **Cancel Booking:** Cancel an active reservation.

## Prerequisites

* **Python:** Version 3.10 or higher.

### Required Libraries
This project relies on the following external libraries:
* **Pillow (PIL):** For image processing and UI rendering.
* **tkcalendar:** For the date picker widget.

## Installation

1.  **Download the Source Code**
    Ensure all python files (`.py`) and the `icon/` folder are in the same directory.

2.  **Install Dependencies**
    Run the following command in your terminal:
    ```bash
    pip install pillow tkcalendar
    ```

3.  **Run the Application**
    Start the application by running the main script:
    ```bash
    python hotel_booking_app.py
    ```

## Project Structure

* `hotel_booking_app.py`: Main entry point containing the navigation and main frame setup.
* `booking_flow_*.py`: Modules handling the booking process (Dates, Search, Guest Info, Payment).
* `manage_booking_flow.py`: Modules for viewing and managing existing bookings.
* `rooms_data.py` & `booking_storage.py`: Logic for data handling and JSON file operations.
* `rooms_db.json`: Database of available rooms.
* `bookings.json`: Storage for user reservations.

## Credits
* **Images:** All background images and icons are sourced from [Canva](https://www.canva.com/).
