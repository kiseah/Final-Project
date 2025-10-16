# FILE: login.py
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry

# import database globals
from database import conn, cursor, current_geometry, is_fullscreen

# global placeholders that will be created when window is shown
entry_username = None
entry_password = None
login_window = None


def login():
    # local import to avoid circular import at module load time
    from dashboard import open_dashboard

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


def show_login_window():
    global entry_username, entry_password, login_window, current_geometry, is_fullscreen

    login_window = tk.Tk()
    login_window.title("Admin Login")

    login_window.geometry(current_geometry)
    if is_fullscreen:
        login_window.state('zoomed')

    def on_resize(event=None):
        global current_geometry
        current_geometry = login_window.geometry()

    def on_fullscreen_change(event=None):
        global is_fullscreen
        is_fullscreen = (login_window.state() == 'zoomed')

    # para same gihapon ang size if ma resize
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
    
    # IIGHT FRAME
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