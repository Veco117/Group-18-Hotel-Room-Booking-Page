import tkinter as tk

from tkinter import ttk, messagebox

import json

import os

import sys

# Try to import Pillow library

try:

    from PIL import Image, ImageTk

    HAS_PIL = True

except ImportError:

    HAS_PIL = False

    print("⚠️ Warning: Pillow library not detected. Images will not be displayed.")

    print("Please run in terminal: pip install pillow")

# ==========================================

# Global Configuration & UI Style Constants

# ==========================================

WINDOW_WIDTH = 900

WINDOW_HEIGHT = 600

BG_COLOR = "#F5F5F5"

FRAME_BG_COLOR = "#FFFFFF"

PRIMARY_COLOR = "#2F80ED"   # Blue

SECONDARY_COLOR = "#E0E0E0" # Light gray

NAV_COLOR = "#333333"       

TEXT_COLOR = "#333333"

FONT_TITLE = ("Arial", 18, "bold")

FONT_SUBTITLE = ("Arial", 14, "bold")

FONT_NORMAL = ("Arial", 12)

FONT_SMALL = ("Arial", 10, "italic")

FONT_NAV = ("Arial", 11, "bold")

DB_FILE = "bookings.json"

# ==========================================

# Utility Functions

# ==========================================

def ensure_dummy_data():

    if not os.path.exists(DB_FILE):

        dummy_data = [{"confirmation_code": "A1B2", "last_name": "Lu", "room_type": "King", "check_in": "2025-11-01", "status": "Confirmed"}]

        try:

            with open(DB_FILE, 'w') as f: 

                json.dump(dummy_data, f)

        except: 

            pass

def check_booking(last_name, code):

    ensure_dummy_data()

    try:

        with open(DB_FILE, 'r') as f:

            bookings = json.load(f)

            for booking in bookings:

                if booking["last_name"].lower() == last_name.lower() and booking["confirmation_code"] == code:

                    return booking

        return None

    except: 

        return None

