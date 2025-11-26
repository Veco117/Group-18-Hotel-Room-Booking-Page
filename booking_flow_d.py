# booking_flow_d.py
# F8: Payment Page - Process payment with validation
# F9: Confirmation Page - Generate confirmation code and save to JSON

import tkinter as tk
from tkinter import messagebox
import re
import os
from booking_storage import add_booking

try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def create_round_rect_canvas(canvas, x1, y1, x2, y2, radius=20, tags=None,
                             **kwargs):
    """
    Draw rounded rectangle using Canvas's create_polygon
    This is a native Canvas method, doesn't require Pillow
    """
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    if tags:
        kwargs['tags'] = tags
    return canvas.create_polygon(points, smooth=True, **kwargs)


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

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "payment_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo,
                                         anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        # Center position
        center_x = 450

        # Title: "Payment Information" (dark blue text, directly on background)
        self.canvas.create_text(
            center_x, 90,
            text="Payment Information",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="center"
        )

        # Total amount display (drawn on canvas, moved down)
        self.amount_text_id = self.canvas.create_text(
            center_x, 190,
            text="Total Amount: $0.00",
            font=("Arial", 16, "bold"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Info text (drawn on canvas, moved down)
        self.canvas.create_text(
            center_x, 220,
            text="Please enter your payment details to complete the reservation.",
            font=("Arial", 10, "italic"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Payment form elements directly on canvas (no white background, moved down)
        form_y_start = 280
        row_spacing = 50

        # Card Number label
        self.canvas.create_text(
            center_x - 120, form_y_start,
            text="Card Number (16 digits):",
            font=FONT_LABEL,
            fill="#001540",
            anchor="e"
        )
        self.entry_card = tk.Entry(self.canvas, font=FONT_LABEL, width=25,
                                   bg="white")
        self.canvas.create_window(center_x - 90, form_y_start,
                                  window=self.entry_card, anchor="w")

        # CVV label
        self.canvas.create_text(
            center_x - 120, form_y_start + row_spacing,
            text="CVV (3 digits):",
            font=FONT_LABEL,
            fill="#001540",
            anchor="e"
        )
        self.entry_cvv = tk.Entry(self.canvas, font=FONT_LABEL, width=25,
                                  show="*", bg="white")
        self.canvas.create_window(center_x - 90, form_y_start + row_spacing,
                                  window=self.entry_cvv, anchor="w")

        # Expiry Date label
        self.canvas.create_text(
            center_x - 120, form_y_start + row_spacing * 2,
            text="Expiry Date (MM/YY):",
            font=FONT_LABEL,
            fill="#001540",
            anchor="e"
        )
        self.entry_expiry = tk.Entry(self.canvas, font=FONT_LABEL, width=25,
                                     bg="white")
        self.canvas.create_window(center_x - 90,
                                  form_y_start + row_spacing * 2,
                                  window=self.entry_expiry, anchor="w")

        # Cardholder Name label
        self.canvas.create_text(
            center_x - 120, form_y_start + row_spacing * 3,
            text="Cardholder Name:",
            font=FONT_LABEL,
            fill="#001540",
            anchor="e"
        )
        self.entry_cardholder = tk.Entry(self.canvas, font=FONT_LABEL,
                                         width=25, bg="white")
        self.canvas.create_window(center_x - 90,
                                  form_y_start + row_spacing * 3,
                                  window=self.entry_cardholder, anchor="w")

        # Button dimensions (same as other pages)
        btn_width = 200
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 500  # Button Y position

        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2

        # "Back to Summary" button (darker blue background, white text)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height

        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#004aad",  # Blue color
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Back to Summary",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>",
                             lambda e: controller.show_frame("SummaryPage"))
        self.canvas.tag_bind("btn_back", "<Enter>",
                             lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>",
                             lambda e: self.canvas.config(cursor="hand2"))

        # "Complete Payment" button (dark blue background, white text)
        btn_pay_x1 = start_x + btn_width + btn_spacing
        btn_pay_y1 = btn_y - btn_height // 2
        btn_pay_x2 = btn_pay_x1 + btn_width
        btn_pay_y2 = btn_pay_y1 + btn_height

        create_round_rect_canvas(
            self.canvas,
            btn_pay_x1, btn_pay_y1, btn_pay_x2, btn_pay_y2,
            radius=btn_radius,
            fill="#001540",  # Dark blue (same as Continue button)
            outline="",
            tags="btn_pay"
        )
        self.canvas.create_text(
            (btn_pay_x1 + btn_pay_x2) // 2,
            (btn_pay_y1 + btn_pay_y2) // 2,
            text="Complete Payment",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_pay"
        )
        self.canvas.tag_bind("btn_pay", "<Button-1>", lambda e: self.on_pay())
        self.canvas.tag_bind("btn_pay", "<Enter>",
                             lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_pay", "<Leave>",
                             lambda e: self.canvas.config(cursor=""))

        # Refresh amount when page is shown
        self.bind("<<ShowPage>>", self.refresh_amount)

    def refresh_amount(self, event=None):
        """Update the total amount display"""
        total = getattr(self.controller, "total_price", 0.0)
        self.canvas.itemconfig(self.amount_text_id,
                               text=f"Total Amount: ${total:.2f}")

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

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "book_comfirm_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo,
                                         anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        center_x = 450

        # Title: "Booking Confirmed!" (directly on background)
        self.canvas.create_text(
            center_x, 200,
            text="Booking Confirmed!",
            font=("Arial", 24, "bold"),
            fill="#000636",  # Dark blue
            anchor="center"
        )

        # Confirmation message (directly on background)
        self.message_text_id = self.canvas.create_text(
            center_x, 262,
            text="Your TVXK Hotel reservation has been successfully created!",
            font=("Arial", 13),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Confirmation code display (white background frame for readability)
        self.code_frame = tk.Frame(self.canvas, bg="white", relief="ridge",
                                   bd=2)
        self.canvas.create_window(center_x, 350, window=self.code_frame,
                                  anchor="center", width=500, height=120)

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

        # Important message (directly on background)
        self.canvas.create_text(
            center_x, 450,
            text="Please save this confirmation code for future reference.\n"
                 "You can use it to view, modify, or cancel your reservation.",
            font=("Arial", 11, "italic"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Button to return home (using rounded rectangle)
        btn_width = 200
        btn_height = 45
        btn_radius = 10
        btn_y = 540  # Moved down 1cm (40 pixels)

        btn_home_x1 = center_x - btn_width // 2
        btn_home_y1 = btn_y - btn_height // 2
        btn_home_x2 = btn_home_x1 + btn_width
        btn_home_y2 = btn_home_y1 + btn_height

        create_round_rect_canvas(
            self.canvas,
            btn_home_x1, btn_home_y1, btn_home_x2, btn_home_y2,
            radius=btn_radius,
            fill="#53a5b3",  # Teal blue
            outline="",
            tags="btn_home"
        )
        self.canvas.create_text(
            center_x,
            btn_y,
            text="Return to Home",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_home"
        )
        self.canvas.tag_bind("btn_home", "<Button-1>",
                             lambda e: self.return_home())
        self.canvas.tag_bind("btn_home", "<Enter>",
                             lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_home", "<Leave>",
                             lambda e: self.canvas.config(cursor="hand2"))

        # Generate confirmation when page is shown
        self.bind("<<ShowPage>>", self.generate_confirmation)

    def generate_confirmation(self, event=None):
        """Generate confirmation code and save booking to JSON"""
        # Collect all booking data
        stay_info = getattr(self.controller, "current_stay", {})
        room = getattr(self.controller, "selected_room", {})
        guest_info = getattr(self.controller, "guest_info", {})
        payment_info = getattr(self.controller, "payment_info", {})
        filters = getattr(self.controller, "current_filter", {})
        total = getattr(self.controller, "total_price", 0.0)

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

            # Ensure the specific room number is saved!
            "room_number": room.get("room_number", "N/A"),

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
                "We look forward to your visit! :)"
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
        if hasattr(self.controller, "guest_info"):
            delattr(self.controller, "guest_info")
        if hasattr(self.controller, "payment_info"):
            delattr(self.controller, "payment_info")
        if hasattr(self.controller, "current_filter"):
            delattr(self.controller, "current_filter")
        if hasattr(self.controller, "total_price"):
            delattr(self.controller, "total_price")

        # Return to welcome page
        self.controller.show_frame("WelcomePage")