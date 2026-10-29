import os
import pickle
import csv
from datetime import datetime, date
import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk

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

def open_about_us_window():
    file_path = "about_us.txt"
    if not os.path.exists(file_path):
        messagebox.showerror("File Error", f"'{file_path}' not found in project folder!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    about_win = tk.Toplevel(root)
    about_win.title("About Us")
    about_win.geometry("450x380")
    about_win.configure(bg="#FFFFFF")

    tk.Label(about_win, text="About Airbnb", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#FF385C").pack(pady=10)

    text_frame = tk.Frame(about_win, bg="#FFFFFF")
    text_frame.pack(fill="both", expand=True, padx=15, pady=10)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    txt_display = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set, font=("Courier", 9), bg="#F7F7F7", bd=1, relief="solid")
    txt_display.insert("1.0", file_content)
    txt_display.config(state="disabled")
    txt_display.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=txt_display.yview)

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

# --- ADMIN DASHBOARD ---
def open_admin_dashboard():
    admin_win = tk.Toplevel(root)
    admin_win.title("Airbnb Admin Dashboard")
    admin_win.geometry("750x500")
    admin_win.configure(bg="#F7F7F7")

    tk.Label(admin_win, text="🛠️ Admin Control Panel", font=("Segoe UI", 16, "bold"), bg="#F7F7F7", fg="#222222").pack(pady=10)

    lbl_b = tk.Label(admin_win, text="All Customer Bookings", font=("Segoe UI", 11, "bold"), bg="#F7F7F7", fg="#FF385C")
    lbl_b.pack(anchor="w", padx=20, pady=(5, 2))

    tree_b = ttk.Treeview(admin_win, columns=("BID", "User", "House", "CheckIn", "CheckOut"), show="headings", height=6)
    tree_b.heading("BID", text="Booking ID")
    tree_b.heading("User", text="User Name")
    tree_b.heading("House", text="House ID")
    tree_b.heading("CheckIn", text="Check-In")
    tree_b.heading("CheckOut", text="Check-Out")

    tree_b.column("BID", width=80, anchor="center")
    tree_b.column("User", width=150)
    tree_b.column("House", width=80, anchor="center")
    tree_b.column("CheckIn", width=120, anchor="center")
    tree_b.column("CheckOut", width=120, anchor="center")
    tree_b.pack(fill="x", padx=20)

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

    frame_price = tk.LabelFrame(admin_win, text="Manage House Prices", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", padx=15, pady=10)
    frame_price.pack(fill="x", padx=20, pady=15)

    tk.Label(frame_price, text="House ID:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5)
    ent_hid = tk.Entry(frame_price, width=8, font=("Segoe UI", 10))
    ent_hid.grid(row=0, column=1, padx=5)

    tk.Label(frame_price, text="New Price (₹):", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5)
    ent_new_price = tk.Entry(frame_price, width=12, font=("Segoe UI", 10))
    ent_new_price.grid(row=0, column=3, padx=5)

    def update_price_action():
        hid = ent_hid.get().strip()
        np = ent_new_price.get().strip()
        if not hid or not np:
            messagebox.showwarning("Input Error", "Please provide House ID and New Price!")
            return
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE houses SET price_per_night = %s WHERE house_id = %s", (np, hid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Price for House #{hid} updated successfully!")
            load_houses()

    def reset_price_action():
        hid = ent_hid.get().strip()
        if not hid:
            messagebox.showwarning("Input Error", "Please provide House ID!")
            return
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE houses SET price_per_night = 0 WHERE house_id = %s", (hid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Price for House #{hid} cleared/set to 0!")
            load_houses()

    btn_upd = tk.Button(frame_price, text="Update Price", command=update_price_action, bg="#222222", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=8, pady=4)
    btn_upd.grid(row=0, column=4, padx=10)

    btn_del_p = tk.Button(frame_price, text="Clear Price", command=reset_price_action, bg="#FF385C", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=8, pady=4)
    btn_del_p.grid(row=0, column=5, padx=5)

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
            messagebox.showwarning("Warning", "All fields required!")
            return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (full_name, username, password) VALUES (%s, %s, %s)", (n, u, p))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                reg_win.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
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

