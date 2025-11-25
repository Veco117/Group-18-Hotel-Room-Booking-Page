import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# Try to import Pillow library (required for rounded corners and color processing)
try:
    from PIL import Image, ImageTk, ImageDraw, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow library not detected. Please run: pip install pillow")
    print("Without Pillow, rounded corner effects will degrade to rectangles.")

# Import booking flow pages
from booking_flow_b import DateSelectionPage, SearchResultsPage
from booking_flow_c import GuestInfoPage, SummaryPage  # F3+F6 合并版本
from booking_flow_d import PaymentPage, ConfirmationPage
from manage_booking_flow import ViewBookingPage, ModifyBookingPage, CancelBookingPage

# =========================================
# Global Configuration & Color Constants
# =========================================

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

BG_COLOR = "#F5F5F5"
SECONDARY_COLOR = "#E0E0E0"

# Bottom navigation button colors
NAV_BTN_BG = "#001540"      # Dark navy blue
NAV_BTN_FG = "#FFFFFF"      # White text

# Font configuration
FONT_TITLE = ("Arial", 24, "bold")      
FONT_SECTION = ("Arial", 12, "bold")    
FONT_BTN = ("Arial", 11, "bold")        
FONT_NORMAL = ("Arial", 12)

DB_FILE = "bookings.json"

# ==========================================
# Core Utility Functions: Data & Image Processing
# ==========================================

def ensure_dummy_data():
    """Generate dummy booking data for testing"""
    if not os.path.exists(DB_FILE):
        dummy_data = [{"confirmation_code": "A1B2", "last_name": "Lu", "room_type": "King", "check_in": "2025-11-01", "status": "Confirmed"}]
        try: 
            with open(DB_FILE, 'w') as f: 
                json.dump(dummy_data, f)
        except: 
            pass

def check_booking(last_name, code):
    """Query booking logic"""
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

# --- Core Graphics Processing Logic ---

def make_transparent(img):
    """
    【Smart Background Removal】
    If the image has a white background, try to make white transparent.
    Solves the 'black square' problem.
    """
    img = img.convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        # If pixel is close to white (R>200, G>200, B>200), make it transparent
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    return img

def invert_icon(img):
    """
    【Icon Black-White Inversion】
    Invert the icon itself (negative color), keeping transparency unchanged
    """
    if not HAS_PIL: return None
    
    img = img.convert('RGBA')
    # Get each channel
    r, g, b, a = img.split()
    
    # Convert RGB to grayscale, then invert
    # Using formula: inverted = 255 - original
    r_inv = ImageOps.invert(r)
    g_inv = ImageOps.invert(g)
    b_inv = ImageOps.invert(b)
    
    # Merge inverted channels, keeping original transparency
    out = Image.merge('RGBA', (r_inv, g_inv, b_inv, a))
    return out

def create_colored_icon(img, color):
    """
    【Icon Color Change】(kept for compatibility)
    Fill icon content with specified color based on transparency (color='black' or 'white').
    """
    if not HAS_PIL: return None
    
    img = img.convert('RGBA')
    # Get alpha channel
    r, g, b, a = img.split()
    
    # Create solid color base image
    color_layer = Image.new('RGB', img.size, color)
    
    # Use original image's alpha channel as mask to cut out solid color icon
    out = Image.merge('RGBA', (
        color_layer.split()[0], 
        color_layer.split()[1], 
        color_layer.split()[2], 
        a 
    ))
    return out

