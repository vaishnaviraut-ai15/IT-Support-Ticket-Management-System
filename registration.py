import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


def register_user():
    name = name_entry.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get()
    department = department_combo.get()

    # Check empty fields
    if name == "" or username == "" or password == "" or department == "":
        messagebox.showwarning(
            "Missing Information",
            "Please fill all fields."
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

        # Check whether username already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s",
            (username,)
        )

        if cursor.fetchone() is not None:
            messagebox.showerror(
                "Registration Failed",
                "Username already exists."
            )
            return

        # Insert new user
        query = """
        INSERT INTO users
        (name, username, password, department, role)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            username,
            password,
            department,
            "User"
        )

        cursor.execute(query, values)
        connection.commit()

        messagebox.showinfo(
            "Success",
            "Registration successful!"
        )

        # Clear form
        name_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        department_combo.set("")

    except Exception as e:
        connection.rollback()
        messagebox.showerror(
            "Error",
            f"Registration failed:\n{e}"
        )

    finally:
        cursor.close()
        connection.close()


# ---------------- GUI ----------------

window = tk.Tk()
window.title("IT Support - Registration")
window.geometry("450x400")
window.resizable(False, False)


title_label = tk.Label(
    window,
    text="IT Support Ticket System",
    font=("Arial", 20, "bold")
)
title_label.pack(pady=15)


registration_label = tk.Label(
    window,
    text="User Registration",
    font=("Arial", 15)
)
registration_label.pack(pady=5)


# Name
tk.Label(
    window,
    text="Name:",
    font=("Arial", 11)
).pack(anchor="w", padx=60, pady=(15, 3))

name_entry = tk.Entry(
    window,
    width=35
)
name_entry.pack()


# Username
tk.Label(
    window,
    text="Username:",
    font=("Arial", 11)
).pack(anchor="w", padx=60, pady=(10, 3))

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
).pack(anchor="w", padx=60, pady=(10, 3))

password_entry = tk.Entry(
    window,
    width=35,
    show="*"
)
password_entry.pack()


# Department
tk.Label(
    window,
    text="Department:",
    font=("Arial", 11)
).pack(anchor="w", padx=60, pady=(10, 3))

department_combo = ttk.Combobox(
    window,
    width=32,
    state="readonly",
    values=[
        "Computer",
        "IT",
        "HR",
        "Finance",
        "Management",
        "Other"
    ]
)
department_combo.pack()


# Register button
register_button = tk.Button(
    window,
    text="REGISTER",
    width=20,
    command=register_user
)
register_button.pack(pady=25)


window.mainloop()
