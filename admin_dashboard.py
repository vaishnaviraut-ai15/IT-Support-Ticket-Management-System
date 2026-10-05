import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


def open_admin_dashboard(user_id, name, role):

    # ---------------- PYTHON DICTIONARY ----------------

    priority_info = {
        "Low": "Normal priority",
        "Medium": "Needs attention",
        "High": "Urgent issue"
    }

    # ---------------- PYTHON SET ----------------

    ticket_categories = {
        "Hardware",
        "Software",
        "Network",
        "Printer",
        "Login/Account",
        "Other"
    }

    window = tk.Tk()

    window.title("IT Support - Staff Dashboard")
    window.geometry("1200x650")
    window.resizable(False, False)

    # ---------------- TITLE ----------------

    tk.Label(
        window,
        text="IT Support Staff Dashboard",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(
        window,
        text=f"Welcome, {name}    |    Role: {role}",
        font=("Arial", 11)
    ).pack(pady=5)

    # ---------------- SEARCH ----------------

    search_frame = tk.Frame(window)
    search_frame.pack(pady=10)

    tk.Label(
        search_frame,
        text="Search:"
    ).pack(side="left", padx=5)

    search_entry = tk.Entry(
        search_frame,
        width=30
    )
    search_entry.pack(side="left", padx=5)

    tk.Label(
        search_frame,
        text="Status:"
    ).pack(side="left", padx=5)

    status_combo = ttk.Combobox(
        search_frame,
        values=[
            "All",
            "Open",
            "In Progress",
            "Resolved",
            "Closed"
        ],
        state="readonly",
        width=15
    )

    status_combo.set("All")
    status_combo.pack(side="left", padx=5)

    # ---------------- TABLE ----------------

    table_frame = tk.Frame(window)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    columns = (
        "ID",
        "User",
        "Department",
        "Title",
        "Category",
        "Priority",
        "Status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=15
    )

    for column in columns:
        tree.heading(
            column,
            text=column
        )

    tree.column("ID", width=60)
    tree.column("User", width=150)
    tree.column("Department", width=110)
    tree.column("Title", width=250)
    tree.column("Category", width=120)
    tree.column("Priority", width=90)
    tree.column("Status", width=110)

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    # ---------------- LOAD ALL TICKETS ----------------

    def load_tickets():

        for item in tree.get_children():
            tree.delete(item)

        search_text = search_entry.get().strip()
        selected_status = status_combo.get()

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to MySQL."
            )
            return

        cursor = None

        try:

            cursor = connection.cursor()

            query = """
                SELECT
                    tickets.ticket_id,
                    users.name,
                    users.department,
                    tickets.title,
                    tickets.category,
                    tickets.priority,
                    tickets.status
                FROM tickets
                JOIN users
                    ON tickets.user_id = users.user_id
                WHERE 1=1
            """

            values = []

            if search_text != "":
                query += """
                    AND (
                        users.name LIKE %s
                        OR tickets.title LIKE %s
                        OR tickets.category LIKE %s
                    )
                """

                search_value = "%" + search_text + "%"

                values.append(search_value)
                values.append(search_value)
                values.append(search_value)

            if selected_status != "All":
                query += " AND tickets.status = %s"
                values.append(selected_status)

            query += """
                ORDER BY tickets.ticket_id DESC
            """

            cursor.execute(
                query,
                tuple(values)
            )

            tickets = cursor.fetchall()

            for ticket in tickets:

                tree.insert(
                    "",
                    tk.END,
                    values=ticket
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not load tickets:\n{e}"
            )

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ---------------- UPDATE TICKET STATUS ----------------

    def update_ticket():

        selected_item = tree.selection()

        if not selected_item:

            messagebox.showwarning(
                "Selection Required",
                "Please select a ticket first."
            )

            return

        values = tree.item(
            selected_item[0],
            "values"
        )

        ticket_id = values[0]

        update_window = tk.Toplevel(window)

        update_window.title(
            "Update Ticket Status"
        )

        update_window.geometry(
            "450x400"
        )

        update_window.resizable(
            False,
            False
        )

        tk.Label(
            update_window,
            text=f"Ticket #{ticket_id}",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        # Status

        tk.Label(
            update_window,
            text="Status"
        ).pack(pady=5)

        status_update = ttk.Combobox(
            update_window,
            values=[
                "Open",
                "In Progress",
                "Resolved",
                "Closed"
            ],
            state="readonly",
            width=35
        )

        status_update.pack()

        status_update.set(
            values[6]
        )

        # Resolution

        tk.Label(
            update_window,
            text="Resolution"
        ).pack(pady=(20, 5))

        resolution_text = tk.Text(
            update_window,
            width=40,
            height=8
        )

        resolution_text.pack()

        def save_update():

            new_status = status_update.get()

            new_resolution = resolution_text.get(
                "1.0",
                tk.END
            ).strip()

            if not new_status:

                messagebox.showwarning(
                    "Validation",
                    "Please select a status."
                )

                return

            connection = get_connection()

            if connection is None:

                messagebox.showerror(
                    "Database Error",
                    "Could not connect to MySQL."
                )

                return

            cursor = None

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE tickets
                    SET status = %s,
                        resolution = %s
                    WHERE ticket_id = %s
                """, (
                    new_status,
                    new_resolution,
                    ticket_id
                ))

                connection.commit()

                messagebox.showinfo(
                    "Success",
                    "Ticket status updated successfully."
                )

                update_window.destroy()

                load_tickets()

            except Exception as e:

                connection.rollback()

                messagebox.showerror(
                    "Error",
                    f"Could not update ticket:\n{e}"
                )

            finally:

                if cursor:
                    cursor.close()

                connection.close()

        tk.Button(
            update_window,
            text="SAVE UPDATE",
            width=20,
            command=save_update
        ).pack(pady=20)

    # ---------------- TICKET STATISTICS ----------------

    def show_statistics():

        stats_window = tk.Toplevel(window)
        stats_window.title("Ticket Statistics")
        stats_window.geometry("500x450")
        stats_window.resizable(False, False)

        tk.Label(
            stats_window,
            text="Ticket Statistics",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to MySQL."
            )
            stats_window.destroy()
            return

        cursor = None

        try:

            cursor = connection.cursor()

            # -------- STATUS STATISTICS --------

            cursor.execute("""
                SELECT status, COUNT(*)
                FROM tickets
                GROUP BY status
            """)

            status_results = cursor.fetchall()

            tk.Label(
                stats_window,
                text="Tickets by Status",
                font=("Arial", 13, "bold")
            ).pack(pady=10)

            for status, count in status_results:

                tk.Label(
                    stats_window,
                    text=f"{status}: {count}"
                ).pack()

            # -------- CATEGORY STATISTICS --------

            cursor.execute("""
                SELECT category, COUNT(*)
                FROM tickets
                GROUP BY category
            """)

            category_results = cursor.fetchall()

            tk.Label(
                stats_window,
                text="Tickets by Category",
                font=("Arial", 13, "bold")
            ).pack(pady=20)

            for category, count in category_results:

                tk.Label(
                    stats_window,
                    text=f"{category}: {count}"
                ).pack()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not load statistics:\n{e}"
            )

        finally:

            if cursor:
                cursor.close()

            connection.close()

        # ---------------- BUTTONS ----------------

    tk.Button(
        search_frame,
        text="SEARCH",
        width=12,
        command=load_tickets
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="REFRESH",
        width=12,
        command=load_tickets
    ).pack(side="left", padx=5)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="UPDATE STATUS",
        width=18,
        command=update_ticket
    ).pack(side="left", padx=10)

    tk.Button(
        button_frame,
        text="STATISTICS",
        width=18,
        command=show_statistics
    ).pack(side="left", padx=10)

    tk.Button(
        button_frame,
        text="LOGOUT",
        width=18,
        command=window.destroy
    ).pack(side="left", padx=10)

    # Initial data

    load_tickets()

    window.mainloop()