# --- DISPLAY HOUSES WITH SPACIOUS CARDS ---
def load_houses(category="All"):
    global selected_house_id, selected_card_frame
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
            hdr.grid(row=current_row_idx, column=0, columnspan=3, sticky="w", pady=(18, 6), padx=15)
            tk.Label(hdr, text=f"📍 Stays in {dest_name} ({len(houses)} available)", font=("Segoe UI", 13, "bold"), bg="#FFFFFF", fg="#222222").pack(side="left")
            current_row_idx += 1

            for idx, h in enumerate(houses):
                r = current_row_idx + (idx // 3)
                c = idx % 3

                h_id = h["house_id"]
                h_title = h["title"]
                house_num = idx + 1

                card = tk.Frame(grid_container, bg="#FFFFFF", highlightbackground="#EBEBEB", highlightthickness=1, cursor="hand2")
                # Increased padding to spread cards out more across the screen
                card.grid(row=r, column=c, padx=16, pady=14, sticky="nsew")
                card.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                canvas = tk.Canvas(card, width=295, height=165, bg="#F7F7F7", highlightthickness=0)
                canvas.pack(fill="x")
                canvas.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                script_dir = os.path.dirname(os.path.abspath(__file__))
                img_path = os.path.join(script_dir, f"{h_id}.png")

                if os.path.exists(img_path):
                    try:
                        img = tk.PhotoImage(file=img_path)
                        loaded_images[h_id] = img
                        canvas.create_image(147, 82, image=img)
                    except Exception:
                        canvas.create_text(147, 82, text="🏠 Image Error", fill="#717171")
                else:
                    canvas.create_text(147, 82, text=f"🏠 {dest_name} {house_num}", font=("Segoe UI", 10, "bold"), fill="#222222")

                info = tk.Frame(card, bg="#FFFFFF", padx=12, pady=10)
                info.pack(fill="both", expand=True)
                info.bind("<Button-1>", lambda e, i=h_id, f=card, t=h_title: select_card(i, f, t))

                tk.Label(info, text=h_title, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", anchor="w", wraplength=265, justify="left").pack(anchor="w", pady=2)
                tk.Label(info, text=h["size"], font=("Segoe UI", 8), fg="#717171", bg="#FFFFFF", anchor="w").pack(anchor="w")
                tk.Label(info, text=f"₹{h['price_per_night']:,.0f} / night", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", anchor="w").pack(anchor="w", pady=(6, 0))

            current_row_idx += ((len(houses) - 1) // 3) + 1

        for i in range(3):
            grid_container.columnconfigure(i, weight=1)

# --- POST-BOOKING & PAYMENT SUMMARY PAGE ---
def show_booking_confirmation(booking_id, house_title, cin, cout, price_per_night, nights):
    pay_win = tk.Toplevel(root)
    pay_win.title("Booking Details & Payment Confirmation")
    pay_win.geometry("450x540")
    pay_win.configure(bg="#FFFFFF")

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
        messagebox.showinfo("Payment Successful", f"Payment of ₹{total_amount:,.2f} completed via {pay_opt.get()}!\nReceipt exported to 'bookings_report.csv'.")
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
    global grid_container, ent_search, lbl_selected, ent_cin, ent_cout

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

    cat_bar = tk.Frame(home, bg="#FFFFFF")
    cat_bar.pack(fill="x", padx=20, pady=8)

    for cat in ["All", "City", "Mountains", "Beaches", "Island"]:
        btn = tk.Button(cat_bar, text=cat, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#222222", bd=0, command=lambda c=cat: load_houses(c))
        btn.pack(side="left", padx=10)

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