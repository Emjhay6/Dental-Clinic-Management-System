from OOP_CLINIC import Dental_Clinic
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import datetime

#Widgets
class Widgets(tk.Frame):
    def __init__(self, master, clinic):
        super().__init__(master, bg="#9CE3FF")
        self.clinic = clinic

    def pack_fill(self):
        self.pack(expand=True, fill="both")

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def entry(self, text):
        tk.Label(self, text=text, bg="#9CE3FF", font=("Arial", 10)).pack()
        e = tk.Entry(self)
        e.pack()
        return e

    def combobox(self, text, values):
        tk.Label(self, text=text, bg="#9CE3FF", font=("Arial", 10)).pack()
        var = tk.StringVar()
        cb = ttk.Combobox(self, textvariable=var, values=values, state="readonly")
        cb.pack()
        return var, cb

    def listbox(self, text, items):
        tk.Label(self, text=text, bg="#9CE3FF", font=("Arial", 10)).pack()
        lb = tk.Listbox(self, selectmode=tk.MULTIPLE, height=6, width=50, exportselection=False)
        for it in items:
            lb.insert(tk.END, it)
        lb.pack()
        return lb

#Searh Patient GUI
class Search_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Search Patients", font=("Arial", 18, "bold"), bg="#9CE3FF").pack(pady=10)
        self.name = self.entry("Patient Name:")

        tk.Button(self, text="Search", command=self.search, width=10).pack(pady=20, side="bottom")

    def search(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showerror("Error", "Patient name is required.")
            return
        
        if clinic.search_patient(name):
            columns = ("Patient", "Service", "Reason", "Tooth Placement", "Tooth Number", "Price", "Dentist")
            tree = ttk.Treeview(self, columns=columns, show="headings")
            tree.pack(expand=True, fill="both")
            widths = [120, 120, 95, 90, 150, 55, 75]
            for col, w in zip(columns, widths):
                tree.heading(col, text=col)
                tree.column(col, width=w)

            clinic.cursor.execute("""
                SELECT patient_name, service, reason, teeth_placement, teeth_number, price, dentist
                FROM history WHERE patient_name = ?""", (name,))
            records = clinic.cursor.fetchall()

            if not records:
                messagebox.showinfo("Info", "No patient history found.")
                return

            for r in records:
                patient, service, reason, placement, tooth_num, price, dentist = r
                tooth_full = f"{int(tooth_num)} - {clinic.tooth_names.get(int(tooth_num), '')}" if tooth_num and str(tooth_num).isdigit() else ""
                tree.insert("", tk.END, values=(patient, service, reason or "", placement or "", tooth_full, f"₱{price}", dentist or ""))
        else:
            messagebox.showinfo("Info", "No Patient Found.")

#Appointment GUI
class Appointment_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Book Appointment", font=("Arial", 18, "bold"), bg="#9CE3FF").pack(pady=10)

        self.name = self.entry("Patient Name:")
        self.age = self.entry("Age:")
        self.contact = self.entry("Contact:")
        self.dentist_var, _ = self.combobox("Choose Dentist:", clinic.dentist)

        self.time = self.entry("Preferred Time (e.g., 10:00):")
        self.date = self.entry("Preferred Date (YYYY-MM-DD):")

        self.services_lb = self.listbox("Choose Services:", clinic.get_services())
        self.reason_var, _ = self.combobox("Reason:", clinic.reason)

        self.placement_label = tk.Label(self, text="Teeth Placement:", bg="#9CE3FF", font=("Arial", 10))
        self.placement_var = tk.StringVar()
        self.placement_menu = ttk.Combobox(self, textvariable=self.placement_var, values=clinic.tooth_placement, state="readonly")

        self.teeth_label = tk.Label(self, text="Teeth Number:", bg="#9CE3FF", font=("Arial", 10))
        self.tooth_var = tk.StringVar()
        self.tooth_menu = ttk.Combobox(self, textvariable=self.tooth_var, width=30)

        self.services_lb.bind("<<ListboxSelect>>", self._check_service)
        self.placement_menu.bind("<<ComboboxSelected>>", self._tooth_place)

        tk.Button(self, text="Submit", command=self.submit, width=10).pack(pady=20, side="bottom")

    def _check_service(self, event=None):
        selected = [self.services_lb.get(i) for i in self.services_lb.curselection()]
        need = any(s in selected for s in ["Tooth Extraction", "Tooth Filling(Pasta)"])
        if need:
            self.placement_label.pack()
            self.placement_menu.pack()
            self.teeth_label.pack()
            self.tooth_menu.pack()
        else:
            self.placement_label.pack_forget()
            self.placement_menu.pack_forget()
            self.teeth_label.pack_forget()
            self.tooth_menu.pack_forget()

    def _tooth_place(self, event=None):
        p = self.placement_var.get()
        nums = range(1, 17) if p == "Upper" else range(17, 33)
        self.tooth_menu["values"] = [f"{n} - {clinic.tooth_names[n]}" for n in nums]

    def submit(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showerror("Error", "Patient name is required.")
            return

        try:
            age = int(self.age.get())
        except:
            messagebox.showerror("Error", "Age must be a number.")
            return
        if age <= 0:
            messagebox.showerror("Error", "Age must be greater than 0.")
            return

        contact = self.contact.get().strip()
        if not contact:
            messagebox.showerror("Error", "Contact is required.")
            return

        dentist_choice = self.dentist_var.get().strip()
        if not dentist_choice or dentist_choice not in clinic.dentist:
            messagebox.showerror("Error", "Please select a valid dentist.")
            return

        selected_services = [self.services_lb.get(i) for i in self.services_lb.curselection()]
        if not selected_services:
            messagebox.showerror("Error", "Please select at least one service.")
            return

        reason_choice = self.reason_var.get().strip()
        if not reason_choice or reason_choice not in clinic.reason:
            messagebox.showerror("Error", "Please select a valid reason.")
            return

        need = any(s in ["Tooth Extraction", "Tooth Filling(Pasta)"] for s in selected_services)
        if need:
            place = self.placement_var.get()
            num = self.tooth_var.get().strip()
            if " - " in num:
                num = num.split(" - ")[0]
            if not place or not num:
                messagebox.showerror("Error", "Teeth placement and teeth number are required.")
                return
        else:
            place = None
            num = None

        time_val = self.time.get().strip()
        date_val = self.date.get().strip()
        if not time_val or not date_val:
            messagebox.showerror("Error", "Please enter time and date.")
            return

        try:
            datetime.datetime.strptime(time_val, "%H:%M")
            datetime.datetime.strptime(date_val, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Time must be HH:MM and Date YYYY-MM-DD.")
            return

        try:
            clinic.cursor.execute("SELECT COUNT(*) FROM appointments WHERE dentist = ? AND time = ? AND date = ?", (dentist_choice, time_val, date_val))
            if clinic.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Slot already taken.")
                return

            clinic.db.conn.execute("BEGIN")
            if not clinic.find_patient(name):
                clinic.cursor.execute("INSERT INTO patients (name, age, contact) VALUES (?, ?, ?)", (name, age, contact))
            clinic.cursor.execute("INSERT INTO appointments (patient_name, dentist, time, date) VALUES (?, ?, ?, ?)", (name, dentist_choice, time_val, date_val))

            total = 0
            for service in selected_services:
                clinic.cursor.execute("SELECT price FROM services WHERE service_name = ?", (service,))
                price = clinic.cursor.fetchone()[0]
                total += price
                clinic.cursor.execute("INSERT INTO history (patient_name, service, reason, teeth_placement, teeth_number, price, dentist) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, service, reason_choice, place, num, price, dentist_choice))
            clinic.db.conn.commit()
            messagebox.showinfo("Result", f"Appointment booked for {name} with {dentist_choice} on {date_val} at {time_val}.\nTotal Cost: ₱{total}")
        except Exception as e:
            clinic.db.conn.rollback()
            messagebox.showerror("Error", str(e))

        self.clear()
        self.build()

#Walk-in GUI
class WalkIn_ui(Appointment_ui):
    def build(self):
        tk.Label(self, text="Walk-In", font=("Arial", 18, "bold"), bg="#9CE3FF").pack(pady=10)

        self.name = self.entry("Patient Name:")
        self.age = self.entry("Age:")
        self.contact = self.entry("Contact:")
        self.dentist_var, _ = self.combobox("Choose Dentist:", clinic.dentist)

        self.services_lb = self.listbox("Choose Services:", clinic.get_services())
        self.reason_var, _ = self.combobox("Reason:", clinic.reason)

        self.placement_label = tk.Label(self, text="Teeth Placement:", bg="#9CE3FF", font=("Arial", 10))
        self.placement_var = tk.StringVar()
        self.placement_menu = ttk.Combobox(self, textvariable=self.placement_var, values=clinic.tooth_placement, state="readonly")

        self.teeth_label = tk.Label(self, text="Teeth Number:", bg="#9CE3FF", font=("Arial", 10))
        self.tooth_var = tk.StringVar()
        self.tooth_menu = ttk.Combobox(self, textvariable=self.tooth_var, width=30)

        self.services_lb.bind("<<ListboxSelect>>", self._check_service)
        self.placement_menu.bind("<<ComboboxSelected>>", self._tooth_place)

        tk.Button(self, text="Submit", command=self.submit, width=10).pack(pady=20, side="bottom")

    def submit(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showerror("Error", "Patient name is required.")
            return

        try:
            age = int(self.age.get())
        except:
            messagebox.showerror("Error", "Age must be a number.")
            return
        if age <= 0:
            messagebox.showerror("Error", "Age must be greater than 0.")
            return

        contact = self.contact.get().strip()
        if not contact:
            messagebox.showerror("Error", "Contact is required.")
            return

        dentist_choice = self.dentist_var.get().strip()
        if not dentist_choice or dentist_choice not in clinic.dentist:
            messagebox.showerror("Error", "Please select a valid dentist.")
            return

        selected_services = [self.services_lb.get(i) for i in self.services_lb.curselection()]
        if not selected_services:
            messagebox.showerror("Error", "Please select at least one service.")
            return

        reason_choice = self.reason_var.get().strip()
        if not reason_choice or reason_choice not in clinic.reason:
            messagebox.showerror("Error", "Please select a valid reason.")
            return

        need = any(s in ["Tooth Extraction", "Tooth Filling(Pasta)"] for s in selected_services)
        if need:
            place = self.placement_var.get()
            num = self.tooth_var.get().strip()
            if " - " in num:
                num = num.split(" - ")[0]
            if not place or not num:
                messagebox.showerror("Error", "Teeth placement and teeth number are required.")
                return
        else:
            place = None
            num = None

        try:
            if not clinic.find_patient(name):
                clinic.cursor.execute("INSERT INTO patients (name, age, contact) VALUES (?, ?, ?)", (name, age, contact))
                clinic.db.conn.commit()

            total = 0
            for service in selected_services:
                clinic.cursor.execute("SELECT price FROM services WHERE service_name = ?", (service,))
                price = clinic.cursor.fetchone()[0]
                total += price
                clinic.cursor.execute("INSERT INTO history (patient_name, service, reason, teeth_placement, teeth_number, price, dentist) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, service, reason_choice, place, num, price, dentist_choice))
            clinic.db.conn.commit()
            messagebox.showinfo("Result", f"Patient {name} Walk-in Successfully.\nTotal Cost: ₱{total}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.clear()
        self.build()

#View Appointment GUI
class View_Appointments_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Appointments", font=("Arial", 18, "bold"), bg="#9CE3FF").pack(pady=10)

        columns = ("Patient", "Dentist", "Time", "Date", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(expand=True, fill="both")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)

        for row in clinic.show_appointments():
            self.tree.insert("", tk.END, values=row)

        tk.Label(self, text="Update Status", font=("Arial", 12, "bold"), bg="#9CE3FF").pack(pady=10)
        self.status_var = tk.StringVar()
        status_box = ttk.Combobox(self, textvariable=self.status_var, values=["Pending", "Completed"], state="readonly")
        status_box.pack()

        tk.Button(self, text="Save Status", command=self.update_status, width=12).pack(pady=10)

    def update_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select an appointment.")
            return
        new_status = self.status_var.get()
        if not new_status:
            messagebox.showerror("Error", "Please choose a status.")
            return
        data = self.tree.item(sel)["values"]
        patient, dentist, time, date, _ = data
        clinic.cursor.execute("UPDATE appointments SET status = ? WHERE patient_name=? AND dentist=? AND time=? AND date=?", (new_status, patient, dentist, time, date))
        clinic.db.conn.commit()
        self.clear()
        self.build()

#Patients Record GUI
class Patient_Record_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Patients Records", font=("Arial", 18, "bold"), bg="#9CE3FF").pack(pady=10)

        columns = ("Patient", "Service", "Reason", "Tooth Placement", "Tooth Number", "Price", "Dentist", "Total Spent")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        tree.pack(expand=True, fill="both")
        widths = [120, 120, 95, 90, 150, 55, 75, 90]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w)

        clinic.cursor.execute("SELECT patient_name, service, reason, teeth_placement, teeth_number, price, dentist FROM history ORDER BY patient_name ASC")
        records = clinic.cursor.fetchall()
        total_spent_dict = {}
        for row in records:
            patient_name = row[0]
            price = row[5]
            if patient_name in total_spent_dict:
                total_spent_dict[patient_name] += price
            else:
                total_spent_dict[patient_name] = price

        for r in records:
            patient, service, reason, placement, tooth_num, price, dentist = r
            tooth_full = f"{int(tooth_num)} - {clinic.tooth_names.get(int(tooth_num), '')}" if tooth_num and str(tooth_num).isdigit() else ""
            total_spent = f"₱{total_spent_dict.get(patient, 0)}"
            tree.insert("", tk.END, values=(patient, service, reason or "", placement or "", tooth_full, f"₱{price}", dentist or "", total_spent))

#Inventory GUI
class Inventory_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Inventory", font=("Arial", 22, "bold"), bg="#9CE3FF").pack(pady=10)
        tree = ttk.Treeview(self, columns=("Item", "Quantity", "Price"), show="headings")
        tree.pack(expand=True, fill="both")
        for col in ("Item", "Quantity", "Price"):
            tree.heading(col, text=col)
        clinic.cursor.execute("SELECT item, qty, price FROM inventory")
        for row in clinic.cursor.fetchall():
            tree.insert("", tk.END, values=row)

#Sell Product GUI
class Sell_Item_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Sell Product", font=("Arial", 22, "bold"), bg="#9CE3FF").pack(pady=10)
        clinic.cursor.execute("SELECT item FROM inventory")
        items = [i[0] for i in clinic.cursor.fetchall()]
        tk.Label(self, text="Product:", bg="#9CE3FF", font=("Arial", 10)).pack()
        self.item_box = ttk.Combobox(self, values=items, state="readonly")
        self.item_box.pack(pady=10)
        self.qty_entry = self.entry("Quantity:")
        tk.Button(self, text="Submit", command=self.sell, width=10).pack(pady=20, side="bottom")

    def sell(self):
        item = self.item_box.get()
        if not item:
            messagebox.showerror("Error", "Please select an item.")
            return
        try:
            qty = int(self.qty_entry.get())
        except:
            messagebox.showerror("Error", "Quantity must be a number.")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0.")
            return
        clinic.cursor.execute("SELECT qty FROM inventory WHERE item=?", (item,))
        res = clinic.cursor.fetchone()
        if not res:
            messagebox.showerror("Error", "Item not found.")
            return
        if qty > res[0]:
            messagebox.showerror("Error", "Not enough stock.")
            return
        clinic.cursor.execute("UPDATE inventory SET qty = qty - ? WHERE item=?", (qty, item))
        clinic.db.conn.commit()
        messagebox.showinfo("Success", "Item Sold.")
        self.clear()
        Inventory_ui(self.master, self.clinic).pack_fill()

#Restock Item GUI
class Restock_ui(Widgets):
    def __init__(self, master, clinic):
        super().__init__(master, clinic)
        self.build()

    def build(self):
        tk.Label(self, text="Restock Product", font=("Arial", 22, "bold"), bg="#9CE3FF").pack(pady=10)
        clinic.cursor.execute("SELECT item FROM inventory")
        items = [i[0] for i in clinic.cursor.fetchall()]
        tk.Label(self, text="Product:", bg="#9CE3FF", font=("Arial", 10)).pack()
        self.item_box = ttk.Combobox(self, values=items, state="readonly")
        self.item_box.pack(pady=10)
        self.qty_entry = self.entry("Quantity:")
        tk.Button(self, text="Submit", command=self.restock, width=10).pack(pady=20, side="bottom")

    def restock(self):
        item = self.item_box.get()
        if not item:
            messagebox.showerror("Error", "Please select an item.")
            return
        try:
            qty = int(self.qty_entry.get())
        except:
            messagebox.showerror("Error", "Quantity must be a number.")
            return
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0.")
            return
        clinic.cursor.execute("UPDATE inventory SET qty = qty + ? WHERE item=?", (qty, item))
        clinic.db.conn.commit()
        messagebox.showinfo("Success", "Inventory Updated.")
        self.clear()
        Inventory_ui(self.master, self.clinic).pack_fill()

#Main Window GUI
class Main_Window(tk.Tk):
    def __init__(self, clinic):
        super().__init__()
        self.clinic = clinic
        self.title("🦷Dental Clinic System")
        self.geometry("1300x700")

        img = Image.open("denbg.jpg").resize((200, 700))
        self.bg_img = ImageTk.PhotoImage(img)

        self.menu_frame = tk.Frame(self, width=200)
        self.menu_frame.pack(side="left", fill="both")
        
        lbl = tk.Label(self.menu_frame, image=self.bg_img)
        lbl.place(x=0, y=0, relwidth=1, relheight=1)
        self.menu_frame.pack_propagate(False)

        self.content_frame = tk.Frame(self, bg="#9CE6FF")
        self.content_frame.pack(side="right", expand=True, fill="both")

        self.current_form = None
        self.inv_open = False

        self.button()
        self.show_home()

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def show_form(self, form_cls):
        self.clear_content()
        form = form_cls(self.content_frame, self.clinic)
        form.pack_fill()
        self.current_form = form

    def show_home(self):
        self.clear_content()
        tk.Label(self.content_frame, text="🦷 Welcome\nto the Dental Clinic\nManagement System",
                 font=("Verdana", 35, "bold"), fg="#5B5656", bg="#9CE3FF").pack(pady=100)

    def button(self):
        btn_opts = {"font": ("Arial", 13), "bg": "#9CE3FF", "fg": "black", "width": 15}
        tk.Button(self.menu_frame, text="Home", command=self.show_home, **btn_opts).pack(pady=15)
        tk.Button(self.menu_frame, text="Book Appointment", command= lambda: self.show_form(Appointment_ui), **btn_opts).pack(pady=15)
        tk.Button(self.menu_frame, text="Walk-In", command=lambda: self.show_form(WalkIn_ui), **btn_opts).pack()
        tk.Button(self.menu_frame, text="View Appointment", command=lambda: self.show_form(View_Appointments_ui), **btn_opts).pack(pady=15)
        tk.Button(self.menu_frame, text="Patient Record", command=lambda: self.show_form(Patient_Record_ui), **btn_opts).pack()
        tk.Button(self.menu_frame, text="Search Patient", command=lambda: self.show_form(Search_ui), **btn_opts).pack(pady=15)
        tk.Button(self.menu_frame, text="Inventory ▼", command=self.toggle_inventory, **btn_opts).pack()

        self.btn1 = tk.Button(self.menu_frame, text="• View Inventory", font=("Arial", 10), bg="#9CE3FF", fg="black", anchor="w", width=13, command=lambda: self.show_form(Inventory_ui))
        self.btn2 = tk.Button(self.menu_frame, text="• Sell Product", font=("Arial", 10), bg="#9CE3FF", fg="black", anchor="w", width=13, command=lambda: self.show_form(Sell_Item_ui))
        self.btn3 = tk.Button(self.menu_frame, text="• Restock Product", font=("Arial", 10), bg="#9CE3FF", fg="black", anchor="w", width=13, command=lambda: self.show_form(Restock_ui))

        tk.Button(self.menu_frame, text="Close System", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), command=self.confirm_exit).pack(side="bottom", pady=20)

    def toggle_inventory(self):
        self.inv_open = not self.inv_open
        if self.inv_open:
            self.btn1.pack()
            self.btn2.pack()
            self.btn3.pack()
        else:
            self.btn1.pack_forget()
            self.btn2.pack_forget()
            self.btn3.pack_forget()

    def confirm_exit(self):
        if messagebox.askyesno("Close System", "Are you sure you want to close?"):
            self.destroy()

clinic = Dental_Clinic()
app = Main_Window(clinic)
app.mainloop()