def load_and_resize_image(filename, width, height):

    if not HAS_PIL: 

        return None

    try:

        if not os.path.exists(filename):

            print(f"❌ Error: Image file not found: {filename}")

            return None

        img = Image.open(filename)

        img = img.resize((width, height), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(img)

    except Exception as e:

        print(f"❌ Image loading failed: {e}")

        return None

# ==========================================

# Page Class Definitions

# ==========================================

class WelcomePage(tk.Frame):

    """

    【F1】Welcome Page (Final Version)

    Top navigation bar (floating) + Background image (900x600) + Action buttons

    """

    def __init__(self, parent, controller):

        super().__init__(parent, bg=BG_COLOR)

        self.controller = controller

        self.bg_image_tk = None  # Keep reference

        # --- 1. Background Image Area (Canvas) - Full window size 900x600 ---

        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)

        self.canvas.pack(fill="both", expand=True)

        # Load background image at full window size (900x600)

        self.bg_image_tk = load_and_resize_image("welcome_bg.png", WINDOW_WIDTH, WINDOW_HEIGHT)

        if self.bg_image_tk:

            self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.bg_image_tk, anchor="center")

        else:

            # If no image, display text

            self.canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//3, text="Welcome to TVXK Hotel", font=("Arial", 24, "bold"), fill="#333")

            self.canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//3 + 40, text="(Image 'welcome_bg.png' not found)", font=("Arial", 10), fill="red")

        # --- 2. Top Navigation Bar (floating on top of image) ---

        nav_bar = tk.Frame(self, bg="white", height=60)

        nav_bar.place(x=0, y=0, width=WINDOW_WIDTH, height=60)

        tk.Label(nav_bar, text="TVXK HOTEL", font=("Arial", 16, "bold"), bg="white", fg="black").pack(side="left", padx=30)

        nav_buttons_frame = tk.Frame(nav_bar, bg="white")

        nav_buttons_frame.pack(side="right", padx=30)

        nav_items = [("Rooms", "RoomsPage"), ("Location", "LocationPage"), ("About us", "AboutUsPage")]

        for text, page_name in nav_items:

            tk.Button(nav_buttons_frame, text=text, font=FONT_NAV, bg="white", fg="black", relief="flat",

                      activebackground="#f0f0f0", cursor="hand2",

                      command=lambda p=page_name: controller.show_frame(p)).pack(side="left", padx=15)

        # --- 3. Action buttons directly on background image ---

        # Book Now button - positioned left and down a bit, extended left

        btn_book = tk.Button(self.canvas, text="BOOK NOW", font=("Arial", 12, "bold"),

                             bg=SECONDARY_COLOR, fg="black", width=30, height=2, relief="flat",

                             cursor="hand2",

                             command=lambda: controller.show_frame("FilterPage"))

        self.canvas.create_window(WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT - 80, window=btn_book, anchor="center")

        # Manage Booking button - positioned right and down a bit, extended right

        btn_manage = tk.Button(self.canvas, text="MANAGE BOOKING", font=("Arial", 12, "bold"),

                               bg=SECONDARY_COLOR, fg="black", width=30, height=2, relief="flat",

                               cursor="hand2",

                               command=lambda: controller.show_frame("ManageBookingPage"))

        self.canvas.create_window(WINDOW_WIDTH//2 + 180, WINDOW_HEIGHT - 80, window=btn_manage, anchor="center")


class ImagePageBase(tk.Frame):

    """Common full-screen image display page + Navigation bar + Back button"""

    def __init__(self, parent, controller, image_filename, title_text):

        super().__init__(parent, bg="black")

        self.controller = controller

        self.image_filename = image_filename

        self.tk_image = None 

        # --- Canvas for image - Full window size 900x600 ---

        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)

        self.canvas.pack(fill="both", expand=True)

        self.bind("<<ShowPage>>", self.load_image)

        # --- Top Navigation Bar (floating on top of image) ---

        nav_bar = tk.Frame(self, bg="white", height=60)

        nav_bar.place(x=0, y=0, width=WINDOW_WIDTH, height=60)

        tk.Label(nav_bar, text="TVXK HOTEL", font=("Arial", 16, "bold"), bg="white", fg="black").pack(side="left", padx=30)

        nav_buttons_frame = tk.Frame(nav_bar, bg="white")

        nav_buttons_frame.pack(side="right", padx=30)

        nav_items = [("Rooms", "RoomsPage"), ("Location", "LocationPage"), ("About us", "AboutUsPage")]

        for text, page_name in nav_items:

            tk.Button(nav_buttons_frame, text=text, font=FONT_NAV, bg="white", fg="black", relief="flat",

                      activebackground="#f0f0f0", cursor="hand2",

                      command=lambda p=page_name: controller.show_frame(p)).pack(side="left", padx=15)

        # --- Bottom Bar (floating on bottom of image) ---

        self.bottom_bar = tk.Frame(self, bg="white", height=60)

        self.bottom_bar.place(x=0, y=WINDOW_HEIGHT-60, width=WINDOW_WIDTH, height=60)

        tk.Button(self.bottom_bar, text="← Back to Main Menu", font=("Arial", 12, "bold"),

                  bg=SECONDARY_COLOR, fg=TEXT_COLOR, width=20, relief="flat",

                  command=lambda: controller.show_frame("WelcomePage")).pack(side="left", padx=20, pady=10)

        tk.Label(self.bottom_bar, text=title_text, font=("Arial", 14, "bold"), bg="white", fg="#333").pack(side="right", padx=30)

    def load_image(self, event=None):

        if self.tk_image: 

            return

        # Load image at full window size (900x600)

        self.tk_image = load_and_resize_image(self.image_filename, WINDOW_WIDTH, WINDOW_HEIGHT)

        if self.tk_image:

            self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.tk_image, anchor="center")

        else:

            self.canvas.create_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, text=f"Image not found:\n{self.image_filename}", fill="white", font=("Arial", 16))


class RoomsPage(ImagePageBase):

    def __init__(self, parent, controller): 

        super().__init__(parent, controller, "rooms_img.png", "Our Rooms")


class LocationPage(ImagePageBase):

    def __init__(self, parent, controller): 

        super().__init__(parent, controller, "location_img.png", "Explore Location")


class AboutUsPage(ImagePageBase):

    def __init__(self, parent, controller): 

        super().__init__(parent, controller, "about_img.png", "About Us")


# ==========================================

# Filter & Manage Pages (F4, F11)

# ==========================================

