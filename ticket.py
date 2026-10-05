import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


def open_create_ticket(user_id):
    window = tk.Toplevel()
    window.title("Create Support Ticket")
    window.geometry("550x600")
    window.resizable(False, False)

    # Title
    tk.Label(
        window,
        text="Create Support Ticket",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    # Problem title
    tk.Label(
        window,
        text="Problem Title:",
        font=("Arial", 11)
    ).pack(anchor="w", padx=60, pady=(10, 3))

    title_entry = tk.Entry(
        window,
        width=50
    )
    title_entry.pack()

    # Category
    tk.Label(
        window,
        text="Category:",
        font=("Arial", 11)
    ).pack(anchor="w", padx=60, pady=(15, 3))

    category_combo = ttk.Combobox(
        window,
        width=47,
        state="readonly",
        values=[
            "Hardware",
            "Software",
            "Network",
            "Printer",
            "Login/Account",
            "Other"
        ]
    )
    category_combo.pack()

    # Description
    tk.Label(
        window,
        text="Description:",
        font=("Arial", 11)
    ).pack(anchor="w", padx=60, pady=(15, 3))

    description_text = tk.Text(
        window,
        width=50,
        height=7
    )
    description_text.pack()

    # Priority
    tk.Label(
        window,
        text="Priority:",
        font=("Arial", 11)
    ).pack(anchor="w", padx=60, pady=(15, 3))

    priority_var = tk.StringVar(value="Medium")

    priority_frame = tk.Frame(window)
    priority_frame.pack()

    tk.Radiobutton(
        priority_frame,
        text="Low",
        variable=priority_var,
        value="Low"
    ).pack(side="left", padx=15)

    tk.Radiobutton(
        priority_frame,
        text="Medium",
        variable=priority_var,
        value="Medium"
    ).pack(side="left", padx=15)

    tk.Radiobutton(
        priority_frame,
        text="High",
        variable=priority_var,
        value="High"
    ).pack(side="left", padx=15)

    # Submit function
    def submit_ticket():

        title = title_entry.get().strip()
        category = category_combo.get()
        description = description_text.get("1.0", tk.END).strip()
        priority = priority_var.get()

        # Validation
        if title == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter the problem title."
            )
            return

        if category == "":
            messagebox.showwarning(
                "Missing Information",
                "Please select a category."
            )
            return

        if description == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter the problem description."
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
            INSERT INTO tickets
            (user_id, title, category, description, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (
                user_id,
                title,
                category,
                description,
                priority,
                "Open"
            )

            cursor.execute(query, values)
            connection.commit()

            ticket_id = cursor.lastrowid

            messagebox.showinfo(
                "Ticket Created",
                f"Ticket created successfully!\n\n"
                f"Ticket ID: {ticket_id}"
            )

            # Clear form
            title_entry.delete(0, tk.END)
            category_combo.set("")
            description_text.delete("1.0", tk.END)
            priority_var.set("Medium")

        except Exception as e:
            connection.rollback()

            messagebox.showerror(
                "Error",
                f"Could not create ticket:\n{e}"
            )

        finally:
            cursor.close()
            connection.close()

    # Submit button
    tk.Button(
        window,
        text="SUBMIT TICKET",
        width=25,
        height=2,
        command=submit_ticket
    ).pack(pady=25)
