import mysql.connector
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# DATABASE SETUP
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="barangay profiling"
)
cursor = conn.cursor()

current_geometry = "800x500"
is_fullscreen = False

# CREATE TABLES IF NOT EXIST
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50)
) 
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS residents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resident_id VARCHAR(20) UNIQUE,
    full_name VARCHAR(255),
    gender VARCHAR(10),
    birthdate DATE,
    house_no VARCHAR(20),
    purok_zone VARCHAR(20)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS households (
    id INT AUTO_INCREMENT PRIMARY KEY,
    household_code VARCHAR(10),
    house_no VARCHAR(100),
    purok_zone VARCHAR(100),
    head_of_family VARCHAR(200),
    total_members INT(11)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS barangay_mintal_officials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region VARCHAR(100),
    province VARCHAR(100),
    city_municipality VARCHAR(100),
    barangay VARCHAR(100),
    position VARCHAR(100),
    lastname VARCHAR(100),
    firstname VARCHAR(100),
    middlename VARCHAR(100),
    suffix VARCHAR(20),
    email_address VARCHAR(150),
    barangay_hall_telno VARCHAR(50)
)
""")

# Insert default admin user if not exists
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", "1234"))
    conn.commit()

# LOGIN FUNCTION
def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in both username and password.")
        return

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

# LOGOUT FUNCTION
def logout(current_window):
    confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
    if confirm:
        current_window.destroy()
        show_login_window()

# DASHBOARD WINDOW
def open_dashboard():
    global current_geometry, is_fullscreen

    dashboard = tk.Tk()
    dashboard.title("Admin Dashboard")
    dashboard.geometry(current_geometry)

    if is_fullscreen:
        dashboard.state('zoomed')

    def on_resize(event=None):
        global current_geometry
        current_geometry = dashboard.geometry()

    def on_fullscreen_change(event=None):
        global is_fullscreen
        is_fullscreen = (dashboard.state() == 'zoomed')

    dashboard.bind("<Configure>", on_resize)
    dashboard.bind("<Map>", on_fullscreen_change)

    ttk.Style().theme_use('clam')

    def clear_main():
        for widget in main_frame.winfo_children():
            widget.destroy()

    def show_dashboard():
        clear_main()

        cursor.execute("SELECT COUNT(*) FROM residents")
        total_residents = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM households")
        total_households = cursor.fetchone()[0]
        cursor.execute("SELECT position, lastname, firstname, suffix FROM barangay_mintal_officials")
        officials = cursor.fetchall()

        tk.Label(main_frame, text="Admin Dashboard", font=("Segoe UI", 22, "bold"), bg="white").pack(pady=20)

        content_frame = tk.Frame(main_frame, bg="white")
        content_frame.pack(expand=True, fill="both", pady=20, padx=40)

        # Left Box (Residents & Households)
        left_box = tk.Frame(content_frame, bg="#E3F2FD", bd=2, relief="ridge", width=350, height=300)
        left_box.pack(side="left", expand=True, fill="both", padx=15, pady=10)
        left_box.pack_propagate(False)

        # Title (stays at top)
        tk.Label(left_box, text="Barangay Statistics", bg="#E3F2FD",
                font=("Segoe UI", 20, "bold")).pack(pady=(20, 125))

        tk.Label(left_box, text=f"👨 Residents:        {total_residents}", bg="#E3F2FD",
                font=("Segoe UI", 20)).pack(pady=10)
        tk.Label(left_box, text=f"🏠 Households:    {total_households}", bg="#E3F2FD",
                font=("Segoe UI", 20)).pack(pady=10)

        # Right Box (Barangay Officials)
        right_box = tk.Frame(content_frame, bg="#E8F5E9", bd=2, relief="ridge", width=350, height=300)
        right_box.pack(side="right", expand=True, fill="both", padx=15, pady=10)
        right_box.pack_propagate(False)

        tk.Label(right_box, text="Barangay Officials", bg="#E8F5E9",
                font=("Segoe UI", 20, "bold")).pack(pady=(20, 50))

        # If there are officials, list them
        if officials:
            for pos, lname, fname, suffix in officials:
                full_name = f"{fname} {lname} {suffix if suffix else ''}".strip()
                tk.Label(right_box, text=f"{pos}: {full_name}", bg="#E8F5E9",
                        font=("Segoe UI", 12)).pack(anchor="w", padx=30, pady=3)
        else:
            tk.Label(right_box, text="No officials found in database.", bg="#E8F5E9",
                    font=("Segoe UI", 11, "italic"), fg="gray").pack(pady=20)

    # RESIDENTS PAGE
    def show_residents():
        clear_main()
        tk.Label(main_frame, text="Residents Record", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)

        # Search bar
        search_frame = Frame(main_frame, bg="white")
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:", bg="white").pack(side=LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=40)
        search_entry.pack(side=LEFT, padx=5)

        # Frame for table and scrollbars
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=BOTH, expand=True)

        # Create Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Resident ID", "Full Name", "Gender", "Birthdate", "House No", "Purok"),
            show="headings"
        )

        # Attach vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)

        # Attach horizontal scrollbar
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side=BOTTOM, fill=X)

        # Pack the treeview last so it fills the rest of the space
        tree.pack(fill=BOTH, expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        def load_residents(search_term=""):
            for row in tree.get_children():
                tree.delete(row)
            if search_term:
                query = "SELECT * FROM residents WHERE full_name LIKE %s OR resident_id LIKE %s"
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT * FROM residents")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        def search_residents():
            load_residents(search_entry.get())

        def clear_search():
            search_entry.delete(0, END)
            load_residents()

        tk.Button(search_frame, text="Search", command=search_residents, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=clear_search, bg="#9E9E9E", fg="white").pack(side=LEFT, padx=5)

        def add_resident_window():
            win = Toplevel(dashboard)
            win.title("Add Resident")
            win.geometry("350x400")

            labels = ["Resident ID", "Full Name", "Gender", "Birthdate (YYYY-MM-DD)", "House No", "Purok"]
            entries = {}

            for label in labels:
                tk.Label(win, text=label).pack()
                if "Birthdate" in label:
                    entry = DateEntry(win,
                                    width=18,
                                    background="#1E88E5",
                                    foreground="white",
                                    borderwidth=2,
                                    date_pattern="yyyy-mm-dd")
                else:
                    entry = tk.Entry(win)

                entry.pack(pady=5)
                entries[label] = entry

            def save_resident():
                data = [entries[label].get() for label in labels]
                if any(x == "" for x in data):
                    messagebox.showwarning("Warning", "Please fill out all fields!")
                    return
                cursor.execute("""
                    INSERT INTO residents (resident_id, full_name, gender, birthdate, house_no, purok_zone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, tuple(data))
                conn.commit()
                messagebox.showinfo("Success", "Resident added successfully!")
                win.destroy()
                load_residents()

            tk.Button(win, text="Save", command=save_resident, bg="#2196F3", fg="white").pack(pady=10)

        def edit_resident_window():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a resident to edit.")
                return

            data = tree.item(selected[0])["values"]
            win = Toplevel(dashboard)
            win.title("Edit Resident")
            win.geometry("350x400")

            fields = ["Resident ID", "Full Name", "Gender", "Birthdate (YYYY-MM-DD)", "House No", "Purok"]
            entries = {}

            for i, label in enumerate(fields):
                tk.Label(win, text=label).pack()

                if "Birthdate" in label:
                    e = DateEntry(win,
                                  width=18,
                                  background="#1E88E5",
                                  foreground="white",
                                  borderwidth=2,
                                  date_pattern="yyyy-mm-dd")
                    e.set_date(data[i+1])
                else:
                    e = tk.Entry(win)
                    e.insert(0, data[i+1])

                e.pack(pady=5)
                entries[label] = e

            def save_edit():
                updated = [entries[f].get() for f in fields]
                cursor.execute("""
                    UPDATE residents 
                    SET resident_id=%s, full_name=%s, gender=%s, birthdate=%s, house_no=%s, purok_zone=%s
                    WHERE id=%s
                """, (*updated, data[0]))
                conn.commit()
                messagebox.showinfo("Updated", "Resident updated successfully!")
                win.destroy()
                load_residents()

            tk.Button(win, text="Save Changes", command=save_edit, bg="#4CAF50", fg="white").pack(pady=10)

        def delete_resident():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "PLease select a resident to delete.")
                return
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this resident?")
            if not confirm:
                return
            data = tree.item(selected[0])["values"]
            cursor.execute("DELETE FROM residents WHERE id=%s", (data[0],))
            conn.commit()
            messagebox.showinfo("Deleted", "Resident deleted successfully!")
            load_residents()
            #auto_close_message("Deleted", "Resident deleted successfully!")

        load_residents()
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Resident", command=add_resident_window,
                bg="#4CAF50", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Edit Selected", command=edit_resident_window,
                bg="#FF9800", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=delete_resident,
                bg="red", fg="white", width=15).pack(side=LEFT, padx=5)

    # HOUSEHOLDS PAGE
    def show_households():
        clear_main()
        tk.Label(main_frame, text="Households Record", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)

        # Search bar
        search_frame = Frame(main_frame, bg="white")
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:", bg="white").pack(side=LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=40)
        search_entry.pack(side=LEFT, padx=5)

        # Frame for table and scrollbars
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=BOTH, expand=True)

        # Create Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Household No", "House No", "Purok", "Head of Family", "Total Members"),
            show="headings"
        )

        # Attach vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)

        # Attach horizontal scrollbar
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side=BOTTOM, fill=X)

        # Pack the treeview last so it fills the rest of the space
        tree.pack(fill=BOTH, expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        def load_households(search_term=""):
            for row in tree.get_children():
                tree.delete(row)
            if search_term:
                query = "SELECT * FROM households WHERE household_code LIKE %s OR house_no LIKE %s OR purok_zone LIKE %s OR head_of_family LIKE %s"
                cursor.execute(query, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT * FROM households")
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        def search_households():
            load_households(search_entry.get())

        def clear_search():
            search_entry.delete(0, END)
            load_households()

        tk.Button(search_frame, text="Search", command=search_households, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=clear_search, bg="#9E9E9E", fg="white").pack(side=LEFT, padx=5)

        def add_household_window():
            win = Toplevel(dashboard)
            win.title("Add Household")
            win.geometry("300x300")

            tk.Label(win, text="Household No").pack()
            hno_entry = tk.Entry(win)
            hno_entry.pack(pady=5)

            tk.Label(win, text="House No").pack()
            house_entry = tk.Entry(win)
            house_entry.pack(pady=5)

            tk.Label(win, text="Purok").pack()
            purok_entry = tk.Entry(win)
            purok_entry.pack(pady=5)

            tk.Label(win, text="Head of Family").pack()
            head_entry = tk.Entry(win)
            head_entry.pack(pady=5)

            tk.Label(win, text="Total Members").pack()
            members_entry = tk.Entry(win)
            members_entry.pack(pady=5)

            def save_household():
                hno = hno_entry.get().strip()
                house = house_entry.get().strip()
                purok = purok_entry.get().strip()
                head = head_entry.get().strip()
                members = members_entry.get().strip()
                if not hno or not house or not purok or not head or not members:
                    messagebox.showwarning("Warning", "Please fill out all fields!")
                    return
                cursor.execute("INSERT INTO households (household_code, house_no, purok_zone, head_of_family, total_members) VALUES (%s, %s, %s, %s, %s)", (hno, house, purok, head, members))
                conn.commit()
                messagebox.showinfo("Success", "Household added successfully!")
                win.destroy()
                load_households()

            tk.Button(win, text="Save", command=save_household, bg="#2196F3", fg="white").pack(pady=10)

        def edit_household_window():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a household to edit.")
                return

            data = tree.item(selected[0])["values"]
            win = Toplevel(dashboard)
            win.title("Edit Household")
            win.geometry("300x300")

            tk.Label(win, text="Household No").pack()
            hno_entry = tk.Entry(win)
            hno_entry.pack(pady=5)
            hno_entry.insert(0, data[1])

            tk.Label(win, text="House No").pack()
            house_entry = tk.Entry(win)
            house_entry.pack(pady=5)
            house_entry.insert(0, data[2])

            tk.Label(win, text="Purok").pack()
            purok_entry = tk.Entry(win)
            purok_entry.pack(pady=5)
            purok_entry.insert(0, data[3])

            tk.Label(win, text="Head of Family").pack()
            head_entry = tk.Entry(win)
            head_entry.pack(pady=5)
            head_entry.insert(0, data[4])

            tk.Label(win, text="Total Members").pack()
            members_entry = tk.Entry(win)
            members_entry.pack(pady=5)
            members_entry.insert(0, data[5])

            def save_edit():
                cursor.execute("UPDATE households SET household_code=%s, house_no=%s, purok_zone=%s, head_of_family=%s, total_members=%s WHERE id=%s",
                               (hno_entry.get(), house_entry.get(), purok_entry.get(), head_entry.get(), members_entry.get(), data[0]))
                conn.commit()
                messagebox.showinfo("Updated", "Household updated successfully!")
                win.destroy()
                load_households()

            tk.Button(win, text="Save Changes", command=save_edit, bg="#4CAF50", fg="white").pack(pady=10)

        def delete_household():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "PLease elect a household to delete.")
                return
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this household?")
            if not confirm:
                return
            data = tree.item(selected[0])["values"]
            cursor.execute("DELETE FROM households WHERE id=%s", (data[0],))
            conn.commit()
            messagebox.showinfo("Deleted", "Household deleted successfully!")
            load_households()

        load_households()
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Household", command=add_household_window,
                bg="#4CAF50", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Edit Selected", command=edit_household_window,
                bg="#FF9800", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=delete_household,
                bg="red", fg="white", width=15).pack(side=LEFT, padx=5)

    # BARANGAY OFFICIALS PAGE
    def show_brgyofficials():
        clear_main()
        tk.Label(main_frame, text="Barangay Officials", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Search bar
        search_frame = Frame(main_frame, bg="white")
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search:", bg="white").pack(side=LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=40)
        search_entry.pack(side=LEFT, padx=5)

        # Frame for table and scrollbars
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=BOTH, expand=True)

        # Create Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Region", "Province", "City/Municipality", "Barangay", "Position", "Last Name", "First Name", "Middle Name", "Suffix", "Email Address", "Barangay Hall Tel No"),
            show="headings"
        )

        # Attach vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)

        # Attach horizontal scrollbar
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side=BOTTOM, fill=X)

        # Pack the treeview last so it fills the rest of the space
        tree.pack(fill=BOTH, expand=True)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        def load_brgyofficials(search_term=""):
            for row in tree.get_children():
                tree.delete(row)
            if search_term:
                # Remove extra spaces and lowercase for uniform matching
                search_term = search_term.strip().lower()

                # Split search term into parts (for full name search)
                parts = search_term.split()

                # Base query
                base_query = "SELECT * FROM barangay_mintal_officials"
                cursor.execute(base_query)
                results = cursor.fetchall()

                matched_rows = []
                for row in results:
                    # Extract name fields (adjust indices if needed)
                    lastname = str(row[6]).lower()
                    firstname = str(row[7]).lower()
                    middlename = str(row[8]).lower()
                    suffix = str(row[9]).lower()

                    # Combine to form full name
                    full_name = f"{lastname} {firstname} {middlename} {suffix}".strip()

                    # Match logic
                    if (search_term in lastname or
                        search_term in firstname or
                        search_term in middlename or
                        search_term in suffix or
                        all(part in full_name for part in parts)):
                        matched_rows.append(row)
                for row in matched_rows:
                    tree.insert("", "end", values=row)

            else:
                cursor.execute("SELECT * FROM barangay_mintal_officials")
                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)

        def search_brgyofficials():
            load_brgyofficials(search_entry.get().strip())

        def clear_search():
            search_entry.delete(0, END)
            load_brgyofficials()

        tk.Button(search_frame, text="Search", command=search_brgyofficials, bg="#2196F3", fg="white").pack(side=LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=clear_search, bg="#9E9E9E", fg="white").pack(side=LEFT, padx=5)

        def add_brgyofficial_window():
            win = Toplevel(dashboard)
            win.title("Add Barangay Official")
            win.geometry("600x400")
            win.configure(bg="white")

            # Create main frame with padding
            form_frame = tk.Frame(win, bg="white")
            form_frame.pack(padx=20, pady=20, fill="both", expand=True)

            # Left column labels and entries
            tk.Label(form_frame, text="Region", bg="white").grid(row=0, column=0, sticky="w", pady=5)
            region_entry = tk.Entry(form_frame, width=25)
            region_entry.grid(row=0, column=1, pady=5)

            tk.Label(form_frame, text="Province", bg="white").grid(row=1, column=0, sticky="w", pady=5)
            province_entry = tk.Entry(form_frame, width=25)
            province_entry.grid(row=1, column=1, pady=5)

            tk.Label(form_frame, text="City/Municipality", bg="white").grid(row=2, column=0, sticky="w", pady=5)
            city_entry = tk.Entry(form_frame, width=25)
            city_entry.grid(row=2, column=1, pady=5)

            tk.Label(form_frame, text="Barangay", bg="white").grid(row=3, column=0, sticky="w", pady=5)
            barangay_entry = tk.Entry(form_frame, width=25)
            barangay_entry.grid(row=3, column=1, pady=5)

            tk.Label(form_frame, text="Position", bg="white").grid(row=4, column=0, sticky="w", pady=5)
            position_entry = tk.Entry(form_frame, width=25)
            position_entry.grid(row=4, column=1, pady=5)

            # Right column labels and entries
            tk.Label(form_frame, text="Last Name", bg="white").grid(row=0, column=2, sticky="w", padx=(40, 0), pady=5)
            lastname_entry = tk.Entry(form_frame, width=25)
            lastname_entry.grid(row=0, column=3, pady=5)

            tk.Label(form_frame, text="First Name", bg="white").grid(row=1, column=2, sticky="w", padx=(40, 0), pady=5)
            firstname_entry = tk.Entry(form_frame, width=25)
            firstname_entry.grid(row=1, column=3, pady=5)

            tk.Label(form_frame, text="Middle Name", bg="white").grid(row=2, column=2, sticky="w", padx=(40, 0), pady=5)
            middlename_entry = tk.Entry(form_frame, width=25)
            middlename_entry.grid(row=2, column=3, pady=5)

            tk.Label(form_frame, text="Suffix", bg="white").grid(row=3, column=2, sticky="w", padx=(40, 0), pady=5)
            suffix_entry = tk.Entry(form_frame, width=25)
            suffix_entry.grid(row=3, column=3, pady=5)

            tk.Label(form_frame, text="Email Address", bg="white").grid(row=4, column=2, sticky="w", padx=(40, 0), pady=5)
            email_entry = tk.Entry(form_frame, width=25)
            email_entry.grid(row=4, column=3, pady=5)

            tk.Label(form_frame, text="Barangay Hall Tel No", bg="white").grid(row=5, column=2, sticky="w", padx=(40, 0), pady=5)
            tel_entry = tk.Entry(form_frame, width=25)
            tel_entry.grid(row=5, column=3, pady=5)

            # Function to save data
            def save_brgyofficial():
                region = region_entry.get().strip()
                province = province_entry.get().strip()
                city = city_entry.get().strip()
                barangay = barangay_entry.get().strip()
                position = position_entry.get().strip()
                lastname = lastname_entry.get().strip()
                firstname = firstname_entry.get().strip()
                middlename = middlename_entry.get().strip()
                suffix = suffix_entry.get().strip()
                email = email_entry.get().strip()
                tel = tel_entry.get().strip()

                if not all([region, province, city, barangay, position, lastname, firstname, middlename, email, tel]):
                    messagebox.showwarning("Warning", "Please fill out all required fields!")
                    return

                cursor.execute("""
                    INSERT INTO barangay_mintal_officials 
                    (region, province, city_municipality, barangay, position, lastname, firstname, middlename, suffix, email_address, barangay_hall_tel_no)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (region, province, city, barangay, position, lastname, firstname, middlename, suffix, email, tel))
                conn.commit()
                messagebox.showinfo("Success", "Barangay Official added successfully!")
                win.destroy()
                load_brgyofficials()

            # Save button (centered below both columns)
            tk.Button(win, text="Save", command=save_brgyofficial,
                    bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"), width=15
                    ).pack(pady=15)

        def edit_brgyofficial_window():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a barangay official to edit.")
                return

            data = tree.item(selected[0])["values"]

            win = Toplevel(dashboard)
            win.title("Edit Barangay Official")
            win.geometry("600x400")
            win.configure(bg="white")

            # Frame for form
            form_frame = tk.Frame(win, bg="white")
            form_frame.pack(padx=20, pady=20, fill="both", expand=True)

            # LEFT COLUMN
            tk.Label(form_frame, text="Region", bg="white").grid(row=0, column=0, sticky="w", pady=5)
            region_entry = tk.Entry(form_frame, width=25)
            region_entry.grid(row=0, column=1, pady=5)
            region_entry.insert(0, data[1])

            tk.Label(form_frame, text="Province", bg="white").grid(row=1, column=0, sticky="w", pady=5)
            province_entry = tk.Entry(form_frame, width=25)
            province_entry.grid(row=1, column=1, pady=5)
            province_entry.insert(0, data[2])

            tk.Label(form_frame, text="City/Municipality", bg="white").grid(row=2, column=0, sticky="w", pady=5)
            city_entry = tk.Entry(form_frame, width=25)
            city_entry.grid(row=2, column=1, pady=5)
            city_entry.insert(0, data[3])

            tk.Label(form_frame, text="Barangay", bg="white").grid(row=3, column=0, sticky="w", pady=5)
            barangay_entry = tk.Entry(form_frame, width=25)
            barangay_entry.grid(row=3, column=1, pady=5)
            barangay_entry.insert(0, data[4])

            tk.Label(form_frame, text="Position", bg="white").grid(row=4, column=0, sticky="w", pady=5)
            position_entry = tk.Entry(form_frame, width=25)
            position_entry.grid(row=4, column=1, pady=5)
            position_entry.insert(0, data[5])

            # RIGHT COLUMN
            tk.Label(form_frame, text="Last Name", bg="white").grid(row=0, column=2, sticky="w", padx=(40, 0), pady=5)
            lastname_entry = tk.Entry(form_frame, width=25)
            lastname_entry.grid(row=0, column=3, pady=5)
            lastname_entry.insert(0, data[6])

            tk.Label(form_frame, text="First Name", bg="white").grid(row=1, column=2, sticky="w", padx=(40, 0), pady=5)
            firstname_entry = tk.Entry(form_frame, width=25)
            firstname_entry.grid(row=1, column=3, pady=5)
            firstname_entry.insert(0, data[7])

            tk.Label(form_frame, text="Middle Name", bg="white").grid(row=2, column=2, sticky="w", padx=(40, 0), pady=5)
            middlename_entry = tk.Entry(form_frame, width=25)
            middlename_entry.grid(row=2, column=3, pady=5)
            middlename_entry.insert(0, data[8])

            tk.Label(form_frame, text="Suffix", bg="white").grid(row=3, column=2, sticky="w", padx=(40, 0), pady=5)
            suffix_entry = tk.Entry(form_frame, width=25)
            suffix_entry.grid(row=3, column=3, pady=5)
            suffix_entry.insert(0, data[9])

            tk.Label(form_frame, text="Email Address", bg="white").grid(row=4, column=2, sticky="w", padx=(40, 0), pady=5)
            email_entry = tk.Entry(form_frame, width=25)
            email_entry.grid(row=4, column=3, pady=5)
            email_entry.insert(0, data[10])

            tk.Label(form_frame, text="Barangay Hall Tel No", bg="white").grid(row=5, column=2, sticky="w", padx=(40, 0), pady=5)
            tel_entry = tk.Entry(form_frame, width=25)
            tel_entry.grid(row=5, column=3, pady=5)
            tel_entry.insert(0, data[11])

            # Save Changes function
            def save_edit():
                cursor.execute("""
                    UPDATE barangay_mintal_officials 
                    SET region=%s, province=%s, city_municipality=%s, barangay=%s, position=%s, 
                        lastname=%s, firstname=%s, middlename=%s, suffix=%s, email_address=%s, barangay_hall_tel_no=%s
                    WHERE id=%s
                """, (
                    region_entry.get(), province_entry.get(), city_entry.get(), barangay_entry.get(),
                    position_entry.get(), lastname_entry.get(), firstname_entry.get(),
                    middlename_entry.get(), suffix_entry.get(), email_entry.get(), tel_entry.get(), data[0]
                ))
                conn.commit()
                messagebox.showinfo("Updated", "Barangay Official updated successfully!")
                win.destroy()
                load_brgyofficials()

            # Save button centered below both columns
            tk.Button(win, text="Save Changes", command=save_edit,
                    bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"), width=15
                    ).pack(pady=15)

        def delete_brgyofficial():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a barangay official to delete.")
                return
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this barangay official?")
            if not confirm:
                return
            data = tree.item(selected[0])["values"]
            cursor.execute("DELETE FROM brgyofficials WHERE id=%s", (data[0],))
            conn.commit()
            messagebox.showinfo("Deleted", "Barangay Official deleted successfully!")
            load_brgyofficials()

        load_brgyofficials()
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Official", command=add_brgyofficial_window,
                bg="#4CAF50", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Edit Selected", command=edit_brgyofficial_window,
                bg="#FF9800", fg="white", width=15).pack(side=LEFT, padx=5)
        tk.Button(button_frame, text="Delete Selected", command=delete_brgyofficial,
                bg="red", fg="white", width=15).pack(side=LEFT, padx=5)

    # SIDEBAR NAVIGATION
    sidebar = tk.Frame(dashboard, bg="#f0f0f0", width=200)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    try:
        logo_img = Image.open(r"C:\Users\Admin\Documents\School\IT5_FinalProject\mintal.png")
        logo_img = logo_img.resize((120, 120))
        logo_photo = ImageTk.PhotoImage(logo_img)

        logo_label = Label(sidebar, image=logo_photo, bg="#f0f0f0")
        logo_label.image = logo_photo  # prevent garbage collection
        logo_label.pack(pady=(30, 2))  # top padding

    except Exception as e:
        print("Error loading logo:", e)
        Label(sidebar, text="[Logo not available]", bg="#f0f0f0", font=("Arial", 10, "italic")).pack(pady=(20, 10))

    tk.Label(sidebar, text="Barangay Mintal", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=2)
    tk.Label(sidebar, text="Admin", bg="#f0f0f0", font=("Arial", 10)).pack(pady=(0, 25))

    tk.Button(sidebar, text="Dashboard", width=20, command=show_dashboard).pack(pady=5)
    tk.Button(sidebar, text="Barangay Officials", width=20, command=show_brgyofficials).pack(pady=5)
    tk.Button(sidebar, text="Residents", width=20, command=show_residents).pack(pady=5)
    tk.Button(sidebar, text="Households", width=20, command=show_households).pack(pady=5)
    tk.Button(sidebar, text="Logout", bg="red", fg="white", width=20, command=lambda: logout(dashboard)).pack(pady=20)

    main_frame = tk.Frame(dashboard, bg="white")
    main_frame.pack(side="right", expand=True, fill="both")

    show_dashboard()
    dashboard.mainloop()

# MAIN LOGIN SCREEN
def show_login_window():
    global entry_username, entry_password, login_window, login_window, current_geometry, is_fullscreen

    login_window = tk.Tk()
    login_window.title("Admin Login")
    #login_window.geometry("800x500")

    login_window.geometry(current_geometry)
    if is_fullscreen:
        login_window.state('zoomed')

    def on_resize(event=None):
        global current_geometry
        current_geometry = login_window.geometry()

    def on_fullscreen_change(event=None):
        global is_fullscreen
        is_fullscreen = (login_window.state() == 'zoomed')

    # Bind resize and maximize/minimize events
    login_window.bind("<Configure>", on_resize)
    login_window.bind("<Map>", on_fullscreen_change)

    left_frame = tk.Frame(login_window, bg="#1E88E5", width=300, height=450 )
    left_frame.pack(side="left", fill="y")

    try:
        logo_img = Image.open(r"C:\Users\Admin\Documents\School\IT5_FinalProject\mintal.png")
        logo_img = logo_img.resize((200, 200))
        logo_photo = ImageTk.PhotoImage(logo_img)
        tk.Label(left_frame, image=logo_photo, bg="#1E88E5").place(x=50, y=100)

    except Exception as e:
        print("Error loading image:", e)
        tk.Label(left_frame, text="[Logo not available]", bg="#1E88E5", fg="white",
            font=("Segoe UI", 10, "italic")).place(x=75, y=100)
    
    tk.Label(left_frame, text="Barangay Mintal\nProfiling System", bg="#1E88E5", fg="white",
        font=("Segoe UI", 20, "bold"), justify="center").place(x=45, y=300)
    
    tk.Label(left_frame, text="Empowering Local Governance", bg="#1E88E5", fg="white",
        font=("Segoe UI", 10, "italic")).place(x=62, y=450)
    
    # Right Frame for login
    tk.Label(login_window, text="Welcome, Admin!", bg="#f0f0f0", fg="#1565C0",
         font=("Helvetica", 30, "bold")).pack(pady=(70, 5))
    tk.Label(login_window, text="Log in to continue", bg="#f0f0f0", fg="gray",
         font=("Helvetica", 15)).pack(pady=(0, 70))

    tk.Label(login_window, text="Username").pack()
    entry_username = tk.Entry(login_window, font=("Segoe UI", 14), width=30)
    entry_username.pack(pady=5, ipady=3)

    tk.Label(login_window, text="Password").pack()
    entry_password = tk.Entry(login_window, show="*", font=("Segoe UI", 14), width=30)
    entry_password.pack(pady=5, ipady=3)

    entry_username.delete(0, tk.END)
    entry_password.delete(0, tk.END)

    tk.Button(login_window, text="Login", command=login, bg="#2196F3", fg="white", width=20).pack(pady=20)

    tk.Label(login_window, text="Barangay Mintal Profiling System © 2025", bg="#f0f0f0", fg="gray",
         font=("Helvetica", 9)).pack(side="bottom", pady=20)

    login_window.mainloop()

show_login_window()