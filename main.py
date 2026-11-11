import os
import shutil
import pickle
import csv
from datetime import datetime, date
import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# --- GLOBAL CONFIG & DB CONNECTION ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # Change to your MySQL username
    "password": "password", # Change to your MySQL password
    "database": "airbnb_db"
}

current_user_id = None
current_user_name = None
selected_house_id = None
selected_card_frame = None
loaded_images = {}  # Keeps image references in memory
current_room_filter = "All"
temp_selected_image_path = None  # Stores chosen image path before saving


def normalize_house_size(value):
    """Return a consistent filter label for common bedroom/property-size formats."""
    value = str(value or "").strip().upper()
    value = value.replace("BEDROOMS", "BHK").replace("BEDROOM", "BHK")
    value = value.replace(" ", "").replace("-", "")
    if value in ("1BED", "1BEDS"):
        value = "1BHK"
    elif value in ("2BED", "2BEDS"):
        value = "2BHK"
    elif value in ("3BED", "3BEDS"):
        value = "3BHK"
    if value.endswith("BHK") and len(value) > 3:
        return f"{value[:-3]} BHK"
    return value.title() if value else ""

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Cannot connect to MySQL: {err}")
        return None

# --- FILE HANDLING HELPERS ---
def save_user_session_binary(user_id, username):
    """Saves active session state into a binary file (.dat) using pickle.dump()"""
    session_data = {"user_id": user_id, "username": username, "status": "Logged_In"}
    try:
        with open("session.dat", "wb") as bf:
            pickle.dump(session_data, bf)
    except Exception as e:
        print(f"Binary File Error: {e}")

def read_binary_logs():
    """Reads session objects from binary file using pickle.load()"""
    if not os.path.exists("session.dat"):
        messagebox.showinfo("Binary File Log", "No binary session log found.")
        return

    try:
        with open("session.dat", "rb") as bf:
            data = pickle.load(bf)
            messagebox.showinfo("CBSE Binary File Read", f"Binary File Object Content:\n\n{data}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not read binary file: {e}")

def export_booking_to_csv(booking_id, user, house_id, cin, cout):
    """Appends confirmed booking details to a CSV report using csv.writer()"""
    file_exists = os.path.exists("bookings_report.csv")
    try:
        with open("bookings_report.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["Booking_ID", "User_Name", "House_ID", "Check_In", "Check_Out"])
            writer.writerow([booking_id, user, house_id, cin, cout])
    except Exception as e:
        print(f"CSV Export Error: {e}")

# --- ENHANCED AESTHETIC ABOUT US WINDOW ---
def open_about_us_window():
    file_path = "about_us.txt"
    file_content = (
        "Welcome to Airbnb!\n\n"
        "Your ultimate platform for discovering unique holiday homes, luxury villas, "
        "city apartments, and peaceful nature retreats worldwide.\n\n"
        "Developed as part of the CBSE Class 12 Computer Science Project, demonstrating "
        "advanced Python GUI programming with Tkinter, relational database management via MySQL, "
        "file handling (Binary & CSV), and dynamic data analytics."
    )
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception:
            pass

    about_win = tk.Toplevel(root)
    about_win.title("About Airbnb - Project Details")
    about_win.geometry("500x440")
    about_win.configure(bg="#FFFFFF")
    about_win.resizable(False, False)
    about_win.transient(root)

    header_frame = tk.Frame(about_win, bg="#FF385C", height=75)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="airbnb", font=("Segoe UI", 24, "bold"), fg="white", bg="#FF385C").pack(pady=18)

    content_card = tk.Frame(about_win, bg="#FFFFFF", padx=25, pady=20)
    content_card.pack(fill="both", expand=True)

    tk.Label(content_card, text="About Our Project", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg="#222222").pack(anchor="w", pady=(0, 10))

    text_container = tk.Frame(content_card, bg="#F7F7F7", bd=1, relief="solid", padx=12, pady=12)
    text_container.pack(fill="both", expand=True, pady=(0, 15))

    txt_display = tk.Text(
        text_container, 
        wrap="word", 
        font=("Segoe UI", 10), 
        bg="#F7F7F7", 
        fg="#484848", 
        bd=0, 
        highlightthickness=0,
        height=9
    )
    txt_display.insert("1.0", file_content)
    txt_display.config(state="disabled")
    txt_display.pack(side="left", fill="both", expand=True)

    btn_close = tk.Button(
        content_card, 
        text="Got it", 
        command=about_win.destroy, 
        bg="#222222", 
        fg="white", 
        font=("Segoe UI", 10, "bold"), 
        bd=0, 
        padx=20, 
        pady=8,
        cursor="hand2"
    )
    btn_close.pack(anchor="e")

