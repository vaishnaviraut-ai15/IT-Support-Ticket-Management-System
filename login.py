import tkinter as tk
from tkinter import messagebox
from database import get_connection
from user_dashboard import open_dashboard
from admin_dashboard import open_admin_dashboard

def login_user():
    username = username_entry.get().strip()
    password = password_entry.get()

    # Check empty fields
    if username == "" or password == "":
        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password."
        )
        return

    connection = get_connection()

    if connection is None:
        messagebox.showerror(
            "Database Error",
            "Could not connect to MySQL."
        )
        return

    try:
        cursor = connection.cursor()

        query = """
        SELECT user_id, name, role
        FROM users
        WHERE username = %s AND password = %s
        """

        values = (username, password)

        cursor.execute(query, values)

        user = cursor.fetchone()

        if user is not None:
            user_id, name, role = user

            messagebox.showinfo(
                "Login Successful",
                f"Welcome, {name}!"
            )

            window.destroy()

            if role == "Staff":
                open_admin_dashboard(user_id, name, role)
            else:
                open_dashboard(user_id, name, role)

        else:
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Login failed:\n{e}"
        )

    finally:
        cursor.close()
        connection.close()


# ---------------- GUI ----------------

window = tk.Tk()
window.title("IT Support - Login")
window.geometry("450x350")
window.resizable(False, False)


# Title
title_label = tk.Label(
    window,
    text="IT Support Ticket System",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=25)


# Login heading
login_label = tk.Label(
    window,
    text="Login",
    font=("Arial", 16)
)
login_label.pack(pady=5)


# Username
tk.Label(
    window,
    text="Username:",
    font=("Arial", 11)
).pack(anchor="w", padx=70, pady=(20, 3))

username_entry = tk.Entry(
    window,
    width=35
)
username_entry.pack()


# Password
tk.Label(
    window,
    text="Password:",
    font=("Arial", 11)
).pack(anchor="w", padx=70, pady=(15, 3))

password_entry = tk.Entry(
    window,
    width=35,
    show="*"
)
password_entry.pack()


# Login button
login_button = tk.Button(
    window,
    text="LOGIN",
    width=20,
    command=login_user
)
login_button.pack(pady=25)


window.mainloop()