def create_rounded_bg(width, height, bg_color, border_color=None, radius=25):
    """Draw rounded background (returns RGB mode to ensure rounded corners display correctly)"""
    # Convert color string to RGB tuple
    def color_to_rgb(color):
        if isinstance(color, str):
            if color.lower() == "white":
                return (255, 255, 255)
            elif color.lower() == "black":
                return (0, 0, 0)
            else:
                return (255, 255, 255)  # Default white
        return color
    
    bg_rgb = color_to_rgb(bg_color)
    border_rgb = color_to_rgb(border_color) if border_color else None
    
    # Draw in RGBA mode first, then convert to RGB to ensure smooth rounded edges
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Use rounded_rectangle method (requires Pillow 10.0.0+)
    if hasattr(draw, 'rounded_rectangle'):
        # Draw rounded rectangle using rounded_rectangle method
        if border_rgb:
            # Draw border first (black rounded rectangle)
            draw.rounded_rectangle((0, 0, width-1, height-1), radius=radius, fill=border_rgb)
            # Then draw inner background (white rounded rectangle), leaving 2px border
            draw.rounded_rectangle((2, 2, width-3, height-3), radius=max(radius-2, 1), fill=bg_rgb)
        else:
            # No border, draw rounded rectangle directly
            draw.rounded_rectangle((0, 0, width-1, height-1), radius=radius, fill=bg_rgb)
    else:
        # If Pillow version is too old, use ellipse and rectangle combination to draw rounded rectangle
        # Ensure radius doesn't exceed half of width and height
        radius = min(radius, width // 2, height // 2)
        
        if border_rgb:
            # Draw border rectangle (middle part) first
            draw.rectangle((radius, 0, width-radius-1, height-1), fill=border_rgb)
            draw.rectangle((0, radius, width-1, height-radius-1), fill=border_rgb)
            # Draw four rounded corners (using ellipses)
            draw.ellipse((0, 0, radius*2, radius*2), fill=border_rgb)
            draw.ellipse((width-radius*2-1, 0, width-1, radius*2), fill=border_rgb)
            draw.ellipse((0, height-radius*2-1, radius*2, height-1), fill=border_rgb)
            draw.ellipse((width-radius*2-1, height-radius*2-1, width-1, height-1), fill=border_rgb)
            
            # Then draw inner background (white rounded rectangle), leaving 2px border
            inner_radius = max(radius - 2, 1)
            draw.rectangle((inner_radius+2, 2, width-inner_radius-3, height-3), fill=bg_rgb)
            draw.rectangle((2, inner_radius+2, width-3, height-inner_radius-3), fill=bg_rgb)
            # Draw four inner rounded corners
            draw.ellipse((2, 2, inner_radius*2+2, inner_radius*2+2), fill=bg_rgb)
            draw.ellipse((width-inner_radius*2-3, 2, width-3, inner_radius*2+2), fill=bg_rgb)
            draw.ellipse((2, height-inner_radius*2-3, inner_radius*2+2, height-3), fill=bg_rgb)
            draw.ellipse((width-inner_radius*2-3, height-inner_radius*2-3, width-3, height-3), fill=bg_rgb)
        else:
            # No border, draw rounded rectangle directly
            # Draw middle rectangle part
            draw.rectangle((radius, 0, width-radius-1, height-1), fill=bg_rgb)
            draw.rectangle((0, radius, width-1, height-radius-1), fill=bg_rgb)
            # Draw four rounded corners (using ellipses)
            draw.ellipse((0, 0, radius*2, radius*2), fill=bg_rgb)
            draw.ellipse((width-radius*2-1, 0, width-1, radius*2), fill=bg_rgb)
            draw.ellipse((0, height-radius*2-1, radius*2, height-1), fill=bg_rgb)
            draw.ellipse((width-radius*2-1, height-radius*2-1, width-1, height-1), fill=bg_rgb)
    
    # Convert to RGB mode (fill transparent areas with background color)
    rgb_image = Image.new('RGB', (width, height), bg_rgb)
    rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
    return rgb_image

def create_complete_button_image(width, height, bg_color, border_color, icon_img, text_label, text_color, radius=25):
    """
    Generate complete button image (including background, icon, text)
    Layer order: background (bottom) -> icon -> text (top)
    """
    # 1. Draw perfect rounded rectangle background first (bottom layer)
    bg_image = create_rounded_bg(width, height, bg_color, border_color, radius)
    
    # Ensure background is RGB mode
    if bg_image.mode != 'RGB':
        bg_image = bg_image.convert('RGB')
    
    # 2. Add icon (if any) - add icon first to ensure it's above background
    if icon_img and icon_img.size[0] > 0 and icon_img.size[1] > 0:
        # Resize icon to fit button
        icon_h_target = int(height * 0.6)  # Icon height is 60% of button height
        if icon_img.height > 0:
            ratio = icon_h_target / icon_img.height
            icon_w_target = int(icon_img.width * ratio)
        else:
            icon_w_target = icon_h_target
        
        icon_resized = icon_img.resize((icon_w_target, icon_h_target), Image.Resampling.LANCZOS)
        
        # Vertically centered, horizontally offset 25px
        y_pos = (height - icon_h_target) // 2
        x_pos = 25
        
        # If icon is RGBA mode, use alpha channel as mask
        if icon_resized.mode == 'RGBA':
            bg_image.paste(icon_resized, (x_pos, y_pos), icon_resized)
        else:
            bg_image.paste(icon_resized, (x_pos, y_pos))
    
    # 3. Add text (top layer) - add text last to ensure it's on top
    from PIL import ImageFont
    draw = ImageDraw.Draw(bg_image)
    
    # Try to use system font
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", 11)
        except:
            try:
                # Windows system font path
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
            except:
                font = ImageFont.load_default()
    
    # Calculate text position (centered)
    text_x = width // 2
    text_y = height // 2
    
    # Draw text (using anchor="mm" for center alignment)
    draw.text((text_x, text_y), text_label, fill=text_color, font=font, anchor="mm")
    
    return bg_image

def combine_icon(bg_img, icon_img):
    """Combine icon to the left side of background image (kept for compatibility)"""
    # Ensure background is RGB mode
    if bg_img.mode != 'RGB':
        bg_img = bg_img.convert('RGB')
    
    target = bg_img.copy()
    
    # Resize icon to fit button
    icon_h_target = int(bg_img.height * 0.6) # Icon height is 60% of button height
    if icon_img.height > 0:
        ratio = icon_h_target / icon_img.height
        icon_w_target = int(icon_img.width * ratio)
    else:
        icon_w_target = icon_h_target
    
    icon_resized = icon_img.resize((icon_w_target, icon_h_target), Image.Resampling.LANCZOS)
    
    # Vertically centered, horizontally offset 25px
    y_pos = (bg_img.height - icon_h_target) // 2
    x_pos = 25 
    
    # If icon is RGBA mode, use alpha channel as mask
    if icon_resized.mode == 'RGBA':
        target.paste(icon_resized, (x_pos, y_pos), icon_resized)
    else:
        target.paste(icon_resized, (x_pos, y_pos))
    
    return target

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

def load_simple_image(filename, w, h):
    """Simple image loader for background images etc."""
    if not HAS_PIL: return None
    if not os.path.exists(filename) and not os.path.exists(f"icon/{filename}"):
        return None
    
    path = filename if os.path.exists(filename) else f"icon/{filename}"
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        return None

# ==========================================
# Custom Component: SelectionButton (Rounded + Inverted Version)
# ==========================================

class CanvasButton:
    """
    Button class drawn directly on Canvas (not a separate Canvas)
    Draws rounded rectangle, icon, and text on the same Canvas
    """
    def __init__(self, canvas, x, y, width, height, image_filename, variable, value, text_label, mode="radio", command=None, radius=25):
        
        # 1. Basic parameters
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.variable = variable
        self.value = value
        self.mode = mode
        self.user_command = command
        self.text_label = text_label 
        
        # 2. Icon size (adjusted proportionally based on button height)
        # Original: button height 55, icon 35, ratio about 0.64
        icon_size = int(height * 0.64)  # Dynamically adjust based on button height
        
        # 3. Load and process icon
        self.icon_normal_img = None
        self.icon_inverted_img = None
        
        if HAS_PIL:
            icon_path = f"icon/{image_filename}" if not image_filename.startswith("icon/") else image_filename
            if not os.path.exists(icon_path) and os.path.exists(image_filename):
                icon_path = image_filename
            
            try:
                raw_icon = Image.open(icon_path)
                raw_icon = make_transparent(raw_icon)
                raw_icon = raw_icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                icon_normal = raw_icon.copy()
                icon_inverted = invert_icon(raw_icon)
                
                # Convert to Tkinter PhotoImage
                self.icon_normal_img = ImageTk.PhotoImage(icon_normal)
                self.icon_inverted_img = ImageTk.PhotoImage(icon_inverted)
                # Save reference to prevent garbage collection
                self._icon_images = [self.icon_normal_img, self.icon_inverted_img]
            except Exception as e:
                print(f"Error loading icon {image_filename}: {e}")
        
        # 4. Store Canvas object IDs
        self.bg_rect_id = None
        self.border_rect_id = None
        self.icon_id = None
        self.text_id = None
        
        # 5. Initial draw (draw_button will automatically bind events)
        self.draw_button(selected=False)

    def draw_button(self, selected=False):
        """Draw button on Canvas"""
        x1, y1 = self.x - self.width // 2, self.y - self.height // 2
        x2, y2 = self.x + self.width // 2, self.y + self.height // 2
        
        # Clear previous content (reset IDs first to avoid binding to deleted elements)
        if self.bg_rect_id:
            self.canvas.delete(self.bg_rect_id)
            self.bg_rect_id = None
        if self.border_rect_id:
            self.canvas.delete(self.border_rect_id)
            self.border_rect_id = None
        if self.icon_id:
            self.canvas.delete(self.icon_id)
            self.icon_id = None
        if self.text_id:
            self.canvas.delete(self.text_id)
            self.text_id = None
        
        # Use unified tag to identify all elements of this button
        button_tag = f"button_{id(self)}"
        
        if selected:
            # Selected state: black background, white text
            bg_color = "black"
            border_color = None
            text_color = "white"
            icon_img = self.icon_inverted_img
        else:
            # Unselected state: white background, black text (no border)
            bg_color = "white"
            border_color = None  # No border
            text_color = "black"
            icon_img = self.icon_normal_img
        
        # 1. Draw rounded rectangle background
        if border_color:
            # With border: draw border first, then background
            self.border_rect_id = create_round_rect_canvas(
                self.canvas, x1, y1, x2, y2, 
                radius=self.radius, 
                fill=border_color, 
                outline="",
                tags=button_tag
            )
            
            self.bg_rect_id = create_round_rect_canvas(
                self.canvas, x1+2, y1+2, x2-2, y2-2, 
                radius=max(self.radius-2, 1), 
                fill=bg_color, 
                outline="",
                tags=button_tag
            )
        else:
            # No border: draw background directly
            self.bg_rect_id = create_round_rect_canvas(
                self.canvas, x1, y1, x2, y2, 
                radius=self.radius, 
                fill=bg_color, 
                outline="",
                tags=button_tag
            )
        
        # 2. Draw icon (if any)
        icon_spacing = 15  # Fixed spacing between icon and text
        icon_offset = 25  # Distance from icon to left edge
        
        if icon_img:
            # Calculate icon size (consistent with initialization)
            icon_size = int(self.height * 0.64)
            icon_x = x1 + icon_offset + icon_size // 2  # Icon center position
            icon_y = self.y
            self.icon_id = self.canvas.create_image(icon_x, icon_y, image=icon_img, anchor="center", tags=button_tag)
            
            # 3. Draw text (to the right of icon, maintaining fixed spacing)
            font_size = max(9, int(self.height * 0.2))  # Dynamically adjust font size based on button height
            text_x = icon_x + icon_size // 2 + icon_spacing  # Text left edge position
            self.text_id = self.canvas.create_text(
                text_x, self.y, 
                text=self.text_label, 
                font=("Arial", font_size, "bold"), 
                fill=text_color, 
                anchor="w",  # Left align, ensure text starts from fixed position
                tags=button_tag
            )
        else:
            # If no icon, center text
            font_size = max(9, int(self.height * 0.2))
            self.text_id = self.canvas.create_text(
                self.x, self.y, 
                text=self.text_label, 
                font=("Arial", font_size, "bold"), 
                fill=text_color, 
                anchor="center",
                tags=button_tag
            )
        
        # Bind events using unified tag (more reliable)
        self.canvas.tag_bind(button_tag, "<Button-1>", lambda e: self.on_click())
        self.canvas.tag_bind(button_tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(button_tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def on_click(self):
        # Logic processing
        if self.mode == "radio":
            current_value = self.variable.get()
            if current_value == self.value:
                self.variable.set("") # Deselect
            else:
                self.variable.set(self.value)
        elif self.mode == "check":
            current = self.variable.get()
            self.variable.set(not current)

        # Update appearance
        self.update_appearance()

        # Trigger callback
        if self.user_command:
            self.user_command() 

    def update_appearance(self):
        """Update UI based on current variable state - redraw button"""
        is_selected = False
        if self.mode == "radio":
            is_selected = (self.variable.get() == self.value and self.variable.get() != "")
        elif self.mode == "check":
            is_selected = self.variable.get()
        
        # Redraw button (white bg black text <-> black bg white text)
        self.draw_button(selected=is_selected)


# ==========================================
# Page F4: Filter Page (Core Modified Page)
# ==========================================

class FilterPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        
        # 1. Background layer
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0) 
        self.canvas.pack(fill="both", expand=True)
        
        self.bg_img = load_simple_image("filter_bg.png", WINDOW_WIDTH, WINDOW_HEIGHT)
        if self.bg_img:
             self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.bg_img, anchor="center")

        # 2. Create components directly on Canvas, not using large Frame container
        # Calculate layout positions
        start_x = WINDOW_WIDTH // 2
        start_y = 100  # Title starting position
        offset_y = 50  # Overall downward translation distance
        col_width = 280  # Column width
        row_height = 70  # Row height
        
        # Button size (scaled down proportionally)
        btn_scale = 0.85  # Scale ratio (85%)
        btn_width = int(220 * btn_scale)  # 187
        btn_height = int(55 * btn_scale)   # 47
        btn_radius = int(25 * btn_scale)   # 21

        # --- Top title ---
        self.canvas.create_text(start_x, start_y + 30, text="Your Choices", 
                               font=("Arial", 32, "bold"), fill="#001540", anchor="center")

        self.buttons = [] 

        # === Column 1: Room Type (Radio) ===
        col1_x = start_x - col_width
        # Title position: about 50 pixels above first button (consistent with PRICE RANGE and input box distance)
        self.canvas.create_text(col1_x, start_y + 50 + offset_y, text="ROOM TYPE", 
                               font=FONT_SECTION, fill="#001540", anchor="center")
        
        # Room Type changed to multi-select mode (each option has independent BooleanVar)
        self.room_twin = tk.BooleanVar(value=False)
        self.room_double = tk.BooleanVar(value=False)
        self.room_suite = tk.BooleanVar(value=False)
        
        room_types = [
            ("icon_twin.png", self.room_twin, "TWIN"),
            ("icon_double.png", self.room_double, "DOUBLE"),
            ("icon_suite.png", self.room_suite, "SUITE")
        ]
        
        for i, (icon, var, label) in enumerate(room_types):
            btn = CanvasButton(self.canvas,
                              x=col1_x,
                              y=start_y + 100 + offset_y + i * row_height,
                              width=btn_width,
                              height=btn_height,
                              image_filename=icon,
                              variable=var,
                              value=True,
                              text_label=label,
                              mode="check",  # Changed to multi-select mode
                              command=self.refresh_ui,
                              radius=btn_radius)
            self.buttons.append(btn)

        # === Column 2: Preferences ===
        col2_x = start_x
        # Title position: about 50 pixels above first button
        self.canvas.create_text(col2_x, start_y + 50 + offset_y, text="PREFERENCES", 
                               font=FONT_SECTION, fill="#001540", anchor="center")
        
        self.floor_var = tk.StringVar(value="") 
        self.pref_pet = tk.BooleanVar(value=False)
        self.pref_smoke = tk.BooleanVar(value=False)

        # Floor (Radio)
        btn_low = CanvasButton(self.canvas, col2_x, start_y + 100 + offset_y, btn_width, btn_height, "icon_low.png", self.floor_var, "Low", "LOW FLOOR", mode="radio", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_low)
        
        btn_high = CanvasButton(self.canvas, col2_x, start_y + 100 + offset_y + row_height, btn_width, btn_height, "icon_high.png", self.floor_var, "High", "HIGH FLOOR", mode="radio", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_high)

        # Pet & Smoking (Check)
        btn_pet = CanvasButton(self.canvas, col2_x, start_y + 100 + offset_y + 2 * row_height, btn_width, btn_height, "icon_pet.png", self.pref_pet, True, "PET FRIENDLY", mode="check", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_pet)

        btn_smoke = CanvasButton(self.canvas, col2_x, start_y + 100 + offset_y + 3 * row_height, btn_width, btn_height, "icon_smoking.png", self.pref_smoke, True, "SMOKING", mode="check", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_smoke)

        # === Column 3: Add-on Services & Price ===
        col3_x = start_x + col_width
        # Title position: about 50 pixels above first button (consistent with PRICE RANGE and input box distance)
        self.canvas.create_text(col3_x, start_y + 50 + offset_y, text="ADD-ON SERVICES", 
                               font=FONT_SECTION, fill="#001540", anchor="center")
        
        self.pref_shuttle = tk.BooleanVar(value=False)
        self.pref_breakfast = tk.BooleanVar(value=False)

        btn_shuttle = CanvasButton(self.canvas, col3_x, start_y + 100 + offset_y, btn_width, btn_height, "icon_shuttle.png", self.pref_shuttle, True, "AIRPORT\nSHUTTLE", mode="check", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_shuttle)

        btn_break = CanvasButton(self.canvas, col3_x, start_y + 100 + offset_y + row_height, btn_width, btn_height, "icon_breakfast.png", self.pref_breakfast, True, "BREAKFAST", mode="check", command=self.refresh_ui, radius=btn_radius)
        self.buttons.append(btn_break)

        # --- Price Range ---
        self.canvas.create_text(col3_x, start_y + 100 + offset_y + 2 * row_height + 20, text="PRICE RANGE", 
                               font=FONT_SECTION, fill="#001540", anchor="center")
        
        # Use rounded rectangle background (same appearance as buttons, aligned with SMOKING button)
        price_y = start_y + 100 + offset_y + 3 * row_height
        price_w, price_h = btn_width, btn_height  # Same size as buttons
        price_x1 = col3_x - price_w // 2
        price_y1 = price_y - price_h // 2
        price_x2 = col3_x + price_w // 2
        price_y2 = price_y + price_h // 2
        
        # Draw rounded rectangle background (white background only, no border)
        price_bg_tag = f"price_bg_{id(self)}"
        create_round_rect_canvas(
            self.canvas, price_x1, price_y1, price_x2, price_y2,
            radius=btn_radius,
            fill="white",
            outline="",
            tags=price_bg_tag
        )
        
        # Create input box container (white background, blends with rounded rectangle background)
        price_container = tk.Frame(self.canvas, bg="white", highlightthickness=0)
        self.canvas.create_window(col3_x, price_y, window=price_container, width=price_w-20, height=price_h-10)
        
        # Create input boxes (white background, no border)
        entry_frame = tk.Frame(price_container, bg="white", highlightthickness=0)
        entry_frame.pack(expand=True, fill="both")
        
        entry_font_size = max(9, int(btn_height * 0.2))  # Adjust font size based on button height
        self.entry_min = tk.Entry(entry_frame, width=6, bd=0, bg="white", 
                                  justify="center", font=("Arial", entry_font_size, "bold"),
                                  highlightthickness=0, relief="flat",
                                  insertbackground="black")  # Cursor color
        self.entry_min.pack(side="left", padx=5, expand=True)
        
        # Middle horizontal line separator
        separator_label = tk.Label(entry_frame, text="-", bg="white", 
                                   fg="black", font=("Arial", entry_font_size, "bold"),
                                   highlightthickness=0)
        separator_label.pack(side="left", padx=2)
        
        self.entry_max = tk.Entry(entry_frame, width=6, bd=0, bg="white",
                                  justify="center", font=("Arial", entry_font_size, "bold"),
                                  highlightthickness=0, relief="flat",
                                  insertbackground="black")  # Cursor color
        self.entry_max.pack(side="left", padx=5, expand=True)

        # === Bottom navigation buttons (blue rounded rectangles) ===
        nav_y = WINDOW_HEIGHT - 50  # Translate downward, 50 pixels from bottom
        nav_btn_w, nav_btn_h = 180, 45  # Button size
        nav_btn_radius = 22  # Rounded corner radius
        nav_btn_spacing = 40  # Spacing between two buttons
        
        # Calculate button positions (two buttons centered with spacing between)
        nav_btn_left_x = start_x - (nav_btn_w + nav_btn_spacing) // 2
        nav_btn_right_x = start_x + (nav_btn_w + nav_btn_spacing) // 2
        
        # Left button: Back to main menu
        back_x1 = nav_btn_left_x - nav_btn_w // 2
        back_y1 = nav_y - nav_btn_h // 2
        back_x2 = nav_btn_left_x + nav_btn_w // 2
        back_y2 = nav_y + nav_btn_h // 2
        
        back_bg_tag = f"nav_back_{id(self)}"
        create_round_rect_canvas(
            self.canvas, back_x1, back_y1, back_x2, back_y2,
            radius=nav_btn_radius,
            fill=NAV_BTN_BG,
            outline="",
            tags=back_bg_tag
        )
        back_text_id = self.canvas.create_text(
            nav_btn_left_x, nav_y,
            text="Back to main menu",
            font=("Arial", 12, "bold"),
            fill=NAV_BTN_FG,
            anchor="center",
            tags=back_bg_tag
        )
        self.canvas.tag_bind(back_bg_tag, "<Button-1>", lambda e: self.on_back_to_main())
        self.canvas.tag_bind(back_bg_tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(back_bg_tag, "<Leave>", lambda e: self.canvas.config(cursor=""))
        
        # Right button: Search Rooms
        search_x1 = nav_btn_right_x - nav_btn_w // 2
        search_y1 = nav_y - nav_btn_h // 2
        search_x2 = nav_btn_right_x + nav_btn_w // 2
        search_y2 = nav_y + nav_btn_h // 2
        
        search_bg_tag = f"nav_search_{id(self)}"
        create_round_rect_canvas(
            self.canvas, search_x1, search_y1, search_x2, search_y2,
            radius=nav_btn_radius,
            fill=NAV_BTN_BG,
            outline="",
            tags=search_bg_tag
        )
        search_text_id = self.canvas.create_text(
            nav_btn_right_x, nav_y,
            text="Search Rooms",
            font=("Arial", 12, "bold"),
            fill=NAV_BTN_FG,
            anchor="center",
            tags=search_bg_tag
        )
        self.canvas.tag_bind(search_bg_tag, "<Button-1>", lambda e: self.on_search())
        self.canvas.tag_bind(search_bg_tag, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(search_bg_tag, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def refresh_ui(self):
        """Notify all buttons to update their state"""
        for btn in self.buttons:
            btn.update_appearance()
    
    def clear_all_selections(self):
        """Clear all selections"""
        # Clear room type selections
        self.room_twin.set(False)
        self.room_double.set(False)
        self.room_suite.set(False)
        
        # Clear floor selection
        self.floor_var.set("")
        
        # Clear preference selections
        self.pref_pet.set(False)
        self.pref_smoke.set(False)
        
        # Clear add-on service selections
        self.pref_shuttle.set(False)
        self.pref_breakfast.set(False)
        
        # Clear price inputs
        self.entry_min.delete(0, tk.END)
        self.entry_max.delete(0, tk.END)
        
        # Update all button appearances
        self.refresh_ui()
    
    def on_back_to_main(self):
        """Clear all selections before returning to main page"""
        self.clear_all_selections()
        self.controller.show_frame("WelcomePage")

    def on_search(self):
        # Collect data
        # Room Type now supports multi-select, collect all selected room types
        selected_rooms = []
        if self.room_twin.get():
            selected_rooms.append("Twin")
        if self.room_double.get():
            selected_rooms.append("Double")
        if self.room_suite.get():
            selected_rooms.append("Suite")

        selection = {
            "Room": selected_rooms,  # Now a list
            "Floor": self.floor_var.get(),
            "Pet": self.pref_pet.get(),
            "Smoke": self.pref_smoke.get(),
            "Shuttle": self.pref_shuttle.get(),
            "Breakfast": self.pref_breakfast.get(),
            "MinPrice": self.entry_min.get(),
            "MaxPrice": self.entry_max.get()
        }

        # Save filter to controller
        self.controller.current_filter = selection

        # Navigate to search results page
        self.controller.show_frame("SearchResultsPage")

# ==========================================
# Page F1: Welcome Page
# ==========================================

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.bg_img = load_simple_image("welcome_bg.png", WINDOW_WIDTH, WINDOW_HEIGHT)
        if self.bg_img:
            self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.bg_img, anchor="center")
        
        # Nav Bar
        nav_bar = tk.Frame(self, bg="white", height=60)
        nav_bar.place(x=0, y=0, width=WINDOW_WIDTH, height=60)
        tk.Label(nav_bar, text="TVXK HOTEL", font=("Arial", 16, "bold"), bg="white").pack(side="left", padx=30)
        nav_frame = tk.Frame(nav_bar, bg="white")
        nav_frame.pack(side="right", padx=30)
        for t, p in [("Rooms","RoomsPage"), ("Location","LocationPage"), ("About us","AboutUsPage")]:
            tk.Button(nav_frame, text=t, font=("Arial", 11, "bold"), bg="white", relief="flat", 
                      cursor="hand2", command=lambda p=p: controller.show_frame(p)).pack(side="left", padx=15)

        # Buttons
        btn_book = tk.Button(self.canvas, text="BOOK NOW", font=("Arial", 12, "bold"),
                             bg=SECONDARY_COLOR, fg="black", width=30, height=2, relief="flat",
                             cursor="hand2", command=lambda: controller.show_frame("DateSelectionPage"))
        self.canvas.create_window(WINDOW_WIDTH//2 - 180, WINDOW_HEIGHT - 80, window=btn_book, anchor="center")

        btn_manage = tk.Button(self.canvas, text="MANAGE BOOKING", font=("Arial", 12, "bold"),
                               bg=SECONDARY_COLOR, fg="black", width=30, height=2, relief="flat",
                               cursor="hand2", command=lambda: controller.show_frame("ManageBookingPage"))
        self.canvas.create_window(WINDOW_WIDTH//2 + 180, WINDOW_HEIGHT - 80, window=btn_manage, anchor="center")

# ==========================================
# Page F11: Manage Booking
# ==========================================

class ManageBookingPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="black")
        self.controller = controller
        
        # 1. Canvas as main container
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 2. Load background image (maintain original size 900x600)
        self.bg_img = load_simple_image("booking_bg.png", WINDOW_WIDTH, WINDOW_HEIGHT)
        if self.bg_img:
            self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.bg_img, anchor="center")
        
        # 3. Right side white rounded card (top doesn't exceed main area of background image)
        card_width = 390  # Tighten width
        card_height = 440  # Further compress height
        card_x = WINDOW_WIDTH - card_width - 25  # 25px from right edge
        card_y = 80  # Top position, overall downward translation
        
        card_x1 = card_x
        card_y1 = card_y
        card_x2 = card_x + card_width
        card_y2 = card_y + card_height
        
        # Draw rounded rectangle card (white background)
        card_tag = f"manage_card_{id(self)}"
        create_round_rect_canvas(
            self.canvas, card_x1, card_y1, card_x2, card_y2,
            radius=25,
            fill="white",
            outline="",
            tags=card_tag
        )
        
        # 5. Create content container on card (adjust position to move content upward, remove border occlusion)
        card_container = tk.Frame(self.canvas, bg="white", highlightthickness=0, relief="flat", bd=0)
        # Adjust window position to move content upward
        container_y_offset = -20  # Upward offset
        # Remove border when creating window
        window_id = self.canvas.create_window(card_x + card_width//2, card_y + card_height//2 + container_y_offset, 
                                              window=card_container, width=card_width-70, height=card_height-70)
        # Ensure window has no border
        self.canvas.itemconfig(window_id, state="normal")
        
        # 6. Title (moved to top)
        title_label = tk.Label(card_container, text="Manage Your Booking", 
                               font=("Arial", 22, "bold"), bg="white", fg="black")
        title_label.pack(pady=(2, 8), anchor="w")  # Top padding set to 2px, close to top
        
        # 7. Instruction text (reduce spacing to 1/2)
        instruction_label = tk.Label(card_container, 
                                    text="Please enter the name and reservation number as they appear on your reservation confirmation.",
                                    font=("Arial", 9), bg="white", fg="#666666", wraplength=card_width-90, justify="left")
        instruction_label.pack(pady=(0, 5), anchor="w")  # 10 * 1/2 = 5
        
        # 8. Input container (reduce spacing to 1/2)
        input_frame = tk.Frame(card_container, bg="white")
        input_frame.pack(fill="x", pady=(0, 4))  # 7 * 1/2 ≈ 4
        
        # First Name (reduce spacing and padding to 1/2, further thin border)
        firstname_label = tk.Label(input_frame, text="First Name", font=("Arial", 10, "bold"), bg="white", fg="black", anchor="w")
        firstname_label.pack(fill="x", pady=(0, 2))  # 3 * 1/2 ≈ 2
        self.entry_firstname = tk.Entry(input_frame, font=("Arial", 10), bg="#F5F5F5", 
                                        relief="flat", bd=2, highlightthickness=0, insertbackground="black")
        self.entry_firstname.pack(fill="x", pady=(0, 4), ipady=2)  # 7 * 1/2 ≈ 4, 4 * 1/2 = 2
        
        # Last Name (reduce spacing and padding to 1/2, further thin border)
        lastname_label = tk.Label(input_frame, text="Last Name", font=("Arial", 10, "bold"), bg="white", fg="black", anchor="w")
        lastname_label.pack(fill="x", pady=(0, 2))  # 3 * 1/2 ≈ 2
        self.entry_lastname = tk.Entry(input_frame, font=("Arial", 10), bg="#F5F5F5", 
                                       relief="flat", bd=2, highlightthickness=0, insertbackground="black")
        self.entry_lastname.pack(fill="x", pady=(0, 4), ipady=2)  # 7 * 1/2 ≈ 4, 4 * 1/2 = 2
        
        # Booking Number (reduce spacing and padding to 1/2, further thin border)
        booking_label = tk.Label(input_frame, text="Booking Number", font=("Arial", 10, "bold"), bg="white", fg="black", anchor="w")
        booking_label.pack(fill="x", pady=(0, 2))  # 3 * 1/2 ≈ 2
        self.entry_code = tk.Entry(input_frame, font=("Arial", 10), bg="#F5F5F5", 
                                   relief="flat", bd=2, highlightthickness=0, insertbackground="black")
        self.entry_code.pack(fill="x", pady=(0, 0), ipady=2)  # Remove bottom spacing, stick to button
        
        # 9. Result label (for displaying search results, reduce spacing)
        self.result_label = tk.Label(card_container, text="", font=("Arial", 11), bg="white", fg="green")
        self.result_label.pack(pady=(3, 0))  # Reduce spacing
        
        # 10. Button container (ensure buttons are inside card and not occluded, stick to input box)
        button_frame = tk.Frame(card_container, bg="white")
        button_frame.pack(fill="x", pady=(0, 0))  # Remove top spacing, stick to input box
        
        # Button size (adapt to container width)
        container_width = card_width - 70
        btn_w = container_width
        btn_h = 32
        
        # Log in button Canvas (black background, white text, placed above Back button)
        login_canvas = tk.Canvas(button_frame, bg="white", width=btn_w, height=btn_h, highlightthickness=0)
        login_canvas.pack(fill="x", pady=(0, 0))
        login_btn_x = btn_w // 2
        login_btn_y = btn_h // 2
        login_btn_tag = f"login_btn_{id(self)}"
        create_round_rect_canvas(
            login_canvas, 0, 0, btn_w, btn_h,
            radius=6,
            fill="black",
            outline="",
            tags=login_btn_tag
        )
        login_canvas.create_text(login_btn_x, login_btn_y, text="Log in", 
                                font=("Arial", 11, "bold"), fill="white", anchor="center", tags=login_btn_tag)
        login_canvas.tag_bind(login_btn_tag, "<Button-1>", lambda e: self.perform_search())
        login_canvas.tag_bind(login_btn_tag, "<Enter>", lambda e: login_canvas.config(cursor="hand2"))
        login_canvas.tag_bind(login_btn_tag, "<Leave>", lambda e: login_canvas.config(cursor=""))
        
        # Or separator line (in the middle between Log in and Back buttons, reduce spacing)
        separator_frame = tk.Frame(button_frame, bg="white", height=16)
        separator_frame.pack(fill="x", pady=(2, 2))  # Reduce spacing, close but not overlapping
        separator_canvas = tk.Canvas(separator_frame, bg="white", width=btn_w, height=16, highlightthickness=0)
        separator_canvas.pack(fill="x")
        separator_line_x1 = 35
        separator_line_x2 = btn_w - 35
        separator_canvas.create_line(separator_line_x1, 8, separator_line_x2, 8, 
                                    fill="#E0E0E0", width=0.5)  # Thinner separator line
        # Create white background for "Or" text
        separator_canvas.create_rectangle(btn_w // 2 - 18, 0, 
                                         btn_w // 2 + 18, 16,
                                         fill="white", outline="")
        separator_canvas.create_text(btn_w // 2, 8, text="Or", 
                                    font=("Arial", 10), fill="#999999", anchor="center")
        
        # Back to main menu button Canvas (light blue-green background, black text, placed at bottom)
        back_canvas = tk.Canvas(button_frame, bg="white", width=btn_w, height=btn_h, highlightthickness=0)
        back_canvas.pack(fill="x", pady=(0, 0))
        back_btn_x = btn_w // 2
        back_btn_y = btn_h // 2
        back_btn_tag = f"back_btn_{id(self)}"
        create_round_rect_canvas(
            back_canvas, 0, 0, btn_w, btn_h,
            radius=6,
            fill="#B0E0E6",  # Light blue-green
            outline="",
            tags=back_btn_tag
        )
        back_canvas.create_text(back_btn_x, back_btn_y, text="Back to main menu", 
                               font=("Arial", 11, "bold"), fill="black", anchor="center", tags=back_btn_tag)
        back_canvas.tag_bind(back_btn_tag, "<Button-1>", lambda e: controller.show_frame("WelcomePage"))
        back_canvas.tag_bind(back_btn_tag, "<Enter>", lambda e: back_canvas.config(cursor="hand2"))
        back_canvas.tag_bind(back_btn_tag, "<Leave>", lambda e: back_canvas.config(cursor=""))

    def perform_search(self):
        first_name = self.entry_firstname.get().strip()
        last_name = self.entry_lastname.get().strip()
        code = self.entry_code.get().strip()

        # Import the booking storage function
        from booking_storage import find_booking_by_code

        # Query using Last Name and Confirmation Code
        booking = find_booking_by_code(last_name, code)
        if booking:
            self.result_label.config(text=f"Found: {booking.get('room_type', 'N/A')} Room", fg="green")
            # Save booking to controller and navigate to view page
            self.controller.current_booking = booking
            self.controller.show_frame("ViewBookingPage")
        else:
            self.result_label.config(text="No booking found.", fg="red")

# ==========================================
# Static Display Page Base Class
# ==========================================

class ImagePageBase(tk.Frame):
    def __init__(self, parent, controller, img_file, title):
        super().__init__(parent, bg="black")
        self.controller = controller
        self.img_file = img_file
        
        # Top navigation
        nav_bar = tk.Frame(self, bg="white", height=60)
        nav_bar.place(x=0, y=0, width=WINDOW_WIDTH, height=60)
        tk.Label(nav_bar, text="TVXK HOTEL", font=("Arial", 16, "bold"), bg="white", fg="black").pack(side="left", padx=30)
        nav_frame = tk.Frame(nav_bar, bg="white")
        nav_frame.pack(side="right", padx=30)
        for t, p in [("Rooms","RoomsPage"), ("Location","LocationPage"), ("About us","AboutUsPage")]:
            tk.Button(nav_frame, text=t, font=("Arial", 11, "bold"), bg="white", fg="black", relief="flat", 
                      cursor="hand2", command=lambda p=p: controller.show_frame(p)).pack(side="left", padx=15)
        
        # Bottom return bar
        bar = tk.Frame(self, bg="white", height=50)
        bar.place(x=0, y=WINDOW_HEIGHT-50, width=WINDOW_WIDTH, height=50)
        tk.Button(bar, text="← Back", command=lambda: controller.show_frame("WelcomePage"), 
                  relief="flat", bg="white", fg="black", cursor="hand2").pack(side="left", padx=20)
        tk.Label(bar, text=title, bg="white", fg="black", font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.bind("<<ShowPage>>", self.load)
        nav_bar.lift()
        bar.lift()

    def load(self, event=None):
        if not hasattr(self, 'tk_img'):
            # Maintain image original size 900x600, no scaling
            self.tk_img = load_simple_image(self.img_file, WINDOW_WIDTH, WINDOW_HEIGHT)
            if self.tk_img: 
                self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, image=self.tk_img, anchor="center")

class RoomsPage(ImagePageBase):
    def __init__(self, parent, controller): 
        super().__init__(parent, controller, "rooms_img.png", "Rooms")

class LocationPage(ImagePageBase):
    def __init__(self, parent, controller): 
        super().__init__(parent, controller, "location_img.png", "Location")

class AboutUsPage(ImagePageBase):
    def __init__(self, parent, controller): 
        super().__init__(parent, controller, "about_img.png", "About Us")

# ==========================================
# Main Program Entry
# ==========================================

class TVXKHotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TVXK Hotel Booking System - Group 18")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Register all pages
        all_pages = (
            WelcomePage,
            FilterPage,
            ManageBookingPage,
            RoomsPage,
            LocationPage,
            AboutUsPage,
            # Booking flow pages
            DateSelectionPage,
            SearchResultsPage,
            GuestInfoPage,  # F3+F6 合并在一起
            SummaryPage,
            PaymentPage,
            ConfirmationPage,
            # Manage booking pages
            ViewBookingPage,
            ModifyBookingPage,
            CancelBookingPage,
        )

        for F in all_pages:
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")
        
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        frame.event_generate("<<ShowPage>>")

if __name__ == "__main__":
    if os.environ.get('DISPLAY', '') == '' and os.name != 'nt': 
        print("Run locally.")
    else: 
        app = TVXKHotelApp()
        app.mainloop()