def open_analytics_window():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor(dictionary=True)
    q1 = """
        SELECT d.name AS dest, COUNT(h.house_id) AS total_stays, AVG(h.price_per_night) AS avg_price
        FROM destination d
        LEFT JOIN houses h ON d.dest_id = h.dest_id
        GROUP BY d.dest_id, d.name
    """
    cursor.execute(q1)
    stats = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_b FROM bookings")
    total_bookings = cursor.fetchone()["total_b"]
    conn.close()

    win = tk.Toplevel(root)
    win.title("CBSE SQL Analytics Report")
    win.geometry("440x360")
    win.configure(bg="#FFFFFF")
    win.transient(root)

    tk.Label(win, text="📊 SQL Aggregate Analytics", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#FF385C").pack(pady=10)
    
    tree = ttk.Treeview(win, columns=("Dest", "Stays", "AvgPrice"), show="headings", height=8)
    tree.heading("Dest", text="Destination")
    tree.heading("Stays", text="Total Stays")
    tree.heading("AvgPrice", text="Avg Price/Night (₹)")
    
    tree.column("Dest", width=140)
    tree.column("Stays", width=90, anchor="center")
    tree.column("AvgPrice", width=130, anchor="e")

    for s in stats:
        avg_p = f"₹{s['avg_price']:.2f}" if s['avg_price'] else "N/A"
        tree.insert("", "end", values=(s["dest"], s["total_stays"], avg_p))

    tree.pack(fill="x", padx=15, pady=5)
    tk.Label(win, text=f"Total System Bookings Executed: {total_bookings}", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222").pack(pady=10)

# --- EXPANDED ADMIN DASHBOARD WITH STABLE FILE BROWSER ---
def open_admin_dashboard():
    global temp_selected_image_path
    temp_selected_image_path = None

    admin_win = tk.Toplevel(root)
    admin_win.title("Airbnb Admin Control Center")
    admin_win.geometry("820x720")
    admin_win.configure(bg="#F7F7F7")
    # Keep this as a normal Toplevel. Making it transient can cause some native
    # file dialogs (especially on Windows) to hide the admin window unexpectedly.
    admin_win.protocol("WM_DELETE_WINDOW", admin_win.destroy)

    canvas_adm = tk.Canvas(admin_win, bg="#F7F7F7", highlightthickness=0)
    scrollbar_adm = ttk.Scrollbar(admin_win, orient="vertical", command=canvas_adm.yview)
    adm_container = tk.Frame(canvas_adm, bg="#F7F7F7")

    adm_window = canvas_adm.create_window((0, 0), window=adm_container, anchor="nw")
    adm_container.bind("<Configure>", lambda e: canvas_adm.configure(scrollregion=canvas_adm.bbox("all")))
    canvas_adm.bind("<Configure>", lambda e: canvas_adm.itemconfig(adm_window, width=e.width))
    canvas_adm.configure(yscrollcommand=scrollbar_adm.set)

    canvas_adm.pack(side="left", fill="both", expand=True)
    scrollbar_adm.pack(side="right", fill="y")

    tk.Label(adm_container, text="🛠️ Admin Control Panel", font=("Segoe UI", 16, "bold"), bg="#F7F7F7", fg="#222222").pack(pady=10)

    # Bookings Viewer Section
    lbl_b = tk.Label(adm_container, text="All Customer Bookings", font=("Segoe UI", 11, "bold"), bg="#F7F7F7", fg="#FF385C")
    lbl_b.pack(anchor="w", padx=20, pady=(5, 2))

    tree_b = ttk.Treeview(adm_container, columns=("BID", "User", "House", "CheckIn", "CheckOut"), show="headings", height=4)
    tree_b.heading("BID", text="Booking ID")
    tree_b.heading("User", text="User Name")
    tree_b.heading("House", text="House ID")
    tree_b.heading("CheckIn", text="Check-In")
    tree_b.heading("CheckOut", text="Check-Out")

    tree_b.column("BID", width=60, anchor="center")
    tree_b.column("User", width=140)
    tree_b.column("House", width=60, anchor="center")
    tree_b.column("CheckIn", width=100, anchor="center")
    tree_b.column("CheckOut", width=100, anchor="center")
    tree_b.pack(fill="x", padx=20, pady=5)

    def refresh_bookings():
        for row in tree_b.get_children():
            tree_b.delete(row)
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT b.booking_id, u.full_name, b.house_id, b.check_in, b.check_out FROM bookings b JOIN users u ON b.user_id = u.user_id ORDER BY b.booking_id DESC")
            for b in cursor.fetchall():
                tree_b.insert("", "end", values=(b["booking_id"], b["full_name"], b["house_id"], str(b["check_in"]), str(b["check_out"])))
            conn.close()

    refresh_bookings()

    # 1. Price Management Frame
    frame_price = tk.LabelFrame(adm_container, text="Manage House Prices", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=8)
    frame_price.pack(fill="x", padx=20, pady=8)

    tk.Label(frame_price, text="House ID:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5)
    ent_hid = tk.Entry(frame_price, width=6, font=("Segoe UI", 10))
    ent_hid.grid(row=0, column=1, padx=5)

    tk.Label(frame_price, text="New Price (₹):", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5)
    ent_new_price = tk.Entry(frame_price, width=10, font=("Segoe UI", 10))
    ent_new_price.grid(row=0, column=3, padx=5)

    def update_price_action():
        hid = ent_hid.get().strip()
        np = ent_new_price.get().strip()
        if not hid or not np:
            messagebox.showwarning("Input Error", "Please provide House ID and New Price!", parent=admin_win)
            return
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE houses SET price_per_night = %s WHERE house_id = %s", (np, hid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Price for House #{hid} updated successfully!", parent=admin_win)
            load_houses()

    btn_upd = tk.Button(frame_price, text="Update Price", command=update_price_action, bg="#222222", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=8, pady=4)
    btn_upd.grid(row=0, column=4, padx=10)

    # 2. Add New Property Frame with Destination Dropdown & File Picker
    frame_add = tk.LabelFrame(adm_container, text="➕ Add New Property Listing & Image", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=10)
    frame_add.pack(fill="x", padx=20, pady=8)

    tk.Label(frame_add, text="Title:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=4)
    ent_add_title = tk.Entry(frame_add, width=30, font=("Segoe UI", 9))
    ent_add_title.grid(row=0, column=1, columnspan=3, sticky="w", pady=4, padx=5)

    tk.Label(frame_add, text="Destination:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=4)
    
    dest_map = {}
    conn_d = get_db_connection()
    if conn_d:
        cur_d = conn_d.cursor()
        cur_d.execute("SELECT dest_id, name FROM destination")
        for row in cur_d.fetchall():
            dest_map[row[1]] = row[0]
        conn_d.close()

    dest_names = list(dest_map.keys()) if dest_map else ["Goa", "New York", "Bali", "Paris"]
    dest_dropdown = ttk.Combobox(frame_add, values=dest_names, state="readonly", width=16, font=("Segoe UI", 9))
    if dest_names:
        dest_dropdown.set(dest_names[0])
    dest_dropdown.grid(row=1, column=1, sticky="w", pady=4, padx=5)

    tk.Label(frame_add, text="Property Size:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", pady=4)
    # Correct schema values matching your SQL table ('1 BHK', '2 BHK', 'Villa')
    size_dropdown = ttk.Combobox(frame_add, values=["1 BHK", "2 BHK", "3 BHK", "Villa"], state="readonly", width=14, font=("Segoe UI", 9))
    size_dropdown.set("1 BHK")
    size_dropdown.grid(row=1, column=3, sticky="w", pady=4, padx=5)

    tk.Label(frame_add, text="Price/Night (₹):", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=4)
    ent_add_price = tk.Entry(frame_add, width=12, font=("Segoe UI", 9))
    ent_add_price.grid(row=2, column=1, sticky="w", pady=4, padx=5)

    lbl_img_status = tk.Label(frame_add, text="No image selected", bg="#FFFFFF", fg="gray", font=("Segoe UI", 8))
    lbl_img_status.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)

    def browse_image():
        global temp_selected_image_path

        # Use the admin window as the dialog owner, then explicitly restore it.
        # The dialog is cancelled safely when the user presses Cancel or closes it.
        admin_win.update_idletasks()
        try:
            file_path = filedialog.askopenfilename(
                parent=admin_win,
                title="Select Property Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif"),
                    ("PNG images", "*.png"),
                    ("JPEG images", "*.jpg *.jpeg"),
                    ("GIF images", "*.gif"),
                    ("All files", "*.*")
                ]
            )
        finally:
            # Some Windows/Tk combinations leave the Toplevel behind the main
            # window after a native dialog closes. Bring it back without
            # recreating it, so all entered form details remain intact.
            if admin_win.winfo_exists():
                admin_win.deiconify()
                admin_win.lift()
                admin_win.focus_force()

        if file_path:
            temp_selected_image_path = file_path
            filename = os.path.basename(file_path)
            lbl_img_status.config(text=f"Selected: {filename}", fg="#008489")

    btn_browse = tk.Button(frame_add, text="📁 Browse Image", command=browse_image, bg="#F7F7F7", fg="#222222", font=("Segoe UI", 9), bd=1, relief="solid", padx=8, pady=2)
    btn_browse.grid(row=2, column=3, sticky="w", padx=5)

    def add_property_action():
        global temp_selected_image_path
        title = ent_add_title.get().strip()
        selected_dest_name = dest_dropdown.get()
        size = size_dropdown.get().strip()
        price = ent_add_price.get().strip()

        if not title or not price or not size:
            messagebox.showwarning("Input Error", "Please provide a Property Title, Size, and Price!", parent=admin_win)
            return

        dest_id = dest_map.get(selected_dest_name, 1)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO houses (dest_id, title, size, price_per_night) VALUES (%s, %s, %s, %s)",
                    (dest_id, title, size, price)
                )
                conn.commit()
                new_house_id = cursor.lastrowid

                if temp_selected_image_path and os.path.exists(temp_selected_image_path):
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    image_ext = os.path.splitext(temp_selected_image_path)[1].lower()
                    if image_ext not in (".png", ".jpg", ".jpeg", ".gif"):
                        image_ext = ".png"
                    dest_img_path = os.path.join(script_dir, f"{new_house_id}{image_ext}")
                    shutil.copy2(temp_selected_image_path, dest_img_path)
                    img_msg = f" and image saved as {new_house_id}{image_ext}!"
                else:
                    img_msg = " (No custom image chosen)."

                messagebox.showinfo("Success!", f"Property added successfully!\nAssigned House ID: #{new_house_id}{img_msg}", parent=admin_win)
                
                ent_add_title.delete(0, tk.END)
                ent_add_price.delete(0, tk.END)
                lbl_img_status.config(text="No image selected", fg="gray")
                temp_selected_image_path = None
                load_houses()
                refresh_bookings()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Could not add property: {err}", parent=admin_win)
            finally:
                conn.close()

    btn_add_prop = tk.Button(frame_add, text="Save & Add Property", command=add_property_action, bg="#FF385C", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6)
    btn_add_prop.grid(row=3, column=3, sticky="e", pady=5)

    # 3. Delete Property Frame
    frame_del = tk.LabelFrame(adm_container, text="🗑️ Delete Property Listing", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=8)
    frame_del.pack(fill="x", padx=20, pady=(8, 20))

    tk.Label(frame_del, text="House ID to Delete:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5)
    ent_del_hid = tk.Entry(frame_del, width=8, font=("Segoe UI", 10))
    ent_del_hid.grid(row=0, column=1, padx=5)

    def delete_property_action():
        hid = ent_del_hid.get().strip()
        if not hid:
            messagebox.showwarning("Input Error", "Please provide the House ID to delete!", parent=admin_win)
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete House #{hid}?", parent=admin_win):
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM houses WHERE house_id = %s", (hid,))
                conn.commit()
                
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Remove whichever supported image format was saved for this house.
                for extension in (".png", ".jpg", ".jpeg", ".gif"):
                    img_path = os.path.join(script_dir, f"{hid}{extension}")
                    if os.path.exists(img_path):
                        os.remove(img_path)

                messagebox.showinfo("Success", f"House #{hid} deleted successfully!", parent=admin_win)
                ent_del_hid.delete(0, tk.END)
                load_houses()
                refresh_bookings()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Deletion failed: {err}", parent=admin_win)
            finally:
                conn.close()

    btn_del_prop = tk.Button(frame_del, text="Delete Property", command=delete_property_action, bg="#222222", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=4)
    btn_del_prop.grid(row=0, column=2, padx=10)

# --- USER & ADMIN AUTHENTICATION ---
def login_action():
    global current_user_id, current_user_name
    u = ent_login_user.get().strip()
    p = ent_login_pass.get().strip()

    if not u or not p:
        messagebox.showwarning("Input Error", "Enter both username and password!")
        return

    if u.lower() == "admin" and p == "admin123":
        current_user_id = 0
        current_user_name = "Administrator"
        login_frame.pack_forget()
        open_home_frame(is_admin=True)
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (u, p))
        user = cursor.fetchone()
        conn.close()

        if user:
            current_user_id = user["user_id"]
            current_user_name = user["full_name"]
            save_user_session_binary(current_user_id, current_user_name)
            login_frame.pack_forget()
            open_home_frame(is_admin=False)
        else:
            messagebox.showerror("Error", "Invalid username or password!")

