#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to check if tkcalendar DateEntry works
"""

import sys
import io

# Fix encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import tkinter as tk

try:
    from tkcalendar import DateEntry
    print("✓ tkcalendar imported successfully")
    HAS_TKCALENDAR = True
except ImportError as e:
    print(f"✗ Failed to import tkcalendar: {e}")
    HAS_TKCALENDAR = False
    exit(1)

# Create test window
root = tk.Tk()
root.title("Calendar Test")
root.geometry("400x300")

tk.Label(root, text="Testing DateEntry Widget", font=("Arial", 14, "bold")).pack(pady=20)

# Create DateEntry
try:
    cal = DateEntry(root, date_pattern="yyyy-mm-dd", width=20)
    cal.pack(pady=10)
    print("✓ DateEntry widget created successfully")

    tk.Label(root, text="If you see a calendar dropdown above, it works!",
             font=("Arial", 10)).pack(pady=20)

    def show_date():
        print(f"Selected date: {cal.get()}")
        tk.messagebox.showinfo("Date", f"Selected: {cal.get()}")

    tk.Button(root, text="Get Selected Date", command=show_date).pack(pady=10)

    print("\n=== Calendar test window opened ===")
    print("Click on the DateEntry field to see the calendar dropdown")
    print("Close the window when done testing\n")

    root.mainloop()

except Exception as e:
    print(f"✗ Error creating DateEntry: {e}")
    import traceback
    traceback.print_exc()
