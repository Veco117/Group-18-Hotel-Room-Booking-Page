# manage_booking_flow.py
# F12: Modify Booking - Allow users to modify existing bookings
# F13: Cancel Booking - Allow users to cancel bookings

import tkinter as tk
from tkinter import ttk, messagebox
import os
from booking_storage import find_booking_by_code, update_booking, cancel_booking

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")

PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"


def create_round_rect_canvas(canvas, x1, y1, x2, y2, radius=20, tags=None, **kwargs):
    """
    Draw rounded rectangle using Canvas's create_polygon
    This is a native Canvas method, doesn't require Pillow
    """
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    if tags:
        kwargs['tags'] = tags
    return canvas.create_polygon(points, smooth=True, **kwargs)


class ViewBookingPage(tk.Frame):
    """
    Display booking details after search
    Provide options to modify or cancel
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "Your_booking_details_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        center_x = 450
        
        # Title: "Your Booking Details" (directly on background)
        self.canvas.create_text(
            center_x, 50,
            text="Your Booking Details",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Info text (directly on background)
        self.canvas.create_text(
            center_x, 130,
            text="Review your booking information below.",
            font=("Arial", 13, "italic"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Details container (white background frame for readability)
        details_frame = tk.Frame(self.canvas, bg="white", relief="ridge", bd=2)
        self.canvas.create_window(center_x, 340, window=details_frame, anchor="center", width=800, height=350)

        # Details text area
        self.details_text = tk.Text(
            details_frame,
            font=("Courier New", 10),
            bg="white",
            wrap="word",
            height=20,
            state="disabled",
        )
        self.details_text.pack(padx=20, pady=20, fill="both", expand=True)

        # Button dimensions
        btn_width = 180
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 560
        
        # Calculate button positions
        total_width = btn_width * 3 + btn_spacing * 2
        start_x = center_x - total_width // 2
        
        # "Back to Search" button (#d8aeba)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#d8aeba",  # Pink color
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Back to Search",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("ManageBookingPage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Modify Booking" button (#000636)
        btn_modify_x1 = start_x + btn_width + btn_spacing
        btn_modify_y1 = btn_y - btn_height // 2
        btn_modify_x2 = btn_modify_x1 + btn_width
        btn_modify_y2 = btn_modify_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_modify_x1, btn_modify_y1, btn_modify_x2, btn_modify_y2,
            radius=btn_radius,
            fill="#000636",  # Dark blue
            outline="",
            tags="btn_modify"
        )
        self.canvas.create_text(
            (btn_modify_x1 + btn_modify_x2) // 2,
            (btn_modify_y1 + btn_modify_y2) // 2,
            text="Modify Booking",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_modify"
        )
        self.canvas.tag_bind("btn_modify", "<Button-1>", lambda e: controller.show_frame("ModifyBookingPage"))
        self.canvas.tag_bind("btn_modify", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_modify", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Cancel Booking" button (#d15757)
        btn_cancel_x1 = start_x + (btn_width + btn_spacing) * 2
        btn_cancel_y1 = btn_y - btn_height // 2
        btn_cancel_x2 = btn_cancel_x1 + btn_width
        btn_cancel_y2 = btn_cancel_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_cancel_x1, btn_cancel_y1, btn_cancel_x2, btn_cancel_y2,
            radius=btn_radius,
            fill="#d15757",  # Red color
            outline="",
            tags="btn_cancel"
        )
        self.canvas.create_text(
            (btn_cancel_x1 + btn_cancel_x2) // 2,
            (btn_cancel_y1 + btn_cancel_y2) // 2,
            text="Cancel Booking",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_cancel"
        )
        self.canvas.tag_bind("btn_cancel", "<Button-1>", lambda e: controller.show_frame("CancelBookingPage"))
        self.canvas.tag_bind("btn_cancel", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_cancel", "<Leave>", lambda e: self.canvas.config(cursor=""))

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
        
        # Calculate detailed pricing
        # Get room price from rooms_data
        from rooms_data import ROOMS
        room_type = booking.get('room_type', '')
        room_name = booking.get('room_name', '')
        nights = booking.get('nights', 0)
        
        # Find room price from ROOMS list
        room_price_per_night = 0.0
        for room in ROOMS:
            if room.get('short_type') == room_type or room.get('name') == room_name:
                room_price_per_night = room.get('price', 0.0)
                break
        
        # Calculate room total
        room_total = room_price_per_night * nights
        
        # Calculate service fees
        breakfast_fee = 40.0 if booking.get('breakfast', False) else 0.0
        shuttle_fee = 25.0 if booking.get('shuttle', False) else 0.0
        
        # Calculate subtotal and tax
        subtotal = room_total + breakfast_fee + shuttle_fee
        tax = subtotal * 0.10  # 10% tax
        total_price = subtotal + tax
        
        # Display detailed pricing
        details += f"Room Charge:         ${room_total:.2f}\n"
        if breakfast_fee > 0:
            details += f"Breakfast:            ${breakfast_fee:.2f}\n"
        if shuttle_fee > 0:
            details += f"Airport Shuttle:      ${shuttle_fee:.2f}\n"
        details += f"Tax (10%):            ${tax:.2f}\n"
        details += f"Total Price:          ${total_price:.2f}\n"
        details += f"Card (last 4):        ****{booking.get('payment_last4', '****')}\n"

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

        # Create canvas for background image
        canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "modify_your_booking_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        # Create a frame on the canvas for content
        content_frame = tk.Frame(canvas, bg=BG_COLOR)
        canvas.create_window(450, 300, window=content_frame, anchor="center")

        title = tk.Label(content_frame, text="Modify Your Booking", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(20, 10))

        info = tk.Label(
            content_frame,
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
        form = tk.Frame(content_frame, bg=BG_COLOR)
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
        buttons = tk.Frame(content_frame, bg=BG_COLOR)
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

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "cancel_booking_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        center_x = 450
        
        # Details about the booking (directly on background)
        self.booking_info_id = self.canvas.create_text(
            center_x, 360,
            text="",
            font=("Arial", 13),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Info text (directly on background)
        self.canvas.create_text(
            center_x, 430,
            text="This action cannot be undone.\nYour booking will be marked as cancelled.",
            font=("Arial", 12, "italic"),
            fill="#001540",  # Dark blue
            anchor="center"
        )
        
        # Button dimensions
        btn_width = 180
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 510  # Moved down 1.5cm (60 pixels)
        
        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2
        
        # "No, Go Back" button (#98afce)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#98afce",  # Light blue
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="No, Go Back",
            font=("Arial", 12, "bold"),
            fill="white",  # White text
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("ViewBookingPage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Yes, Cancel Booking" button (#d15757)
        btn_confirm_x1 = start_x + btn_width + btn_spacing
        btn_confirm_y1 = btn_y - btn_height // 2
        btn_confirm_x2 = btn_confirm_x1 + btn_width
        btn_confirm_y2 = btn_confirm_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_confirm_x1, btn_confirm_y1, btn_confirm_x2, btn_confirm_y2,
            radius=btn_radius,
            fill="#d15757",  # Red
            outline="",
            tags="btn_confirm"
        )
        self.canvas.create_text(
            (btn_confirm_x1 + btn_confirm_x2) // 2,
            (btn_confirm_y1 + btn_confirm_y2) // 2,
            text="Yes, Cancel Booking",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_confirm"
        )
        self.canvas.tag_bind("btn_confirm", "<Button-1>", lambda e: self.on_confirm_cancel())
        self.canvas.tag_bind("btn_confirm", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_confirm", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # Load booking info when page is shown
        self.bind("<<ShowPage>>", self.load_booking_info)

    def load_booking_info(self, event=None):
        """Display basic booking info"""
        booking = getattr(self.controller, "current_booking", None)
        if not booking:
            self.canvas.itemconfig(self.booking_info_id, text="No booking information")
            return

        info_text = (
            f"Booking Code: {booking.get('confirmation_code', 'N/A')}\n"
            f"Guest: {booking.get('first_name', '')} {booking.get('last_name', '')}\n"
            f"Room: {booking.get('room_name', 'N/A')}\n"
            f"Check-in: {booking.get('check_in', 'N/A')}"
        )
        self.canvas.itemconfig(self.booking_info_id, text=info_text)

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
                "We look forward to your next visit!"
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
