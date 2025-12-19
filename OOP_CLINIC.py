from OOP_DATABASE import Database

#CLASS
class Dental_Clinic(Database):
    def __init__(self):
        super().__init__()
        self.db = self.conn
        self.dentist = ["Dr. De Villa", "Dr. Santos", "Dr. Pueblo"]
        self.reason = ["Tooth Decay", "Infection", "Cracked", "Toothache", "Tartar Removal", "Crowding Teeth", 
                       "Overbite", "Underbite", "Spacing", "Remove Stains"]
        self.tooth_placement = ["Upper", "Lower"]
        self.tooth_names = {
        1: "Upper Right Third Molar",
        2: "Upper Right Second Molar",
        3: "Upper Right First Molar",
        4: "Upper Right Second Premolar",
        5: "Upper Right First Premolar",
        6: "Upper Right Canine",
        7: "Upper Right Lateral Incisor",
        8: "Upper Right Central Incisor",
        9: "Upper Left Central Incisor",
        10: "Upper Left Lateral Incisor",
        11: "Upper Left Canine",
        12: "Upper Left First Premolar",
        13: "Upper Left Second Premolar",
        14: "Upper Left First Molar",
        15: "Upper Left Second Molar",
        16: "Upper Left Third Molar",
        17: "Lower Left Third Molar",
        18: "Lower Left Second Molar",
        19: "Lower Left First Molar",
        20: "Lower Left Second Premolar",
        21: "Lower Left First Premolar",
        22: "Lower Left Canine",
        23: "Lower Left Lateral Incisor",
        24: "Lower Left Central Incisor",
        25: "Lower Right Central Incisor",
        26: "Lower Right Lateral Incisor",
        27: "Lower Right Canine",
        28: "Lower Right First Premolar",
        29: "Lower Right Second Premolar",
        30: "Lower Right First Molar",
        31: "Lower Right Second Molar",
        32: "Lower Right Third Molar" }

    def get_services(self):
        self.cursor.execute("SELECT service_name FROM services")
        return [row[0] for row in self.cursor.fetchall()]

#PATIENTS
    def find_patient(self, name):
        self.cursor.execute("SELECT * FROM patients WHERE name = ?", (name,))
        return self.cursor.fetchone()
    
    def search_patient(self, name):
        self.cursor.execute("SELECT * FROM history WHERE patient_name = ?", (name,))
        return self.cursor.fetchone()
    
    def add_patient(self):
        name = input("Enter Patient Name: ")
        existing = self.find_patient(name)
        if existing:
            print(f"Existing Patient: {existing[1]}")
            return existing
        else:
            while(True):
                try:
                    age = int(input("Enter Age: "))
                    if age < 0:
                        print("Age should be greater than zero.")
                        continue
                    else:
                        break

                except ValueError:
                    print("Age must be numeric.")

            contact = input("Enter Contact Number: ")
            self.cursor.execute("INSERT INTO patients (name, age, contact)" \
            "VALUES (?, ?, ?)", (name, age, contact))
            self.db.commit()
            print(f"New Patient {name} added.")
            return (None, name, age, contact)
                    
#SERVICES
    def choose_services(self, patient_name, dentist = None):
        self.cursor.execute("SELECT * FROM services")
        services = self.cursor.fetchall()
        print("\n---Available Services---")
        for i, serv in enumerate(services, 1):
            print(f"{i}. {serv[1]} - ₱{serv[2]}" )
        
        while(True):
            choice = input("Choose Services by number (separated by comma): ")

            try:
                choices = [int(cho.strip()) for cho in choice.split(",")]

                if any(cho < 1 or cho > len(services) for cho in choices):
                    print("Please choose from the list.")
                    continue
                else:
                    break
            except ValueError:
                print("Please enter numbers separated by comma.")

        total = 0
        for cho in choices:
            index = cho - 1
            service_name = services[index][1]
            price = services[index][2]
            total += price

            #SAVE TO HISTORY
            self.cursor.execute("INSERT INTO history (patient_name, service, reason, teeth_placement, teeth_number, price, dentist)" \
            "VALUES (?, ?, ?, ?, ?, ?, ?)", (patient_name, service_name, None, None, None, price, dentist if dentist else "N/A"))
            self.db.commit()
        print(f"Services for {patient_name}. Total Cost: ₱{total}")