def logout_action(home_frame_ref):
    global current_user_id, current_user_name, selected_house_id
    current_user_id = None
    current_user_name = None
    selected_house_id = None
    if os.path.exists("session.dat"):
        try:
            os.remove("session.dat")
        except Exception:
            pass
    home_frame_ref.pack_forget()
    login_frame.pack(pady=70)

def register_action():
    reg_win = tk.Toplevel(root)
    reg_win.title("Register")
    reg_win.geometry("320x280")
    reg_win.configure(bg="#FFFFFF")
    reg_win.transient(root)

    tk.Label(reg_win, text="Create Account", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#FF385C").pack(pady=(15, 10))

    tk.Label(reg_win, text="Full Name:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30)
    e_name = tk.Entry(reg_win, width=26, font=("Segoe UI", 10))
    e_name.pack(pady=(2, 8))

    tk.Label(reg_win, text="Username:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30)
    e_user = tk.Entry(reg_win, width=26, font=("Segoe UI", 10))
    e_user.pack(pady=(2, 8))

    tk.Label(reg_win, text="Password:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30)
    e_pass = tk.Entry(reg_win, show="*", width=26, font=("Segoe UI", 10))
    e_pass.pack(pady=(2, 15))

    def save_user():
        n, u, p = e_name.get().strip(), e_user.get().strip(), e_pass.get().strip()
        if not n or not u or not p:
            messagebox.showwarning("Warning", "All fields required!", parent=reg_win)
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (full_name, username, password) VALUES (%s, %s, %s)", (n, u, p))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!", parent=reg_win)
                reg_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}", parent=reg_win)
            finally:
                conn.close()

    tk.Button(reg_win, text="Register", command=save_user, bg="#FF385C", fg="white", font=("Segoe UI", 10, "bold"), bd=0, width=20, pady=5).pack(pady=5)

def select_card(house_id, frame, title):
    global selected_house_id, selected_card_frame
    if selected_card_frame:
        selected_card_frame.config(highlightbackground="#EBEBEB", highlightthickness=1)
    
    selected_house_id = house_id
    selected_card_frame = frame
    frame.config(highlightbackground="#FF385C", highlightthickness=2)
    lbl_selected.config(text=f"Selected Stay: {title}")

# --- DISPLAY HOUSES WITH EXACT DATABASE SIZE FILTERING ('1 BHK', '2 BHK', 'Villa') ---
def load_houses(category="All"):
    global selected_house_id, selected_card_frame, current_room_filter
    selected_house_id = None
    selected_card_frame = None
    lbl_selected.config(text="Selected Stay: None")

    for widget in grid_container.winfo_children():
        widget.destroy()

    search_text = ent_search.get().strip()

    query = """
        SELECT h.house_id, h.title, d.dest_id, d.name AS destination, d.category, h.size, h.price_per_night 
        FROM houses h 
        JOIN destination d ON h.dest_id = d.dest_id
        WHERE 1=1
    """
    params = []

    if category != "All":
        cat_map = {
            "Beaches": "Beach",
            "Mountains": "Mountain",
            "City": "City",
            "Island": "Island"
        }
        cat_filter = cat_map.get(category, category)
        query += " AND d.category LIKE %s"
        params.append(f"%{cat_filter}%")

    # Normalize both sides so values such as "1BHK", "1 BHK", and
    # "1 Bedroom" all match the same filter choice.
    if current_room_filter != "All":
        normalized_size_sql = (
            "REPLACE(REPLACE(REPLACE(REPLACE(UPPER(TRIM(h.size)), ' ', ''), "
            "'-', ''), 'BEDROOMS', 'BHK'), 'BEDROOM', 'BHK')"
        )
        query += f" AND {normalized_size_sql} = %s"
        params.append(normalize_house_size(current_room_filter).replace(" ", ""))

    if search_text and search_text != "Search destinations...":
        query += " AND (d.name LIKE %s OR h.title LIKE %s)"
        params.append(f"%{search_text}%")
        params.append(f"%{search_text}%")

    query += " ORDER BY d.dest_id, h.house_id"

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            tk.Label(grid_container, text="No stays found matching your criteria.", font=("Segoe UI", 11), bg="#FFFFFF", fg="#717171").pack(pady=40)
            return

        grouped = {}
        for row in rows:
            dest = row["destination"]
            if dest not in grouped:
                grouped[dest] = []
            grouped[dest].append(row)

        current_row_idx = 0
        for dest_name, houses in grouped.items():
            hdr = tk.Frame(grid_container, bg="#FFFFFF")
            hdr.grid(row=current_row_idx, column=0, columnspan=3, sticky="w", pady=(20, 8), padx=10)
            tk.Label(hdr, text=f"📍 Stays in {dest_name} ({len(houses)} available)", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg="#222222").pack(side="left")
            current_row_idx += 1

            for idx, h in enumerate(houses):
                r = current_row_idx + (idx // 3)
                c = idx % 3

                h_id = h["house_id"]
                h_title = h["title"]

                card = tk.Frame(grid_container, bg="#FFFFFF", highlightbackground="#EBEBEB", highlightthickness=1, cursor="hand2")
                card.grid(row=r, column=c, padx=18, pady=14, sticky="nsew")
                card.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                canvas = tk.Canvas(card, width=275, height=155, bg="#F7F7F7", highlightthickness=0)
                canvas.pack(fill="x")
                canvas.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                script_dir = os.path.dirname(os.path.abspath(__file__))

                image_candidates = [
                    os.path.join(script_dir, f"{h_id}.png"),
                    os.path.join(script_dir, f"{h_id}.jpg"),
                    os.path.join(script_dir, f"{h_id}.jpeg"),
                    os.path.join(script_dir, f"{h_id}.gif")
                ]
                img_path = next((path for path in image_candidates if os.path.exists(path)), None)

                if img_path:
                    try:
                        try:
                            # Pillow supports JPEG and resizes images to fit the card.
                            from PIL import Image, ImageTk
                            pil_image = Image.open(img_path)
                            pil_image.thumbnail((275, 155))
                            img = ImageTk.PhotoImage(pil_image)
                        except ImportError:
                            # Tk's native PhotoImage supports PNG/GIF without Pillow.
                            img = tk.PhotoImage(file=img_path)
                        loaded_images[h_id] = img
                        canvas.create_image(137, 77, image=img)
                    except Exception:
                        canvas.create_text(137, 77, text="🏠 Image Error", fill="#717171")
                else:
                    canvas.create_text(137, 77, text=f"🏠 ID #{h_id} ({dest_name})", font=("Segoe UI", 9, "bold"), fill="#222222")

                info = tk.Frame(card, bg="#FFFFFF", padx=10, pady=10)
                info.pack(fill="both", expand=True)
                info.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                tk.Label(info, text=h_title, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", anchor="w", wraplength=255, justify="left").pack(anchor="w", pady=2)
                tk.Label(info, text=h["size"], font=("Segoe UI", 8), fg="#717171", bg="#FFFFFF", anchor="w").pack(anchor="w")
                tk.Label(info, text=f"₹{h['price_per_night']:,.0f} / night", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", anchor="w").pack(anchor="w", pady=(4, 0))

            current_row_idx += ((len(houses) - 1) // 3) + 1

        for i in range(3):
            grid_container.columnconfigure(i, weight=1)

# --- POST-BOOKING & PAYMENT SUMMARY PAGE ---
def show_booking_confirmation(booking_id, house_title, cin, cout, price_per_night, nights):
    pay_win = tk.Toplevel(root)
    pay_win.title("Booking Details & Payment Confirmation")
    pay_win.geometry("450x540")
    pay_win.configure(bg="#FFFFFF")
    pay_win.transient(root)

    tk.Label(pay_win, text="🎉 Booking Confirmed!", font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#FF385C").pack(pady=(15, 5))
    tk.Label(pay_win, text=f"Booking Reference ID: #{booking_id}", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#717171").pack(pady=(0, 10))

    info_card = tk.Frame(pay_win, bg="#F7F7F7", bd=1, relief="solid", padx=15, pady=15)
    info_card.pack(fill="x", padx=20, pady=10)

    tk.Label(info_card, text=f"Guest Name: {current_user_name}", font=("Segoe UI", 10), bg="#F7F7F7", fg="#222222", anchor="w").pack(fill="x", pady=2)
    tk.Label(info_card, text=f"Property: {house_title}", font=("Segoe UI", 10, "bold"), bg="#F7F7F7", fg="#222222", anchor="w").pack(fill="x", pady=2)
    tk.Label(info_card, text=f"Check-In Date: {cin}", font=("Segoe UI", 10), bg="#F7F7F7", fg="#222222", anchor="w").pack(fill="x", pady=2)
    tk.Label(info_card, text=f"Check-Out Date: {cout}", font=("Segoe UI", 10), bg="#F7F7F7", fg="#222222", anchor="w").pack(fill="x", pady=2)
    tk.Label(info_card, text=f"Duration: {nights} Night(s)", font=("Segoe UI", 10), bg="#F7F7F7", fg="#222222", anchor="w").pack(fill="x", pady=2)

    total_amount = price_per_night * nights  
    tk.Label(info_card, text=f"Total Charged: ₹{total_amount:,.2f}", font=("Segoe UI", 11, "bold"), bg="#F7F7F7", fg="#FF385C", anchor="w").pack(fill="x", pady=(8, 0))

    tk.Label(pay_win, text="Select Payment Method", font=("Segoe UI", 11, "bold"), bg="#FFFFFF", fg="#222222").pack(anchor="w", padx=20, pady=(15, 5))

    pay_opt = tk.StringVar(value="UPI / QR Code")
    for mode in ["UPI / QR Code", "Credit / Debit Card", "Net Banking", "Pay at Property"]:
        tk.Radiobutton(pay_win, text=mode, variable=pay_opt, value=mode, bg="#FFFFFF", font=("Segoe UI", 10), fg="#222222", selectcolor="#F7F7F7").pack(anchor="w", padx=30, pady=3)

    def process_payment():
        messagebox.showinfo("Payment Successful", f"Payment of ₹{total_amount:,.2f} completed via {pay_opt.get()}!\nReceipt exported to 'bookings_report.csv'.", parent=pay_win)
        pay_win.destroy()

    tk.Button(pay_win, text="Complete Payment & Confirm", command=process_payment, bg="#FF385C", fg="white", font=("Segoe UI", 11, "bold"), bd=0, pady=10).pack(fill="x", padx=20, pady=20)

# --- BOOKING ACTION WITH PAST DATE VALIDATION ---
def book_house():
    if not selected_house_id:
        messagebox.showwarning("Selection Error", "Please click a stay card first!")
        return

    cin = ent_cin.get().strip()
    cout = ent_cout.get().strip()

    if not cin or not cout:
        messagebox.showwarning("Date Error", "Please enter Check-in and Check-out dates!")
        return

    try:
        d_in = datetime.strptime(cin, "%Y-%m-%d").date()
        d_out = datetime.strptime(cout, "%Y-%m-%d").date()
        today = date.today()

        if d_in < today:
            messagebox.showerror("Invalid Date", f"Check-in date cannot be in the past! (Today is {today})")
            return
        
        nights = (d_out - d_in).days
        
        if nights <= 0:
            messagebox.showerror("Date Error", "Check-out date must be strictly after the check-in date!")
            return
            
    except ValueError:
        messagebox.showerror("Format Error", "Dates must follow the YYYY-MM-DD format!")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT title, price_per_night FROM houses WHERE house_id = %s", (selected_house_id,))
        house_info = cursor.fetchone()

        overlap_sql = """
            SELECT * FROM bookings 
            WHERE house_id = %s AND check_in < %s AND check_out > %s
        """
        cursor.execute(overlap_sql, (selected_house_id, cout, cin))
        if cursor.fetchone():
            messagebox.showerror("Unavailable", "This stay is already booked for these dates!")
        else:
            insert_sql = "INSERT INTO bookings (user_id, house_id, check_in, check_out) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_sql, (current_user_id, selected_house_id, cin, cout))
            conn.commit()
            
            b_id = cursor.lastrowid
            export_booking_to_csv(b_id, current_user_name, selected_house_id, cin, cout)
            show_booking_confirmation(b_id, house_info["title"], cin, cout, house_info["price_per_night"], nights)
            
        conn.close()

# --- MAIN HOME SCREEN ---
def open_home_frame(is_admin=False):
    global grid_container, ent_search, lbl_selected, ent_cin, ent_cout, current_room_filter

    home = tk.Frame(root, bg="#FFFFFF")
    home.pack(fill="both", expand=True)

    top_bar = tk.Frame(home, bg="#FF385C", height=65)
    top_bar.pack(fill="x")
    top_bar.pack_propagate(False)

    tk.Label(top_bar, text="airbnb", font=("Segoe UI", 22, "bold"), fg="white", bg="#FF385C").pack(side="left", padx=20)
    
    btn_logout = tk.Button(top_bar, text="Logout", command=lambda: logout_action(home), bg="#FFFFFF", fg="#FF385C", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=3)
    btn_logout.pack(side="right", padx=15)

    if is_admin:
        btn_admin = tk.Button(top_bar, text="Admin Panel", command=open_admin_dashboard, bg="#222222", fg="white", font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=3)
        btn_admin.pack(side="right", padx=5)

    btn_about = tk.Button(top_bar, text="About Us", command=open_about_us_window, bg="white", fg="#FF385C", font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=3)
    btn_about.pack(side="right", padx=5)

    btn_binary = tk.Button(top_bar, text="Session Log", command=read_binary_logs, bg="white", fg="#FF385C", font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=3)
    btn_binary.pack(side="right", padx=5)

    btn_stats = tk.Button(top_bar, text="SQL Analytics", command=open_analytics_window, bg="#222222", fg="white", font=("Segoe UI", 8, "bold"), bd=0, padx=8, pady=3)
    btn_stats.pack(side="right", padx=5)

    tk.Label(top_bar, text=f"👤 {current_user_name}", font=("Segoe UI", 9, "bold"), fg="white", bg="#FF385C").pack(side="right", padx=10)

    search_frame = tk.Frame(top_bar, bg="white", bd=1, relief="solid")
    search_frame.pack(side="left", padx=15, pady=12)

    ent_search = tk.Entry(search_frame, font=("Segoe UI", 10), width=22, bd=0, fg="gray")
    ent_search.insert(0, "Search destinations...")
    ent_search.pack(side="left", padx=8, pady=4)

    def on_search_focus_in(event):
        if ent_search.get() == "Search destinations...":
            ent_search.delete(0, tk.END)
            ent_search.config(fg="#222222")

    def on_search_focus_out(event):
        if not ent_search.get().strip():
            ent_search.insert(0, "Search destinations...")
            ent_search.config(fg="gray")

    ent_search.bind("<FocusIn>", on_search_focus_in)
    ent_search.bind("<FocusOut>", on_search_focus_out)

    btn_search = tk.Button(search_frame, text="🔍", command=lambda: load_houses("All"), bg="white", fg="#FF171F", font=("Segoe UI", 9, "bold"), bd=0)
    btn_search.pack(side="right", padx=5)

    # Category Bar & Dynamic Database Property Size Filter Bar
    filter_container = tk.Frame(home, bg="#FFFFFF")
    filter_container.pack(fill="x", padx=20, pady=8)

    cat_bar = tk.Frame(filter_container, bg="#FFFFFF")
    cat_bar.pack(side="left")

    for cat in ["All", "City", "Mountains", "Beaches", "Island"]:
        btn = tk.Button(cat_bar, text=cat, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", bd=0, command=lambda c=cat: load_houses(c))
        btn.pack(side="left", padx=6)

    # Size Filter Dropdown populated dynamically straight from database schema values ('1 BHK', '2 BHK', 'Villa')
    room_filter_frame = tk.Frame(filter_container, bg="#FFFFFF")
    room_filter_frame.pack(side="right", padx=10)

    tk.Label(room_filter_frame, text="Filter Size:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#717171").pack(side="left", padx=5)
    
    db_sizes = ["All Types"]
    conn_s = get_db_connection()
    if conn_s:
        cur_s = conn_s.cursor()
        cur_s.execute("SELECT DISTINCT size FROM houses WHERE size IS NOT NULL AND TRIM(size) != ''")
        normalized_sizes = {
            normalize_house_size(row[0])
            for row in cur_s.fetchall()
            if normalize_house_size(row[0])
        }
        conn_s.close()
        db_sizes.extend(sorted(normalized_sizes, key=lambda value: (value != "Villa", value)))

    # Include the standard categories even if there are currently no listings in one.
    for standard_size in ("1 BHK", "2 BHK", "3 BHK", "Villa"):
        if standard_size not in db_sizes:
            db_sizes.append(standard_size)

    room_dropdown = ttk.Combobox(room_filter_frame, values=db_sizes, state="readonly", width=14, font=("Segoe UI", 9))
    room_dropdown.set("All Types")
    room_dropdown.pack(side="left")

    def on_room_filter_change(event):
        global current_room_filter
        val = room_dropdown.get()
        current_room_filter = "All" if val == "All Types" else val
        load_houses("All")

    room_dropdown.bind("<<ComboboxSelected>>", on_room_filter_change)

    ttk.Separator(home, orient="horizontal").pack(fill="x", padx=20)

    canvas = tk.Canvas(home, bg="#FFFFFF", highlightthickness=0)
    scrollbar = ttk.Scrollbar(home, orient="vertical", command=canvas.yview)
    grid_container = tk.Frame(canvas, bg="#FFFFFF")

    canvas_window = canvas.create_window((0, 0), window=grid_container, anchor="nw")
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    grid_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
    scrollbar.pack(side="right", fill="y")

    # --- MODERNIZED AESTHETIC BOOKING BAR ---
    bbar = tk.Frame(home, bg="#FFFFFF", bd=1, relief="solid")
    bbar.pack(fill="x", side="bottom", padx=20, pady=12, ipady=8)

    lbl_selected = tk.Label(bbar, text="Selected Stay: None", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#FF385C")
    lbl_selected.pack(side="left", padx=15)

    btn_book = tk.Button(bbar, text="Book Stay", command=book_house, bg="#FF385C", fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=18, pady=6)
    btn_book.pack(side="right", padx=15)

    date_frame = tk.Frame(bbar, bg="#FFFFFF", highlightbackground="#DDDDDD", highlightthickness=1, padx=8, pady=3)
    date_frame.pack(side="right", padx=10)

    tk.Label(date_frame, text="📅", font=("Segoe UI", 9), bg="#FFFFFF").pack(side="left", padx=(2, 6))

    today_str = date.today().strftime("%Y-%m-%d")
    cin_box = tk.Frame(date_frame, bg="#FFFFFF")
    cin_box.pack(side="left", padx=4)
    tk.Label(cin_box, text="CHECK-IN", font=("Segoe UI", 7, "bold"), bg="#FFFFFF", fg="#717171").pack(anchor="w")
    ent_cin = tk.Entry(cin_box, width=11, font=("Segoe UI", 9, "bold"), fg="#222222", bd=0, justify="left")
    ent_cin.insert(0, today_str)
    ent_cin.pack(anchor="w")

    ttk.Separator(date_frame, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

    cout_box = tk.Frame(date_frame, bg="#FFFFFF")
    cout_box.pack(side="left", padx=4)
    tk.Label(cout_box, text="CHECKOUT", font=("Segoe UI", 7, "bold"), bg="#FFFFFF", fg="#717171").pack(anchor="w")
    ent_cout = tk.Entry(cout_box, width=11, font=("Segoe UI", 9, "bold"), fg="#222222", bd=0, justify="left")
    ent_cout.insert(0, "2026-11-05")
    ent_cout.pack(anchor="w")

    load_houses()

# --- INITIALIZATION & LOGIN FRAME ---
root = tk.Tk()
root.title("Airbnb Project - CBSE Class 12 Computer Science")
root.geometry("980x680")
root.configure(bg="#FFFFFF")

login_frame = tk.Frame(root, bg="#FFFFFF")
login_frame.pack(pady=70)

tk.Label(login_frame, text="airbnb", font=("Segoe UI", 36, "bold"), fg="#FF385C", bg="#FFFFFF").pack(pady=10)
tk.Label(login_frame, text="Find your next getaway", font=("Segoe UI", 11), fg="#717171", bg="#FFFFFF").pack(pady=(0, 20))

tk.Label(login_frame, text="Username:", font=("Segoe UI", 10, "bold"), fg="#222222", bg="#FFFFFF").pack(anchor="w")
ent_login_user = tk.Entry(login_frame, width=30, font=("Segoe UI", 11), bd=1, relief="solid")
ent_login_user.pack(pady=(3, 12), ipady=3)

tk.Label(login_frame, text="Password:", font=("Segoe UI", 10, "bold"), fg="#222222", bg="#FFFFFF").pack(anchor="w")
ent_login_pass = tk.Entry(login_frame, show="*", width=30, font=("Segoe UI", 11), bd=1, relief="solid")
ent_login_pass.pack(pady=(3, 18), ipady=3)

tk.Button(login_frame, text="Log In", command=login_action, bg="#FF385C", fg="white", font=("Segoe UI", 10, "bold"), width=24, bd=0, pady=8).pack(pady=5)
tk.Button(login_frame, text="Create Account", command=register_action, bg="#FFFFFF", fg="#222222", bd=0, font=("Segoe UI", 9, "underline")).pack(pady=8)

root.mainloop()
