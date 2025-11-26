#Fix the issue where the modify function cannot change the bill price

from tkinter import Tk

class EditBookingPage(Tk.frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.initial_order = None #Keep amended booking.

        tk.Label(self, text='Edit Booking Services', font=('Aptos', 12)).pack(pady=12)

        #Amendable Services.
        self.breakfast_var = tk.BooleanVar()
        self.shuttle_var = tk.BooleanVar()

        tk.Checkbutton(self, text='Would you like to add breakfast as an option? ($40/night)', variable=self.breakfast_var, command=self.recalculate).pack(anchor='w', pady=8)
        tk.Checkbutton(self, text='Do you require transportation to & from YYZ? ($25 flat rate)', variable=self.shuttle_var, command=self.recalculate).pack(anchor='w', pady=8)

        tk.Label(self, text='---').pack(pady=8)
        tk.Label(self, text='Initial Total:').pack(anchor='w')
        self.original_price_label = tk.Label(self, text="$0")
        self.original_price_label.pack(anchor='w')

        tk.Label(self, text='Final Total:').pack(anchor='w')
        self.new_price_label = tk.Label(self, text="$0", font=('Aptos', 14, 'bold'))
        self.new_price_label.pack(anchor='w')

        tk.Button(self, text='Confirm Amendments', command=self.confirm_changes).pack(pady=15)

    def display_summary_of_charges(self, charges):
        """Begin editing with ManageBookingPage"""
        self.initial_order = order

        #Use the current order to establish original values.
        self.breakfast_var.set(order.get('add_breakfast', False))
        self.breakfast_var.set(order.get('add_shuttle', False))

        initial_total = order['summary_of_charges']['grand_total']
        self.initial_price_label.config(text=f"${initial_total:.2f}")

        self.recalculate() #Get new base price.

    def recalculate(self):
        """
        Update label after re-totalling the price.
        """
        if not self.initial_order:
            return

        new_summary_of_charges = total_up_price(
            self.initial_order['room_type'],
            self.initial_order['no_nights'],
            self.breakfast_var.get(),
            self.shuttle_var.get()
        )

        self.new_price_label.config(text=f"${new_summary_of_charges['grand_total']:.2f}")
        self.new_summary_of_charges = new_summary_of_charges #Must be saved to storage.

    def confirm_changes(self):
        """
        JSON file will save the new information based on Group C's logic.
        """
        if not self.initial_order:
            return

        new_info_for_storage = {
            'add_breakfast': self.breakfast_var.get(),
            'add_shuttle': self.shuttle_var.get(),
            'summary_of_charges': self.new_summary_of_charges, #Save new total.
        }

        successful = update_booking(
            self.initial_order['last_name'],
            self.initial_order['confirmation_code'],
            new_info_for_storage
        )

        if successful:
            messagebox.showinfo('Completed!', f'Booking Confirmed Successfully')
            self.controller.show_frame('HomePage')
        else:
            messagebox.showerror('Error!', f'Booking Confirmed Failed')

        #New frame should update ManageBookingPage

        #Amend 'Edit' Button handler:
        self.edit_button = tk.Button(self, text='Edit Booking', command=self.editing_path)
        self.edit_button.pack(pady=10)

    def editing_path(self):
        if self.existing_order:
            self.controller.frames['EditBookingPage'].display_order(self.existing_order)
            self.controller.show_frame('EditBookingPage')