#APPOINTMENT
    def book_appointment(self):
        print("\n---Book Appointment---")
        patient = self.add_patient()
        patient_name = patient[1]

        print("Choose Dentist")
        for i, den in enumerate(self.dentist, 1):
            print(f"{i}. {den}")
        
        while(True):
            
            try:
                dentist_choice = int(input("Select Dentist Number: "))
                if dentist_choice < 1 or dentist_choice > len(self.dentist):
                    print("Choose dentist base on the number from the list.")
                    continue
                else:
                    break

            except ValueError:
                print("Choice must be a number.")

        dentist = self.dentist[dentist_choice - 1]
        time = input("Enter Preffered Time (e.g., 10:00): ")
        date = input("Enter Preffered Date (e.g., 2025-01-01)")

        #CHECK SLOT IF TAKEN
        self.cursor.execute("SELECT * FROM appointments WHERE dentist = ? AND time = ? AND date = ?", (dentist, time, date))
        if self.cursor.fetchone():
            print("Schedule not available. Already book.")
            return
        
        self.cursor.execute("INSERT INTO appointments (patient_name, dentist, time, date, status) VALUES (?, ?, ?, ?, ?)", 
                            (patient_name, dentist, time, date, 'Pending'))
        self.db.commit()
        print(f"Appointment booked for {patient_name} with {dentist} at {time}.")
        self.choose_services(patient_name, dentist)

#WALK-IN
    def walk_in(self):
        print("\n-----Walk-in Patient---")
        patient = self.add_patient()
        patient_name = patient[1]
        self.choose_services(patient_name)
        print(f"Walk-in registered for {patient_name}.")

#INVENTORY
    def view_inventory(self):
        print("\nInventory Stock:")
        self.cursor.execute("SELECT * FROM inventory")
        for item in self.cursor.fetchall():
            print(f"{item[1]}: {item[2]} pcs @ ₱{item[3]} each")

    def restock(self):
        item = input("Item name: ")
        while(True):
            try:
                qty = int(input("Quantity to add: "))
                if qty < 0:
                    print("Quantity must be greater than zero.")
                    continue
                else:
                    break
            except ValueError:
                print("Quantity must be a number.")

        while(True):
            try:
                price = float(input("Price per Item: "))
                if price < 0:
                    print("Price must be greater than zero.")
                    continue
                else:
                    break
            except ValueError:
                print("Price must be a number.")
        self.cursor.execute("SELECT * FROM inventory WHERE item = ?", (item,))
        existing = self.cursor.fetchone()
        if existing:
            new_qty = existing[2] + qty
            self.cursor.execute("UPDATE inventory SET qty = ?, price = ? WHERE item = ?",
                                (new_qty, price, item))
        else:
            self.cursor.execute("INSERT INTO inventory (item, qty, price) VALUES (?, ?, ?)",
                                (item, qty, price))
        self.db.commit()
        print(f"Restocked {item} ({qty} pcs @ ₱{price})")

    def sell_item(self):
        item = input("Item name: ")
        self.cursor.execute("SELECT * FROM inventory WHERE item = ?", (item,))
        product = self.cursor.fetchone()
        if not product:
            print("item not found in inventory.")
        else:
            while(True):
                try:
                    qty = int(input("Quantity to sell: "))
                    if qty <= 0:
                        print("Quantity to sell must be greater than zero. ")
                        continue
                    else:
                        break
                except ValueError:
                    print("Quantity must be a number.")

            if product[2] < qty:
                print("Not enough stock.")
            else:
                total = qty * product[3]
                new_qty = product[2] - qty
                self.cursor.execute("UPDATE inventory SET qty = ? WHERE item = ?", (new_qty, item))
                self.db.commit()

                name = input("Enter buyer name (press ENTER if non-patient): ").strip()
                if name:
                    print(f"Sold {qty} {item} to {name} for ₱{total}.")
                else:
                    print(f"Sold {qty} {item} to NON-patient for ₱{total}.")
#RECORDS
    def show_appointments(self):
        self.cursor.execute("SELECT patient_name, dentist, time, date, status FROM appointments ORDER BY date, time ASC")
        appointments = self.cursor.fetchall()
        return appointments

    def show_patients_records(self):
        self.cursor.execute("SELECT * FROM patients")
        patients = self.cursor.fetchall()
        records = []
        for patient in patients:
            name = patient[1]
            self.cursor.execute("SELECT  patient_name, service, reason, teeth_placement, teeth_number, price, dentist FROM history WHERE patient_name = ?",
                                (name,))
            histo = self.cursor.fetchall()
            total = sum(record[5] for record in histo)
            records.append((name, histo, total))
        return records

clinic = Dental_Clinic()
             