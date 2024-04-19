import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
import datetime
import serial
import threading
import sqlite3

# Constants for UI
BG_COLOR = "#f0f0f0"
TEXT_COLOR = "#333333"
BUTTON_COLOR = "#0078D7"
BUTTON_TEXT_COLOR = "white"
FONT_NORMAL = ("Arial", 12)
FONT_BOLD = ("Arial", 14, "bold")

# Initialize the database
def init_db():
    conn = sqlite3.connect('count_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS counts (
            timestamp DATETIME,
            Locked INTEGER,
            Unlocked INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Set up serial connection
ser = serial.Serial('COM5', 9600)

# Function to update count data
def update_count():
    conn = sqlite3.connect('count_data.db')
    c = conn.cursor()
    try:
        while True:
            data = ser.readline().strip().decode('utf-8')
            if data:
                counts = data.split(',')
                if len(counts) >= 2:
                    locked_label.config(text=f"Locked: {counts[0]}")
                    unlocked_label.config(text=f"Unlocked: {counts[1]}")
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute('INSERT INTO counts (timestamp, Locked, Unlocked) VALUES (?, ?, ?)', (now, counts[0], counts[1]))
                    conn.commit()
    finally:
        conn.close()

# Function to handle login
def handle_login(event=None):
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "pass":
        login_window.withdraw()
        show_count_page()
        threading.Thread(target=update_count, daemon=True).start()
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password")

# Display the count page
# Function to display the count page
# Function to display the count page
def show_count_page():
    count_frame = ttk.Frame(root, padding="10 10 10 10", relief="solid", borderwidth=2)
    count_frame.pack(expand=True, fill='both')  # This centers the frame

    # Ensure labels are defined with count_frame as their parent or repacked with count_frame as parent
    global locked_label, unlocked_label  # Ensure these are accessible globally if defined elsewhere
    locked_label = ttk.Label(count_frame, text="Locked: 0", font=FONT_BOLD)  # Ensure initial text
    unlocked_label = ttk.Label(count_frame, text="Unlocked: 0", font=FONT_BOLD)  # Ensure initial text

    # Place labels within the frame
    locked_label.pack(padx=20, pady=10)
    unlocked_label.pack(padx=20, pady=10)
    
    # Place button within the frame
    view_data_button = ttk.Button(count_frame, text="View Data", command=view_data)
    view_data_button.pack(pady=10)

    # Center the frame with the labels and button in the middle of the window
    count_frame.place(relx=0.5, rely=0.5, anchor='center')

    root.deiconify()



# Function to view data from database
def view_data():
    data_window = tk.Toplevel(root)
    data_window.title("Database Data")
    data_window.geometry("600x400")
    frame = tk.Frame(data_window)
    frame.pack(fill='both', expand=True)
    tree = ttk.Treeview(frame, columns=("timestamp", "Locked", "Unlocked"), show="headings")
    tree.heading("timestamp", text="Timestamp")
    tree.heading("Locked", text="Locked")
    tree.heading("Unlocked", text="Unlocked")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(fill='both', expand=True)
    conn = sqlite3.connect('count_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM counts")
    for row in c.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

# Main window setup
root = tk.Tk()
root.title("Count Display")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.config(bg=BG_COLOR)
root.withdraw()

# Configure labels
locked_label = ttk.Label(root, text="Locked: 0", font=FONT_BOLD)
unlocked_label = ttk.Label(root, text="Unlocked: 0", font=FONT_BOLD)

# Login window setup
login_window = tk.Toplevel(root, bg=BG_COLOR)
login_window.title("Login")
login_window.geometry(f"{screen_width}x{screen_height}+0+0")  # Full screen

# Background image
background_image = ImageTk.PhotoImage(Image.open("chek.jpg"))
background_label = ttk.Label(login_window, image=background_image)
background_label.place(relwidth=1, relheight=1)

# Login form frame
frame = ttk.Frame(login_window, padding=20)
frame.pack(expand=True)

# Login form contents

username_label = tk.Label(frame, text="Username:" , font=FONT_NORMAL)
username_label.pack(pady=(30, 10), padx=150)  # Increase the top padding

username_entry = tk.Entry(frame, font=FONT_NORMAL)
username_entry.pack(pady=5)

password_label = tk.Label(frame, text="Password:", font=FONT_NORMAL)
password_label.pack(pady=5)

password_entry = tk.Entry(frame, show="*", font=FONT_NORMAL)
password_entry.pack(pady=5)

login_button = ttk.Button(frame, text="Login", command=handle_login, style='Accent.TButton')
login_button.pack(pady=(30, 50), padx=150)  # Increase the bottom padding

login_window.bind("<Return>", handle_login)

# Start the GUI
root.mainloop()

# Clean up
ser.close()