class FilterPage(tk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent, bg=BG_COLOR)

        self.controller = controller

        main_frame = tk.Frame(self, bg=FRAME_BG_COLOR, padx=30, pady=30)

        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=500)

        

        tk.Label(main_frame, text="Step 2 - Room Type & Preferences", font=FONT_TITLE, bg=FRAME_BG_COLOR).grid(row=0, column=0, columnspan=4, pady=(0, 20))

        tk.Label(main_frame, text="Room Type:", font=FONT_SUBTITLE, bg=FRAME_BG_COLOR).grid(row=1, column=0, sticky="w", pady=10)

        self.room_var = tk.StringVar(value="Single")

        for i, r in enumerate(["Single", "Double", "King", "Suite"]):

            tk.Radiobutton(main_frame, text=r, variable=self.room_var, value=r, bg=FRAME_BG_COLOR).grid(row=1, column=i+1, sticky="w")

        tk.Label(main_frame, text="Preferences:", font=FONT_SUBTITLE, bg=FRAME_BG_COLOR).grid(row=2, column=0, sticky="w", pady=10)

        self.pref_breakfast = tk.BooleanVar()

        self.pref_smoking = tk.BooleanVar()

        self.pref_pets = tk.BooleanVar()

        tk.Checkbutton(main_frame, text="Breakfast", variable=self.pref_breakfast, bg=FRAME_BG_COLOR).grid(row=2, column=1, sticky="w")

        tk.Checkbutton(main_frame, text="Smoking", variable=self.pref_smoking, bg=FRAME_BG_COLOR).grid(row=2, column=2, sticky="w")

        tk.Checkbutton(main_frame, text="Pets", variable=self.pref_pets, bg=FRAME_BG_COLOR).grid(row=2, column=3, sticky="w")

        tk.Label(main_frame, text="Price Range:", font=FONT_SUBTITLE, bg=FRAME_BG_COLOR).grid(row=4, column=0, sticky="w", pady=10)

        price_frame = tk.Frame(main_frame, bg=FRAME_BG_COLOR)

        price_frame.grid(row=4, column=1, columnspan=3, sticky="w")

        self.entry_min = tk.Entry(price_frame, width=8)

        self.entry_min.pack(side="left")

        tk.Label(price_frame, text="-", bg=FRAME_BG_COLOR).pack(side="left")

        self.entry_max = tk.Entry(price_frame, width=8)

        self.entry_max.pack(side="left")

        btn_frame = tk.Frame(main_frame, bg=FRAME_BG_COLOR)

        btn_frame.grid(row=6, column=0, columnspan=4, sticky="ew", pady=40)

        tk.Button(btn_frame, text="Back", bg=SECONDARY_COLOR, width=12, command=lambda: controller.show_frame("WelcomePage")).pack(side="left")

        tk.Button(btn_frame, text="Search Rooms", bg=PRIMARY_COLOR, fg="white", font=("Arial", 12, "bold"), width=15, command=self.on_search).pack(side="right")

    def on_search(self):

        messagebox.showinfo("Next Step", "Connecting to Result Page...")


class ManageBookingPage(tk.Frame):

    def __init__(self, parent, controller):

        super().__init__(parent, bg=BG_COLOR)

        self.controller = controller

        main_frame = tk.Frame(self, bg=FRAME_BG_COLOR, padx=40, pady=40)

        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=500)

        tk.Label(main_frame, text="Manage My Booking", font=FONT_TITLE, bg=FRAME_BG_COLOR).grid(row=0, column=0, columnspan=2, pady=30)

        tk.Label(main_frame, text="Last Name:", bg=FRAME_BG_COLOR).grid(row=1, column=0, sticky="e", padx=10)

        self.entry_lastname = tk.Entry(main_frame, width=30)

        self.entry_lastname.grid(row=1, column=1)

        tk.Label(main_frame, text="Code:", bg=FRAME_BG_COLOR).grid(row=2, column=0, sticky="e", padx=10)

        self.entry_code = tk.Entry(main_frame, width=30)

        self.entry_code.grid(row=2, column=1)

        tk.Button(main_frame, text="Find", bg=PRIMARY_COLOR, fg="white", command=self.perform_search).grid(row=3, column=1, sticky="e", pady=20)

        self.result_label = tk.Label(main_frame, text="", bg=FRAME_BG_COLOR)

        self.result_label.grid(row=4, column=0, columnspan=2)

        tk.Button(main_frame, text="Back", bg=SECONDARY_COLOR, command=lambda: controller.show_frame("WelcomePage")).grid(row=6, column=0, sticky="w", pady=20)

    def perform_search(self):

        booking = check_booking(self.entry_lastname.get().strip(), self.entry_code.get().strip())

        if booking: 

            self.result_label.config(text=f"Found: {booking['room_type']} Room", fg="green")

        else: 

            self.result_label.config(text="Not found.", fg="red")


class TVXKHotelApp(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("TVXK Hotel Booking System - Group 18")

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.resizable(False, False)

        container = tk.Frame(self, bg=BG_COLOR)

        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)

        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (WelcomePage, FilterPage, ManageBookingPage, RoomsPage, LocationPage, AboutUsPage):

            frame = F(parent=container, controller=self)

            self.frames[F.__name__] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def show_frame(self, page_name):

        frame = self.frames[page_name]

        frame.tkraise()

        frame.event_generate("<<ShowPage>>")


if __name__ == "__main__":

    if os.environ.get('DISPLAY', '') == '' and os.name != 'nt': 

        print("❌ No Display found. Run locally.")

    else: 

        app = TVXKHotelApp()

        app.mainloop()

