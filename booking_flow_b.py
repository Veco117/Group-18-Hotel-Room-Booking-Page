# booking_flow_b.py
# This file contains the pages that belong mostly to my part:
# - DateSelectionPage: F2 date selection and nights calculation.
# - SearchResultsPage: F5 search results list using filters and room data.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

from rooms_data import filter_rooms

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

        title = tk.Label(self, text="Step 1 - Select dates", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(10, 5))

        info = tk.Label(
            self,
            text="I ask you to choose a check-in date and a check-out date.\n"
                 "Then I will calculate how many nights you will stay.",
            font=("Arial", 10, "italic"),
            bg=BG_COLOR,
        )
        info.pack(pady=(0, 10))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(pady=10)

        # Check-in
        tk.Label(form, text="Check-in date", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=0, column=0, padx=8, pady=5, sticky="e"
        )
        if HAS_TKCALENDAR:
            self.entry_check_in = DateEntry(form, date_pattern="yyyy-mm-dd", width=18)
        else:
            self.entry_check_in = tk.Entry(form, width=20, font=FONT_LABEL)
            self.entry_check_in.insert(0, "YYYY-MM-DD")
        self.entry_check_in.grid(row=0, column=1, padx=8, pady=5)

        # Check-out
        tk.Label(form, text="Check-out date", font=FONT_LABEL, bg=BG_COLOR).grid(
            row=1, column=0, padx=8, pady=5, sticky="e"
        )
        if HAS_TKCALENDAR:
            self.entry_check_out = DateEntry(form, date_pattern="yyyy-mm-dd", width=18)
        else:
            self.entry_check_out = tk.Entry(form, width=20, font=FONT_LABEL)
            self.entry_check_out.insert(0, "YYYY-MM-DD")
        self.entry_check_out.grid(row=1, column=1, padx=8, pady=5)

        # Bottom buttons
        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=20)

        btn_back = tk.Button(
            buttons,
            text="Back to home",
            font=("Arial", 12),
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=12,
            command=lambda: controller.show_frame("WelcomePage"),
        )
        btn_back.pack(side="left", padx=10)

        btn_next = tk.Button(
            buttons,
            text="Continue",
            font=FONT_BUTTON,
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            width=15,
            command=self.on_continue,
        )
        btn_next.pack(side="left", padx=10)

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

        title = tk.Label(self, text="Available rooms", font=FONT_TITLE, bg=BG_COLOR)
        title.pack(pady=(10, 5))

        self.info_label = tk.Label(
            self,
            text="",
            font=FONT_LABEL,
            bg=BG_COLOR,
        )
        self.info_label.pack(pady=(0, 10))

        columns = ("name", "type", "floor", "price", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
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

        self.tree.pack(padx=20, pady=10, fill="x")

        buttons = tk.Frame(self, bg=BG_COLOR)
        buttons.pack(pady=15)

        btn_back = tk.Button(
            buttons,
            text="Back to filters",
            font=("Arial", 12),
            bg=SECONDARY_BG,
            fg=SECONDARY_FG,
            width=12,
            command=lambda: controller.show_frame("FilterPage"),
        )
        btn_back.pack(side="left", padx=10)

        btn_choose = tk.Button(
            buttons,
            text="Use this room",
            font=FONT_BUTTON,
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            width=15,
            command=self.on_choose,
        )
        btn_choose.pack(side="left", padx=10)

        # I refresh the table whenever this page is shown.
        self.bind("<<ShowPage>>", self.on_show)

    def on_show(self, event=None):
        # Clear old rows first.
        for item in self.tree.get_children():
            self.tree.delete(item)

        filters = getattr(self.controller, "current_filter", None)
        stay_info = getattr(self.controller, "current_stay", None)

        if not filters:
            self.info_label.config(
                text="I do not have any filters yet. Please go back and choose room filters first."
            )
            return

        if not stay_info:
            self.info_label.config(
                text="I do not know the stay length yet. Please choose dates first."
            )
            return

        nights = stay_info.get("nights", 1)
        check_in = stay_info.get("check_in", "")

        rooms = filter_rooms(filters, stay_info)
        self.controller.search_results = rooms

        if not rooms:
            self.info_label.config(
                text="No rooms matched these filters. Please change the options and try again."
            )
            return

        self.info_label.config(
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
