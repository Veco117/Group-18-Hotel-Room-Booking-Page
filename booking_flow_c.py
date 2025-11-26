import tkinter as tk
from tkinter import messagebox, ttk
import os

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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


# Use colors defined in Part B to maintain consistent style
BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")
PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"

class Tooltip:
    """
    Tooltip class that displays a small window next to the target widget when hovering or triggered
    """
    def __init__(self, widget, text, timeout=2000):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.timeout = timeout
        self._after_id = None

    def show(self):
        self.hide()
        if not self.text:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=2)
        self._after_id = tw.after(self.timeout, self.hide)

    def hide(self):
        if self._after_id and self.tipwindow:
            self.tipwindow.after_cancel(self._after_id)
            self._after_id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class GuestInfoPage(tk.Frame):
    """
    Part C - F3 & F6: Enter guest information
    Design intent: Receive user input, validate it, and store it in controller.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "enter_guest_details_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        # Center position
        center_x = 450
        
        # Title: "Enter Guest Details" (dark blue text, directly on background)
        self.canvas.create_text(
            center_x, 140,
            text="Enter Guest Details",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Form elements directly on background (no white card) - multi-row, centered
        # Up shift 1cm (approximately 40 pixels)
        form_y_start = 200  # 200 (was 240, moved up 40 pixels)
        row_spacing = 50  # Vertical spacing between rows
        
        # Field spacing (horizontal spacing between fields on same row)
        field_spacing = 30
        label_width = 120  # Width for label text
        
        # Calculate center positions for form fields (centered)
        form_center_x = center_x
        
        # All labels align with Adults label, all input boxes have same width
        # Calculate starting x position for labels (aligned with Adults)
        entry_width = 20  # Uniform width for all Entry boxes
        entry_width_pixels = entry_width * 8  # Approximate pixels for Entry width
        
        # Calculate total width of row 1 (Adults and Children)
        row1_width = label_width + 60 + field_spacing + label_width + 60  # Adults + spacing + Children
        row1_start_x = form_center_x - row1_width // 2
        
        # Adults label
        self.canvas.create_text(
            row1_start_x, form_y_start,
            text="Adults (>12):",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.spin_adults = tk.Spinbox(self.canvas, from_=1, to=6, justify="center", width=5, font=FONT_LABEL,
                                      command=self.check_children)
        self.canvas.create_window(row1_start_x + label_width, form_y_start, window=self.spin_adults, anchor="w")

        # Children label
        children_x = row1_start_x + label_width + 60 + field_spacing
        self.canvas.create_text(
            children_x, form_y_start,
            text="Children (<=12):",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.spin_children = tk.Spinbox(self.canvas, from_=0, to=6, justify="center", width=5, font=FONT_LABEL,
                                        command=self.check_children)
        self.canvas.create_window(children_x + label_width, form_y_start, window=self.spin_children, anchor="w")

        # Row 2: First Name (label aligned with Adults, same entry width)
        self.canvas.create_text(
            row1_start_x, form_y_start + row_spacing,
            text="First Name:",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.entry_first_name = tk.Entry(self.canvas, width=entry_width, font=FONT_LABEL, bg="white")
        self.canvas.create_window(row1_start_x + label_width, form_y_start + row_spacing, window=self.entry_first_name, anchor="w")
        
        # Row 3: Last Name (label aligned with Adults, same entry width)
        self.canvas.create_text(
            row1_start_x, form_y_start + row_spacing * 2,
            text="Last Name:",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.entry_last_name = tk.Entry(self.canvas, width=entry_width, font=FONT_LABEL, bg="white")
        self.canvas.create_window(row1_start_x + label_width, form_y_start + row_spacing * 2, window=self.entry_last_name, anchor="w")
        
        # Row 4: Email (label aligned with Adults, same entry width)
        self.canvas.create_text(
            row1_start_x, form_y_start + row_spacing * 3,
            text="Email:",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.entry_email = tk.Entry(self.canvas, width=entry_width, font=FONT_LABEL, bg="white")
        self.canvas.create_window(row1_start_x + label_width, form_y_start + row_spacing * 3, window=self.entry_email, anchor="w")

        # Row 5: Phone Number (label aligned with Adults, same entry width)
        self.canvas.create_text(
            row1_start_x, form_y_start + row_spacing * 4,
            text="Phone Number:",
            font=FONT_LABEL,
            fill="#001540",
            anchor="w"
        )
        self.entry_phone = tk.Entry(self.canvas, width=entry_width, font=FONT_LABEL, bg="white")
        self.canvas.create_window(row1_start_x + label_width, form_y_start + row_spacing * 4, window=self.entry_phone, anchor="w")

        # Button dimensions (directly on background)
        btn_width = 180
        btn_height = 40
        btn_radius = 10
        btn_spacing = 30
        btn_y = 500  # Button Y position
        
        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2
        
        # "Back to dates" button (light blue-grey background, white text)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#6e88b9",  # Blue color
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Back to dates",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("SearchResultsPage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Continue" button (dark purple/blue background, white text, with thin border)
        btn_continue_x1 = start_x + btn_width + btn_spacing
        btn_continue_y1 = btn_y - btn_height // 2
        btn_continue_x2 = btn_continue_x1 + btn_width
        btn_continue_y2 = btn_continue_y1 + btn_height
        
        # Draw border first (thin border)
        create_round_rect_canvas(
            self.canvas,
            btn_continue_x1 - 1, btn_continue_y1 - 1, btn_continue_x2 + 1, btn_continue_y2 + 1,
            radius=btn_radius + 1,
            fill="#000636",  # Border color
            outline="",
            tags="btn_continue_border"
        )
        # Then draw button background
        create_round_rect_canvas(
            self.canvas,
            btn_continue_x1, btn_continue_y1, btn_continue_x2, btn_continue_y2,
            radius=btn_radius,
            fill="#000636",  # Button background color
            outline="",
            tags="btn_continue"
        )
        self.canvas.create_text(
            (btn_continue_x1 + btn_continue_x2) // 2,
            (btn_continue_y1 + btn_continue_y2) // 2,
            text="Continue",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_continue"
        )
        self.canvas.tag_bind("btn_continue", "<Button-1>", lambda e: self.validate_and_proceed())
        self.canvas.tag_bind("btn_continue", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_continue", "<Leave>", lambda e: self.canvas.config(cursor=""))
        self.canvas.tag_bind("btn_continue_border", "<Button-1>", lambda e: self.validate_and_proceed())
        self.canvas.tag_bind("btn_continue_border", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_continue_border", "<Leave>", lambda e: self.canvas.config(cursor=""))

    def check_children(self):
        """Ensure children < adults and total ≤ 6."""
        try:
            adults = int(self.spin_adults.get())
            children = int(self.spin_children.get())
        except ValueError:
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, "0")
            return

        tooltip = Tooltip(self.spin_children, "Children must be less than adults and no more than 6 people in total")

        # Rule 1: children counts < adults count
        if children >= adults:
            new_value = max(adults - 1, 0)
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, str(new_value))
            tooltip.show()
            return

        # Rule 2: total people counts <= 6
        if adults + children > 6:
            # automatically changes children number
            new_value = max(6 - adults, 0)
            self.spin_children.delete(0, "end")
            self.spin_children.insert(0, str(new_value))
            tooltip.show()

    def validate_and_proceed(self):
        """Logic processing: data validation and saving"""
        # Get first name and last name from separate fields
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()

        # Simple validation logic (F6 requirement)
        if not first_name or any(char.isdigit() for char in first_name):
            messagebox.showerror("Error", "Please enter a valid first name (no numbers).")
            return
        if not last_name or any(char.isdigit() for char in last_name):
            messagebox.showerror("Error", "Please enter a valid last name (no numbers).")
            return
        if "@" not in email or "." not in email:
            # TODO: Change to use regex for email validation
            messagebox.showerror("Error", "Please enter a valid email address.")
            return
        # ================== 修改结束 ==================

        if not phone.isdigit() or len(phone) < 8:
            messagebox.showerror("Error", "Please enter a valid phone number (digits only).")
            return
        # TODO: Check the difference between children and adults count

        # Save data to Controller (shared data)
        self.controller.guest_info = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "adults": int(self.spin_adults.get()),
            "children": int(self.spin_children.get())
        }

        # Navigate to booking summary page
        self.controller.show_frame("SummaryPage")


class SummaryPage(tk.Frame):
    """
    Part C - F7: Booking summary, pricing and payment call
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "booking_sumary_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        # Center position
        center_x = 450
        
        # Title: "Booking Summary" (dark blue text, directly on background)
        self.canvas.create_text(
            center_x, 50,
            text="Booking Summary",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="center"
        )

        # Information display area (white background Frame for readability)
        self.info_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window(center_x, 280, window=self.info_frame, anchor="center", width=700, height=300)

        # Button dimensions (same as other pages)
        btn_width = 200
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 500  # Button Y position
        
        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2
        
        # "Edit Details" button (darker blue background, white text)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#8abccf",  # Light blue color
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Edit Details",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("GuestInfoPage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Confirm & Pay" button (dark blue background, white text)
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
            text="Confirm & Pay",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_pay"
        )
        self.canvas.tag_bind("btn_pay", "<Button-1>", lambda e: self.process_payment())
        self.canvas.tag_bind("btn_pay", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_pay", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # Key: Trigger data refresh every time the page is shown
        self.bind("<<ShowPage>>", self.refresh_data)

    def refresh_data(self, event=None):
        """Dynamically read data from Controller and calculate price"""
        # 1. Clear old content
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # 2. Safely get data (prevent errors)
        stay = getattr(self.controller, "current_stay", {})
        room = getattr(self.controller, "selected_room", {})
        guest = getattr(self.controller, "guest_info", {})
        filters = getattr(self.controller, "current_filter", {})

        if not stay or not room:
            tk.Label(self.info_frame, text="Missing booking info.", bg="white").pack()
            return

        # 3. Extract variables
        check_in = stay.get("check_in")
        nights = stay.get("nights", 0)
        room_name = room.get("name", "Unknown")
        price_per_night = float(room.get("price", 0))
        adults = guest.get("adults", 1)

        # 4. Price calculation (F7 core logic)
        room_total = price_per_night * nights
        
        # Add breakfast and shuttle fees
        breakfast_fee = 0.0
        shuttle_fee = 0.0
        if filters.get("Breakfast", False):
            breakfast_fee = 40.0
        if filters.get("Shuttle", False):
            shuttle_fee = 25.0
        
        subtotal = room_total + breakfast_fee + shuttle_fee
        tax = subtotal * 0.10  # Assume 10% tax
        self.final_total = subtotal + tax  # Store as instance variable for payment use

        # 5. UI display
        lines = [
            ("GUEST", f"{guest.get('first_name')}", 14, "bold"),
            ("Room Type", f"{room_name}", 12, "normal"),
            ("Dates", f"{check_in} ({nights} nights)", 12, "normal"),
            ("Guests", f"{adults} Adults, {guest.get('children')} Children", 12, "normal"),
            ("-" * 40, "", 10, "normal"),
            ("Room Charge", f"${room_total:.2f}", 12, "normal"),
        ]
        
        # Add breakfast and shuttle fees to display if selected
        if breakfast_fee > 0:
            lines.append(("Breakfast", f"${breakfast_fee:.2f}", 12, "normal"))
        if shuttle_fee > 0:
            lines.append(("Airport Shuttle", f"${shuttle_fee:.2f}", 12, "normal"))
        
        lines.extend([
            ("Tax (10%)", f"${tax:.2f}", 12, "normal"),
            ("TOTAL DUE", f"${self.final_total:.2f}", 16, "bold")
        ])

        for title, value, size, weight in lines:
            row = tk.Frame(self.info_frame, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=title, font=("Arial", size, weight), bg="white", fg="#555").pack(side="left")
            tk.Label(row, text=value, font=("Arial", size, weight), bg="white", fg="black").pack(side="right")

    def process_payment(self):
        """Navigate to payment page (PaymentPage)"""
        # Save total price to controller for PaymentPage use
        self.controller.total_price = self.final_total

        # Navigate to payment page
        self.controller.show_frame("PaymentPage")
