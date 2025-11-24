# manage_booking_flow.py
# F12: Modify Booking - Allow users to modify existing bookings
# F13: Cancel Booking - Allow users to cancel bookings

import tkinter as tk
from tkinter import ttk, messagebox
from booking_storage import find_booking_by_code, update_booking, cancel_booking

BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")

PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"


class ViewBookingPage(tk.Frame):
    """
    Display booking details after search
    Provide options to modify or cancel
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(self, text="Your Booking Details", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(20, 10))

        info = tk.Label(
            self,
            text="Review your booking information below.",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
        )
        info.pack(pady=(0, 20))

        # Details container
        details_container = tk.Frame(self, bg="white", relief="ridge", bd=2)
        details_container.pack(padx=40, pady=20, fill="both", expand=True)

        # Details text area
        self.details_text = tk.Text(
            details_container,
            font=("Courier New", 10),
            bg="white",
            wrap="word",
            height=16,
            state="disabled",
        )
        self.details_text.pack(padx=20, pady=20, fill="both", expand=True)

        # Buttons
        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=20)

        btn_back = tk.Button(
            buttons,
            text="Back to Search",
            font=("Arial", 12),
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=15,
            command=lambda: controller.show_frame("ManageBookingPage"),
        )
        btn_back.pack(side="left", padx=10)

        btn_modify = tk.Button(
            buttons,
            text="Modify Booking",
            font=FONT_BUTTON,
            bg="#FFA500",  # Orange
            fg="white",
            width=15,
            command=lambda: controller.show_frame("ModifyBookingPage"),
        )
        btn_modify.pack(side="left", padx=10)

        btn_cancel = tk.Button(
            buttons,
            text="Cancel Booking",
            font=FONT_BUTTON,
            bg="#DC3545",  # Red
            fg="white",
            width=15,
            command=lambda: controller.show_frame("CancelBookingPage"),
        )
        btn_cancel.pack(side="left", padx=10)

        # Refresh details when page is shown
        self.bind("<<ShowPage>>", self.refresh_details)

    def refresh_details(self, event=None):
        """Display the current booking details"""
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)

        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            self.details_text.insert("1.0", "No booking information available.")
            self.details_text.config(state="disabled")
            return

        # Build details text
        details = "=" * 60 + "\n"
        details += "                    BOOKING INFORMATION\n"
        details += "=" * 60 + "\n\n"

        details += f"Confirmation Code:   {booking.get('confirmation_code', 'N/A')}\n"
        details += f"Status:              {booking.get('status', 'N/A')}\n\n"

        details += "GUEST INFORMATION\n"
        details += "-" * 60 + "\n"
        details += f"Name:                {booking.get('first_name', '')} {booking.get('last_name', '')}\n"
        details += f"Email:               {booking.get('email', 'N/A')}\n"
        details += f"Phone:               {booking.get('phone', 'N/A')}\n"
        details += f"Guests:              {booking.get('adults', 0)} Adult(s), {booking.get('children', 0)} Child(ren)\n\n"

        details += "STAY DETAILS\n"
        details += "-" * 60 + "\n"
        details += f"Check-in:            {booking.get('check_in', 'N/A')}\n"
        details += f"Check-out:           {booking.get('check_out', 'N/A')}\n"
        details += f"Nights:              {booking.get('nights', 0)}\n\n"

        details += "ROOM INFORMATION\n"
        details += "-" * 60 + "\n"
        details += f"Room:                {booking.get('room_name', 'N/A')}\n"
        details += f"Type:                {booking.get('room_type', 'N/A')}\n"
        details += f"Breakfast:           {'Yes' if booking.get('breakfast') else 'No'}\n"
        details += f"Shuttle:             {'Yes' if booking.get('shuttle') else 'No'}\n\n"

        details += "PAYMENT\n"
        details += "-" * 60 + "\n"
        details += f"Total Price:         ${booking.get('total_price', 0.0):.2f}\n"
        details += f"Card (last 4):       ****{booking.get('payment_last4', '****')}\n"

        details += "=" * 60 + "\n"

        self.details_text.insert("1.0", details)
        self.details_text.config(state="disabled")


class ModifyBookingPage(tk.Frame):
    """
    F12: Modify Booking Page
    Allow users to modify their booking details
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(self, text="Modify Your Booking", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(20, 10))

        info = tk.Label(
            self,
            text="Update your booking information below.\n"
                 "Note: You cannot change the room type or dates here.\n"
                 "To change these, please cancel and create a new booking.",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
            fg="#666666",
            justify="center",
        )
        info.pack(pady=(0, 20))

        # Form frame
        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=20)

        # Email
        tk.Label(form, text="Email:", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=0, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_email = tk.Entry(form, font=FONT_LABEL, width=25)
        self.entry_email.grid(row=0, column=1, padx=10, pady=12)

        # Phone
        tk.Label(form, text="Phone Number:", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=1, column=0, padx=10, pady=12, sticky="e"
        )
        self.entry_phone = tk.Entry(form, font=FONT_LABEL, width=25)
        self.entry_phone.grid(row=1, column=1, padx=10, pady=12)

        # Adults
        tk.Label(form, text="Number of Adults:", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=2, column=0, padx=10, pady=12, sticky="e"
        )
        self.adults_var = tk.IntVar(value=1)
        adults_spinbox = tk.Spinbox(
            form,
            from_=1,
            to=10,
            textvariable=self.adults_var,
            font=FONT_LABEL,
            width=23,
            state="readonly",
        )
        adults_spinbox.grid(row=2, column=1, padx=10, pady=12)

        # Children
        tk.Label(form, text="Number of Children:", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=3, column=0, padx=10, pady=12, sticky="e"
        )
        self.children_var = tk.IntVar(value=0)
        children_spinbox = tk.Spinbox(
            form,
            from_=0,
            to=10,
            textvariable=self.children_var,
            font=FONT_LABEL,
            width=23,
            state="readonly",
        )
        children_spinbox.grid(row=3, column=1, padx=10, pady=12)

        # Add-ons
        addon_frame = tk.Frame(form, bg=BG_COLOR)
        addon_frame.grid(row=4, column=0, columnspan=2, pady=15)

        self.breakfast_var = tk.BooleanVar(value=False)
        breakfast_check = tk.Checkbutton(
            addon_frame,
            text="Include Breakfast",
            variable=self.breakfast_var,
            font=FONT_LABEL,
            bg=BG_COLOR,
        )
        breakfast_check.pack(side="left", padx=15)

        self.shuttle_var = tk.BooleanVar(value=False)
        shuttle_check = tk.Checkbutton(
            addon_frame,
            text="Include Airport Shuttle",
            variable=self.shuttle_var,
            font=FONT_LABEL,
            bg=BG_COLOR,
        )
        shuttle_check.pack(side="left", padx=15)

        # Buttons
        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=30)

        btn_back = tk.Button(
            buttons,
            text="Back",
            font=("Arial", 12),
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=15,
            command=lambda: controller.show_frame("ViewBookingPage"),
        )
        btn_back.pack(side="left", padx=10)

        btn_save = tk.Button(
            buttons,
            text="Save Changes",
            font=FONT_BUTTON,
            bg="#28a745",  # Green
            fg="white",
            width=15,
            command=self.on_save,
        )
        btn_save.pack(side="left", padx=10)

        # Load current data when page is shown
        self.bind("<<ShowPage>>", self.load_current_data)

    def load_current_data(self, event=None):
        """Load current booking data into form"""
        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            return

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, booking.get("email", ""))

        self.entry_phone.delete(0, tk.END)
        self.entry_phone.insert(0, booking.get("phone", ""))

        self.adults_var.set(booking.get("adults", 1))
        self.children_var.set(booking.get("children", 0))

        self.breakfast_var.set(booking.get("breakfast", False))
        self.shuttle_var.set(booking.get("shuttle", False))

    def on_save(self):
        """Save the modified booking"""
        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            messagebox.showerror("Error", "No booking to modify.")
            return

        last_name = booking.get("last_name", "")
        code = booking.get("confirmation_code", "")

        # Collect new data
        new_fields = {
            "email": self.entry_email.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "adults": self.adults_var.get(),
            "children": self.children_var.get(),
            "breakfast": self.breakfast_var.get(),
            "shuttle": self.shuttle_var.get(),
        }

        # Basic validation
        if not new_fields["email"] or not new_fields["phone"]:
            messagebox.showerror("Validation Error", "Email and phone cannot be empty.")
            return

        # Update booking
        success = update_booking(last_name, code, new_fields)

        if success:
            # Update the current booking in controller
            for key, value in new_fields.items():
                booking[key] = value

            messagebox.showinfo(
                "Success",
                "Your booking has been updated successfully!"
            )
            self.controller.show_frame("ViewBookingPage")
        else:
            messagebox.showerror(
                "Error",
                "Failed to update booking. Please try again."
            )


