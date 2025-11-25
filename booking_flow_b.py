# booking_flow_b.py
# This file contains the pages that belong mostly to my part:
# - DateSelectionPage: F2 date selection and nights calculation.
# - SearchResultsPage: F5 search results list using filters and room data.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
    print("tkcalendar loaded - Calendar widgets will be used")
except ImportError:
    HAS_TKCALENDAR = False
    print("tkcalendar not found - Using text entry instead")

from rooms_data import filter_rooms

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

BG_COLOR = "#F5F5F5"
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")

PRIMARY_BG = "#2F80ED"
PRIMARY_FG = "white"
SECONDARY_BG = "#E0E0E0"
SECONDARY_FG = "#333333"


class DateSelectionPage(tk.Frame):
    """
    I let the user pick check-in and check-out dates.
    I then calculate how many nights they stay.
    This is my implementation of F2.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image (blurred beach scene)
        bg_path = "dates_bg.png"
        if HAS_PIL and os.path.exists(bg_path):
            try:
                bg_img = Image.open(bg_path)
                bg_img = bg_img.resize((900, 600), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(bg_img)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            except Exception as e:
                print(f"Failed to load {bg_path}: {e}")

        # Center position for content
        center_x = 450
        center_y = 300
        
        # Title: "Select dates" (dark blue text, same as Continue button)
        self.canvas.create_text(
            center_x, 120,
            text="Select dates",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="center"
        )

        # Instructional text (dark blue text)
        self.canvas.create_text(
            center_x, 170,
            text="Start by choosing your check-in and check-out dates.\nWe'll calculate the number of nights for you.",
            font=("Arial", 12),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="center",
            justify="center"
        )

        # Check-in date label (drawn on canvas) - even closer to input
        checkin_label_x = center_x - 50
        checkin_label_y = center_y - 30
        self.canvas.create_text(
            checkin_label_x, checkin_label_y,
            text="Check-in date:",
            font=("Arial", 12, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="e"
        )
        
        # Check-in date input (placed on canvas) - even closer to label
        if HAS_TKCALENDAR:
            self.entry_check_in = DateEntry(self.canvas, date_pattern="yyyy-mm-dd", width=18)
        else:
            self.entry_check_in = tk.Entry(self.canvas, width=22, font=("Arial", 11), bg="white")
            self.entry_check_in.insert(0, "YYYY-MM-DD")
        self.canvas.create_window(center_x + 5, checkin_label_y, window=self.entry_check_in, anchor="w")

        # Check-out date label (drawn on canvas) - even closer to input
        checkout_label_x = center_x - 50
        checkout_label_y = center_y + 20
        self.canvas.create_text(
            checkout_label_x, checkout_label_y,
            text="Check-out date:",
            font=("Arial", 12, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="e"
        )
        
        # Check-out date input (placed on canvas) - even closer to label
        if HAS_TKCALENDAR:
            self.entry_check_out = DateEntry(self.canvas, date_pattern="yyyy-mm-dd", width=18)
        else:
            self.entry_check_out = tk.Entry(self.canvas, width=22, font=("Arial", 11), bg="white")
            self.entry_check_out.insert(0, "YYYY-MM-DD")
        self.canvas.create_window(center_x + 5, checkout_label_y, window=self.entry_check_out, anchor="w")

        # Button dimensions
        btn_width = 200
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 450  # Button Y position
        
        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2
        
        # "Back to choices" button (darker blue background, white text)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#5A9BC4",  # Darker blue (deeper than #B0E0E6)
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Back to choices",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("WelcomePage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Continue" button (dark blue background, white text)
        btn_next_x1 = start_x + btn_width + btn_spacing
        btn_next_y1 = btn_y - btn_height // 2
        btn_next_x2 = btn_next_x1 + btn_width
        btn_next_y2 = btn_next_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_next_x1, btn_next_y1, btn_next_x2, btn_next_y2,
            radius=btn_radius,
            fill="#001540",  # Dark blue
            outline="",
            tags="btn_next"
        )
        self.canvas.create_text(
            (btn_next_x1 + btn_next_x2) // 2,
            (btn_next_y1 + btn_next_y2) // 2,
            text="Continue",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_next"
        )
        self.canvas.tag_bind("btn_next", "<Button-1>", lambda e: self.on_continue())
        self.canvas.tag_bind("btn_next", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_next", "<Leave>", lambda e: self.canvas.config(cursor=""))

    def on_continue(self):
        raw_in = self.entry_check_in.get().strip()
        raw_out = self.entry_check_out.get().strip()

        try:
            d_in = datetime.strptime(raw_in, "%Y-%m-%d").date()
            d_out = datetime.strptime(raw_out, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror(
                "Input Error",
                "Please use the format YYYY-MM-DD for both dates.",
            )
            return

        if d_out <= d_in:
            messagebox.showerror(
                "Input Error",
                "Check-out date must be later than check-in date.",
            )
            return

        nights = (d_out - d_in).days

        # I store the stay information on the controller so other pages can use it.
        self.controller.current_stay = {
            "check_in": d_in.isoformat(),
            "check_out": d_out.isoformat(),
            "nights": nights,
        }

        messagebox.showinfo(
            "Success",
            f"You are staying for {nights} night(s). Now I will take you to the filter page.",
        )

        self.controller.show_frame("FilterPage")


class SearchResultsPage(tk.Frame):
    """
    I display all the rooms that match the filters and the current stay.
    This is my main implementation of F5.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Create canvas for background image
        self.canvas = tk.Canvas(self, width=900, height=600, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Try to load background image
        bg_path = "available_rooms_bg.png"
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
        
        # Title: "Available rooms" (dark blue text, directly on background)
        self.canvas.create_text(
            center_x, 50,
            text="Available rooms",
            font=("Arial", 28, "bold"),
            fill="#001540",  # Dark blue, same as Continue button
            anchor="center"
        )

        # Info label (will be updated dynamically, drawn on canvas) - moved down
        self.info_text_id = self.canvas.create_text(
            center_x, 130,
            text="",
            font=("Arial", 12),
            fill="#001540",  # Dark blue
            anchor="center"
        )

        # Treeview frame (white background for readability) - moved down
        tree_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window(center_x, 300, window=tree_frame, anchor="center", width=800, height=250)

        columns = ("name", "type", "floor", "price", "total")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("name", text="Room")
        self.tree.heading("type", text="Type")
        self.tree.heading("floor", text="Floor")
        self.tree.heading("price", text="Price / night")
        self.tree.heading("total", text="Total for stay")

        self.tree.column("name", width=260)
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("floor", width=80, anchor="center")
        self.tree.column("price", width=120, anchor="e")
        self.tree.column("total", width=120, anchor="e")

        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        # Button dimensions (same as date selection page)
        btn_width = 200
        btn_height = 45
        btn_radius = 10
        btn_spacing = 30
        btn_y = 500  # Button Y position
        
        # Calculate button positions
        total_width = btn_width * 2 + btn_spacing
        start_x = center_x - total_width // 2
        
        # "Back to filters" button (grey background, white text)
        btn_back_x1 = start_x
        btn_back_y1 = btn_y - btn_height // 2
        btn_back_x2 = btn_back_x1 + btn_width
        btn_back_y2 = btn_back_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_back_x1, btn_back_y1, btn_back_x2, btn_back_y2,
            radius=btn_radius,
            fill="#908080",  # Grey color
            outline="",
            tags="btn_back"
        )
        self.canvas.create_text(
            (btn_back_x1 + btn_back_x2) // 2,
            (btn_back_y1 + btn_back_y2) // 2,
            text="Back to filters",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_back"
        )
        self.canvas.tag_bind("btn_back", "<Button-1>", lambda e: controller.show_frame("FilterPage"))
        self.canvas.tag_bind("btn_back", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_back", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # "Use this room" button (dark blue background, white text)
        btn_choose_x1 = start_x + btn_width + btn_spacing
        btn_choose_y1 = btn_y - btn_height // 2
        btn_choose_x2 = btn_choose_x1 + btn_width
        btn_choose_y2 = btn_choose_y1 + btn_height
        
        create_round_rect_canvas(
            self.canvas,
            btn_choose_x1, btn_choose_y1, btn_choose_x2, btn_choose_y2,
            radius=btn_radius,
            fill="#001540",  # Dark blue (same as Continue button)
            outline="",
            tags="btn_choose"
        )
        self.canvas.create_text(
            (btn_choose_x1 + btn_choose_x2) // 2,
            (btn_choose_y1 + btn_choose_y2) // 2,
            text="Book this room",
            font=("Arial", 12, "bold"),
            fill="white",
            tags="btn_choose"
        )
        self.canvas.tag_bind("btn_choose", "<Button-1>", lambda e: self.on_choose())
        self.canvas.tag_bind("btn_choose", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("btn_choose", "<Leave>", lambda e: self.canvas.config(cursor=""))

        # I refresh the table whenever this page is shown.
        self.bind("<<ShowPage>>", self.on_show)

    def on_show(self, event=None):
        # Clear old rows first.
        for item in self.tree.get_children():
            self.tree.delete(item)

        filters = getattr(self.controller, "current_filter", None)
        stay_info = getattr(self.controller, "current_stay", None)

        if not filters:
            self.canvas.itemconfig(
                self.info_text_id,
                text="I do not have any filters yet. Please go back and choose room filters first."
            )
            return

        if not stay_info:
            self.canvas.itemconfig(
                self.info_text_id,
                text="I do not know the stay length yet. Please choose dates first."
            )
            return

        nights = stay_info.get("nights", 1)
        check_in = stay_info.get("check_in", "")

        rooms = filter_rooms(filters, stay_info)
        self.controller.search_results = rooms

        if not rooms:
            self.canvas.itemconfig(
                self.info_text_id,
                text="No rooms matched these filters. Please change the options and try again."
            )
            return

        self.canvas.itemconfig(
            self.info_text_id,
            text=f"I found {len(rooms)} room type(s) for {nights} night(s), starting on {check_in}."
        )

        for room in rooms:
            price = float(room["price"])
            total = price * nights
            self.tree.insert(
                "",
                "end",
                values=(
                    room["name"],
                    room["short_type"],
                    room["floor"],
                    f"${price:.2f}",
                    f"${total:.2f}",
                ),
            )

    def on_choose(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror(
                "Input Error",
                "Please click on a room in the table first.",
            )
            return

        item_id = selection[0]
        index = self.tree.index(item_id)

        rooms = getattr(self.controller, "search_results", [])
        if index < 0 or index >= len(rooms):
            messagebox.showerror(
                "Input Error",
                "Something went wrong with the selection index.",
            )
            return

        chosen_room = rooms[index]
        self.controller.selected_room = chosen_room

        messagebox.showinfo(
            "Success",
            f"You chose: {chosen_room['name']}\n"
            "The guest information page will use this room.",
        )

        # Member C will implement GuestInfoPage. I just try to go there.
        try:
            self.controller.show_frame("GuestInfoPage")
        except KeyError:
            # If the page does not exist yet I send the user back home.
            self.controller.show_frame("WelcomePage")
