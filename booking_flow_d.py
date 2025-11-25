# booking_flow_d.py
# F8: Payment Page - Process payment with validation
# F9: Confirmation Page - Generate confirmation code and save to JSON

import tkinter as tk
from tkinter import messagebox
import re
from booking_storage import add_booking

BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")

PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"


class PaymentPage(tk.Frame):
    """
    F8: Payment Page
    Collect payment information: card number (16 digits), CVV (3 digits), expiry date
    Validate all fields before processing
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(self, text="Payment Information", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(20, 10))

        # Total amount display
        self.amount_label = tk.Label(
            self,
            text="Total Amount: $0.00",
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg="#2F80ED",
        )
        self.amount_label.pack(pady=(0, 20))

        info = tk.Label(
            self,
            text="Please enter your payment details to complete the reservation.",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
        )
        info.pack(pady=(0, 20))

        # Payment form
        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=20)

        # Card Number
        tk.Label(form, text="Card Number (16 digits):", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=0, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_card = tk.Entry(form, font=FONT_LABEL, width=25)
        self.entry_card.grid(row=0, column=1, padx=10, pady=12)

        # CVV
        tk.Label(form, text="CVV (3 digits):", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=1, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_cvv = tk.Entry(form, font=FONT_LABEL, width=25, show="*")
        self.entry_cvv.grid(row=1, column=1, padx=10, pady=12)

        # Expiry Date
        tk.Label(form, text="Expiry Date (MM/YY):", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=2, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_expiry = tk.Entry(form, font=FONT_LABEL, width=25)
        self.entry_expiry.grid(row=2, column=1, padx=10, pady=12)

        # Cardholder Name
        tk.Label(form, text="Cardholder Name:", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=3, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_cardholder = tk.Entry(form, font=FONT_LABEL, width=25)
        self.entry_cardholder.grid(row=3, column=1, padx=10, pady=12)

        # Validation hints
        hints = tk.Label(
            self,
            text="* Card number must be 16 digits\n* CVV must be 3 digits\n* Expiry date format: MM/YY (e.g., 12/25)\n* All fields must contain only numbers (except cardholder name)",
            font=("Arial", 9, "italic"),
            bg=BG_COLOR,
            fg="#666666",
            justify="left",
        )
        hints.pack(pady=10)

        # Buttons
        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=30)

        btn_back = tk.Button(
            buttons,
            text="Back to Summary",
            font=("Arial", 12),
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=15,
            command=lambda: controller.show_frame("SummaryPage"),
        )
        btn_back.pack(side="left", padx=10)

        btn_pay = tk.Button(
            buttons,
            text="Complete Payment",
            font=FONT_BUTTON,
            bg="#28a745",  # Green for payment button
            fg="white",
            width=18,
            command=self.on_pay,
        )
        btn_pay.pack(side="left", padx=10)

        # Refresh amount when page is shown
        self.bind("<<ShowPage>>", self.refresh_amount)

    def refresh_amount(self, event=None):
        """Update the total amount display"""
        total = getattr(self.controller, "booking_total", 0.0)
        self.amount_label.config(text=f"Total Amount: ${total:.2f}")

    def validate_card_number(self, card):
        """Validate card number: must be 16 digits"""
        card_clean = card.replace(" ", "").replace("-", "")
        if not card_clean.isdigit():
            return False, "Card number must contain only numbers"
        if len(card_clean) != 16:
            return False, "Card number must be exactly 16 digits"
        return True, ""

    def validate_cvv(self, cvv):
        """Validate CVV: must be 3 digits"""
        if not cvv.isdigit():
            return False, "CVV must contain only numbers"
        if len(cvv) != 3:
            return False, "CVV must be exactly 3 digits"
        return True, ""

    def validate_expiry(self, expiry):
        """Validate expiry date: MM/YY format"""
        pattern = r'^(0[1-9]|1[0-2])\/([0-9]{2})$'
        if not re.match(pattern, expiry):
            return False, "Expiry date must be in MM/YY format (e.g., 12/25)"

        # Extract month and year
        parts = expiry.split("/")
        month = int(parts[0])
        year = int(parts[1]) + 2000  # Convert YY to YYYY

        # Simple validation: year should be >= 2025
        from datetime import date
        today = date.today()
        if year < today.year or (year == today.year and month < today.month):
            return False, "Card has expired"

        return True, ""

    def validate_cardholder(self, name):
        """Validate cardholder name: cannot be empty"""
        if not name or name.strip() == "":
            return False, "Cardholder name cannot be empty"
        return True, ""

    def on_pay(self):
        """Validate payment fields and process payment"""
        card = self.entry_card.get().strip()
        cvv = self.entry_cvv.get().strip()
        expiry = self.entry_expiry.get().strip()
        cardholder = self.entry_cardholder.get().strip()

        # Validate card number
        valid, error = self.validate_card_number(card)
        if not valid:
            messagebox.showerror("Payment Error", error)
            return

        # Validate CVV
        valid, error = self.validate_cvv(cvv)
        if not valid:
            messagebox.showerror("Payment Error", error)
            return

        # Validate expiry
        valid, error = self.validate_expiry(expiry)
        if not valid:
            messagebox.showerror("Payment Error", error)
            return

        # Validate cardholder
        valid, error = self.validate_cardholder(cardholder)
        if not valid:
            messagebox.showerror("Payment Error", error)
            return

        # Save payment info (in real app, this would be encrypted/tokenized)
        self.controller.payment_info = {
            "card_last4": card[-4:],  # Only save last 4 digits
            "cardholder": cardholder,
            "expiry": expiry,
        }

        # Show processing message
        messagebox.showinfo(
            "Processing Payment",
            "Payment is being processed...\nPlease wait."
        )

        # Move to confirmation page
        self.controller.show_frame("ConfirmationPage")


class ConfirmationPage(tk.Frame):
    """
    F9: Confirmation Page
    Generate unique confirmation code using UUID
    Save all booking data to JSON file
    Display confirmation message
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(
            self,
            text="Booking Confirmed!",
            font=("Arial", 24, "bold"),
            bg=BG_COLOR,
            fg="#28a745",  # Green
        )
        title.pack(pady=(30, 20))

        # Success icon (using text)
        success_icon = tk.Label(
            self,
            text="✓",
            font=("Arial", 80, "bold"),
            bg=BG_COLOR,
            fg="#28a745",
        )
        success_icon.pack(pady=(10, 20))

        # Confirmation message
        self.message_label = tk.Label(
            self,
            text="Your TVXK Hotel reservation has been successfully created!",
            font=("Arial", 13),
            bg=BG_COLOR,
            fg="#333333",
        )
        self.message_label.pack(pady=(0, 20))

        # Confirmation code display
        self.code_frame = tk.Frame(self, bg="white", relief="ridge", bd=2)
        self.code_frame.pack(padx=50, pady=20)

        tk.Label(
            self.code_frame,
            text="Your Confirmation Code:",
            font=("Arial", 12),
            bg="white",
        ).pack(padx=20, pady=(15, 5))

        self.code_label = tk.Label(
            self.code_frame,
            text="XXXXXXXX",
            font=("Courier New", 28, "bold"),
            bg="white",
            fg="#2F80ED",
        )
        self.code_label.pack(padx=20, pady=(5, 15))

        # Important message
        important_msg = tk.Label(
            self,
            text="Please save this confirmation code for future reference.\n"
                 "You can use it to view, modify, or cancel your reservation.",
            font=("Arial", 11, "italic"),
            bg=BG_COLOR,
            fg="#666666",
            justify="center",
        )
        important_msg.pack(pady=(10, 30))

        # Button to return home
        btn_home = tk.Button(
            self,
            text="Return to Home",
            font=FONT_BUTTON,
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            width=20,
            command=self.return_home,
        )
        btn_home.pack(pady=20)

        # Generate confirmation when page is shown
        self.bind("<<ShowPage>>", self.generate_confirmation)

    def generate_confirmation(self, event=None):
        """Generate confirmation code and save booking to JSON"""
        # Collect all booking data
        stay_info = getattr(self.controller, "current_stay", {})
        room = getattr(self.controller, "selected_room", {})
        # guests = getattr(self.controller, "guest_selection", {})
        guest_info = getattr(self.controller, "guest_info", {})
        payment_info = getattr(self.controller, "payment_info", {})
        filters = getattr(self.controller, "current_filter", {})
        total = getattr(self.controller, "booking_total", 0.0)

        # Prepare booking data for JSON
        booking_data = {
            "first_name": guest_info.get("first_name", ""),
            "last_name": guest_info.get("last_name", ""),
            "email": guest_info.get("email", ""),
            "phone": guest_info.get("phone", ""),
            "adults": guest_info.get("adults", 1),
            "children": guest_info.get("children", 0),
            "room_type": room.get("short_type", "Unknown"),
            "room_name": room.get("name", "Unknown Room"),
            "check_in": stay_info.get("check_in", ""),
            "check_out": stay_info.get("check_out", ""),
            "nights": stay_info.get("nights", 1),
            "breakfast": filters.get("Breakfast", False),
            "shuttle": filters.get("Shuttle", False),
            "total_price": total,
            "payment_last4": payment_info.get("card_last4", "****"),
            "status": "Confirmed",
        }

        # Generate confirmation code and save to JSON
        try:
            confirmation_code = add_booking(booking_data)
            self.code_label.config(text=confirmation_code)

            # Save to controller for potential later use
            self.controller.last_confirmation_code = confirmation_code

            messagebox.showinfo(
                "Success",
                f"Your booking has been saved!\n\nConfirmation Code: {confirmation_code}\n\n"
                "We are looking forward to see you!:)"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save booking: {str(e)}\nPlease contact support."
            )
            self.code_label.config(text="ERROR")

    def return_home(self):
        """Clear booking data and return to home page"""
        # Clear all booking data from controller
        if hasattr(self.controller, "current_stay"):
            delattr(self.controller, "current_stay")
        if hasattr(self.controller, "selected_room"):
            delattr(self.controller, "selected_room")
        if hasattr(self.controller, "guest_selection"):
            delattr(self.controller, "guest_selection")
        if hasattr(self.controller, "guest_info"):
            delattr(self.controller, "guest_info")
        if hasattr(self.controller, "payment_info"):
            delattr(self.controller, "payment_info")
        if hasattr(self.controller, "current_filter"):
            delattr(self.controller, "current_filter")
        if hasattr(self.controller, "booking_total"):
            delattr(self.controller, "booking_total")

        # Return to welcome page
        self.controller.show_frame("WelcomePage")