class CancelBookingPage(tk.Frame):
    """
    F13: Cancel Booking Page
    Allow users to cancel their booking
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        title = tk.Label(
            self,
            text="Cancel Booking",
            font=FONT_TITLE,
            bg=BG_COLOR,
            fg="#DC3545",  # Red
        )
        title.pack(pady=(30, 20))

        # Warning icon
        warning_icon = tk.Label(
            self,
            text="⚠",
            font=("Arial", 60, "bold"),
            bg=BG_COLOR,
            fg="#DC3545",
        )
        warning_icon.pack(pady=(10, 20))

        # Warning message
        warning_msg = tk.Label(
            self,
            text="Are you sure you want to cancel this booking?",
            font=("Arial", 14, "bold"),
            bg=BG_COLOR,
            fg="#333333",
        )
        warning_msg.pack(pady=(0, 10))

        # Details about the booking
        self.booking_info = tk.Label(
            self,
            text="",
            font=("Arial", 11),
            bg=BG_COLOR,
            fg="#666666",
            justify="center",
        )
        self.booking_info.pack(pady=(0, 20))

        info = tk.Label(
            self,
            text="This action cannot be undone.\n"
                 "Your booking will be marked as cancelled.",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
            fg="#999999",
            justify="center",
        )
        info.pack(pady=(0, 30))

        # Buttons
        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=20)

        btn_back = tk.Button(
            buttons,
            text="No, Go Back",
            font=FONT_BUTTON,
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=15,
            command=lambda: controller.show_frame("ViewBookingPage"),
        )
        btn_back.pack(side="left", padx=15)

        btn_confirm = tk.Button(
            buttons,
            text="Yes, Cancel Booking",
            font=FONT_BUTTON,
            bg="#DC3545",  # Red
            fg="white",
            width=18,
            command=self.on_confirm_cancel,
        )
        btn_confirm.pack(side="left", padx=15)

        # Load booking info when page is shown
        self.bind("<<ShowPage>>", self.load_booking_info)

    def load_booking_info(self, event=None):
        """Display basic booking info"""
        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            self.booking_info.config(text="No booking information")
            return

        info_text = (
            f"Booking Code: {booking.get('confirmation_code', 'N/A')}\n"
            f"Guest: {booking.get('first_name', '')} {booking.get('last_name', '')}\n"
            f"Room: {booking.get('room_name', 'N/A')}\n"
            f"Check-in: {booking.get('check_in', 'N/A')}"
        )
        self.booking_info.config(text=info_text)

    def on_confirm_cancel(self):
        """Confirm and cancel the booking"""
        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            messagebox.showerror("Error", "No booking to cancel.")
            return

        last_name = booking.get("last_name", "")
        code = booking.get("confirmation_code", "")

        # Cancel the booking
        success = cancel_booking(last_name, code)

        if success:
            messagebox.showinfo(
                "Booking Cancelled",
                "Your booking has been cancelled successfully.\n\n"
                "期待您的再次光临！"
            )
            # Clear current booking and return to home
            if hasattr(self.controller, "current_booking"):
                delattr(self.controller, "current_booking")
            self.controller.show_frame("WelcomePage")
        else:
            messagebox.showerror(
                "Error",
                "Failed to cancel booking. Please try again."
            )
