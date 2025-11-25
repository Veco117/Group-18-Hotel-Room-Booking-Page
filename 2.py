#Fix the issue where users cannot increase the bill price when adding breakfast and shuttle services.

class BookingPage1(tk.Frame):
    def __init__(self, parent, controller):

        #Breakfast
        self.breakfast_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Would you like to add breakfast as an option? ($20/night)", variable=self.breakfast_var).pack(anchor='w', pady=10)

        #Airport Shuttle Service
        self.shuttle_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self, text="Do you need transportation to/from YYZ? ($25 flat rate)", variable=self.shuttle_var).pack(anchor='w', pady=10)

        tk.Button(self, text="Next step: User Details", command=self.next_step).pack(pady=15)

    def next_step(self):
        selected_room - self.selected_room_var.get()
        add_breakfast = self.breakfast_var.get()
        add_shuttle = self.shuttle_var.get()
        no_nights = 1

        #Total up the price (with shuttle included)
        summary_of_charges = calculate_price(selected_room, no_nights, add_breakfast, add_shuttle)

        #Secure info to proceed
        self.controller.current_booking_data = {
            'add breakfast': add_breakfast,
            'add shuttle': add_shuttle,
            'total price': summary_of_charges
        }

        self.controller.show_frame("UserDetails")
