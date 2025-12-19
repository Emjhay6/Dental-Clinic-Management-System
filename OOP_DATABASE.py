import sqlite3

#DATABASE
db_name = "dc.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        #TABLES FOR PATIENTS
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, age INTEGER, contact TEXT)""")

        #TABLES FOR APPOINTMENT
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    patient_name TEXT,
                    dentist TEXT,
                    time TEXT,
                    date TEXT,
                    status TEXT DEFAULT 'Pending')""")

        #TABLES FOR INVENTORY
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item TEXT,
                    qty INTEGER,
                    price REAL)""")

        #TABLES FOR SERVICES
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT,
                    price REAL)""")

        #TABLE FOR HISTORY
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    service TEXT,
                    reason TEXT,
                    teeth_placement TEXT,
                    teeth_number INTEGER,
                    price REAL,
                    dentist TEXT)""")

        self.conn.commit()

        #DEFAULT PRODUCTS
        self.cursor.execute("SELECT COUNT(*) FROM inventory")
        if self.cursor.fetchone()[0] == 0:
            products = [("Toothbrush", 50, 50),
                        ("Toothpaste", 30, 80),
                        ("Mouthwash", 20, 120),
                        ("Floss", 40, 30),
                        ("Tongue Scraper", 50, 40)]
            self.cursor.executemany("INSERT INTO inventory (item, qty, price) " \
            "VALUES (?, ?, ?)", products)
            self.conn.commit()

        #DEFAULT SERVICES
        self.cursor.execute("SELECT COUNT(*) FROM services")
        if self.cursor.fetchone()[0] == 0:
            services = [("Cleaning", 500),
                        ("Tooth Extraction", 1500),
                        ("Tooth Filling(Pasta)", 1200),
                        ("Braces", 25000),
                        ("Checkup", 300),
                        ("Teeth Whitening", 1300)]
            self.cursor.executemany("INSERT INTO services (service_name, price)" \
            "VALUES (?, ?)", services)
            self.conn.commit()
