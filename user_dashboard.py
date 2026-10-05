import tkinter as tk
from tkinter import ttk, messagebox
from ticket import open_create_ticket
from database import get_connection


# ---------------- CREATE TICKET ----------------

def create_ticket():
    open_create_ticket(current_user_id)


# ---------------- VIEW TICKETS ----------------

def view_tickets():

    ticket_window = tk.Toplevel(window)
    ticket_window.title("My Tickets")
    ticket_window.geometry("1100x650")
    ticket_window.resizable(False, False)

    tk.Label(
        ticket_window,
        text="My Support Tickets",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    # ---------------- SEARCH & FILTER ----------------

    search_frame = tk.Frame(ticket_window)
    search_frame.pack(pady=5)

    tk.Label(
        search_frame,
        text="Search:"
    ).pack(side="left", padx=5)

    search_entry = tk.Entry(
        search_frame,
        width=25
    )
    search_entry.pack(side="left", padx=5)

    tk.Label(
        search_frame,
        text="Status:"
    ).pack(side="left", padx=5)

    status_combo = ttk.Combobox(
        search_frame,
        width=15,
        state="readonly",
        values=[
            "All",
            "Open",
            "In Progress",
            "Resolved",
            "Closed"
        ]
    )
    status_combo.set("All")
    status_combo.pack(side="left", padx=5)

    # ---------------- TABLE ----------------

    table_frame = tk.Frame(ticket_window)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    columns = (
        "ID",
        "Title",
        "Category",
        "Priority",
        "Status"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=12
    )

    for column in columns:
        tree.heading(column, text=column)

    tree.column("ID", width=70)
    tree.column("Title", width=300)
    tree.column("Category", width=170)
    tree.column("Priority", width=130)
    tree.column("Status", width=130)

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

    # ---------------- LOAD TICKETS ----------------

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
                SELECT ticket_id, title, category, priority, status
                FROM tickets
                WHERE user_id = %s
            """

            values = [current_user_id]

            if search_text != "":
                query += """
                    AND (
                        title LIKE %s
                        OR category LIKE %s
                    )
                """

                search_value = "%" + search_text + "%"

                values.append(search_value)
                values.append(search_value)

            if selected_status != "All":
                query += " AND status = %s"
                values.append(selected_status)

            query += " ORDER BY ticket_id DESC"

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

    # ---------------- GET SELECTED TICKET ----------------

    def get_selected_ticket():

        selected_item = tree.selection()

        if not selected_item:
            messagebox.showwarning(
                "Selection Required",
                "Please select a ticket first."
            )
            return None

        values = tree.item(
            selected_item[0],
            "values"
        )

        return values

    # ---------------- UPDATE TICKET ----------------

    def update_ticket():

        selected = get_selected_ticket()

        if not selected:
            return

        ticket_id = selected[0]

        edit_window = tk.Toplevel(ticket_window)
        edit_window.title("Update Ticket")
        edit_window.geometry("450x500")
        edit_window.resizable(False, False)

        # Get current ticket details

        connection = get_connection()

        if connection is None:
            messagebox.showerror(
                "Database Error",
                "Could not connect to database."
            )
            edit_window.destroy()
            return

        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT title, category, description, priority
                FROM tickets
                WHERE ticket_id = %s
                AND user_id = %s
            """, (
                ticket_id,
                current_user_id
            ))

            ticket = cursor.fetchone()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

            edit_window.destroy()
            return

        finally:

            if cursor:
                cursor.close()

            connection.close()

        if not ticket:

            messagebox.showerror(
                "Error",
                "Ticket not found."
            )

            edit_window.destroy()
            return

        # ---------------- TITLE ----------------

        tk.Label(
            edit_window,
            text="Problem Title"
        ).pack(pady=(15, 5))

        title_entry = tk.Entry(
            edit_window,
            width=45
        )
        title_entry.pack()

        title_entry.insert(
            0,
            ticket[0]
        )

        # ---------------- CATEGORY ----------------

        tk.Label(
            edit_window,
            text="Category"
        ).pack(pady=(15, 5))

        category_combo = ttk.Combobox(
            edit_window,
            values=[
                "Hardware",
                "Software",
                "Network",
                "Printer",
                "Login/Account",
                "Other"
            ],
            state="readonly",
            width=42
        )

        category_combo.pack()

        category_combo.set(
            ticket[1]
        )

        # ---------------- DESCRIPTION ----------------

        tk.Label(
            edit_window,
            text="Description"
        ).pack(pady=(15, 5))

        description_text = tk.Text(
            edit_window,
            width=45,
            height=7
        )

        description_text.pack()

        description_text.insert(
            "1.0",
            ticket[2]
        )

        # ---------------- PRIORITY ----------------

        tk.Label(
            edit_window,
            text="Priority"
        ).pack(pady=(15, 5))

        priority_combo = ttk.Combobox(
            edit_window,
            values=[
                "Low",
                "Medium",
                "High"
            ],
            state="readonly",
            width=42
        )

        priority_combo.pack()

        priority_combo.set(
            ticket[3]
        )

        # ---------------- SAVE CHANGES ----------------

        def save_changes():

            new_title = title_entry.get().strip()
            new_category = category_combo.get()
            new_description = description_text.get(
                "1.0",
                tk.END
            ).strip()
            new_priority = priority_combo.get()

            # Validation

            if not new_title:
                messagebox.showwarning(
                    "Validation",
                    "Problem title cannot be empty."
                )
                return

            if not new_category:
                messagebox.showwarning(
                    "Validation",
                    "Please select a category."
                )
                return

            if not new_description:
                messagebox.showwarning(
                    "Validation",
                    "Description cannot be empty."
                )
                return

            if not new_priority:
                messagebox.showwarning(
                    "Validation",
                    "Please select priority."
                )
                return

            # NEW database connection

            connection = get_connection()

            if connection is None:
                messagebox.showerror(
                    "Database Error",
                    "Could not connect to database."
                )
                return

            cursor = None

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    UPDATE tickets
                    SET title = %s,
                        category = %s,
                        description = %s,
                        priority = %s
                    WHERE ticket_id = %s
                    AND user_id = %s
                """, (
                    new_title,
                    new_category,
                    new_description,
                    new_priority,
                    ticket_id,
                    current_user_id
                ))

                connection.commit()

                messagebox.showinfo(
                    "Success",
                    "Ticket updated successfully."
                )

                edit_window.destroy()

                load_tickets()

            except Exception as e:

                connection.rollback()

                messagebox.showerror(
                    "Error",
                    f"Could not update ticket.\n\n{e}"
                )

            finally:

                if cursor:
                    cursor.close()

                connection.close()

        # SAVE BUTTON

        tk.Button(
            edit_window,
            text="SAVE CHANGES",
            command=save_changes,
            width=20
        ).pack(pady=25)

    # ---------------- DELETE TICKET ----------------

    def delete_ticket():

        selected_ticket = get_selected_ticket()

        if selected_ticket is None:
            return

        ticket_id = selected_ticket[0]

        confirm = messagebox.askyesno(
            "Delete Ticket",
            f"Are you sure you want to delete Ticket #{ticket_id}?"
        )

        if not confirm:
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
                DELETE FROM tickets
                WHERE ticket_id = %s
                AND user_id = %s
            """, (
                ticket_id,
                current_user_id
            ))

            connection.commit()

            messagebox.showinfo(
                "Success",
                "Ticket deleted successfully."
            )

            load_tickets()

        except Exception as e:

            connection.rollback()

            messagebox.showerror(
                "Error",
                f"Could not delete ticket:\n{e}"
            )

        finally:

            if cursor:
                cursor.close()

            connection.close()

    # ---------------- BUTTONS ----------------

    tk.Button(
        search_frame,
        text="SEARCH",
        command=load_tickets
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="REFRESH",
        command=load_tickets
    ).pack(side="left", padx=5)

    button_frame = tk.Frame(ticket_window)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="UPDATE",
        width=15,
        command=update_ticket
    ).pack(side="left", padx=10)

    tk.Button(
        button_frame,
        text="DELETE",
        width=15,
        command=delete_ticket
    ).pack(side="left", padx=10)

    # Initial load

    load_tickets()


# ---------------- SEARCH TICKET ----------------

def search_ticket():

    messagebox.showinfo(
        "Search Ticket",
        "Use the Search box in My Tickets."
    )


# ---------------- LOGOUT ----------------

def logout():

    result = messagebox.askyesno(
        "Logout",
        "Are you sure you want to logout?"
    )

    if result:
        window.destroy()


# ---------------- OPEN DASHBOARD ----------------

def open_dashboard(user_id, name, role):

    global window
    global current_user_id

    current_user_id = user_id

    window = tk.Tk()

    window.title(
        "IT Support - User Dashboard"
    )

    window.geometry(
        "500x450"
    )

    window.resizable(
        False,
        False
    )

    # Title

    tk.Label(
        window,
        text="IT Support Ticket System",
        font=("Arial", 20, "bold")
    ).pack(pady=25)

    # Welcome

    tk.Label(
        window,
        text=f"Welcome, {name}!",
        font=("Arial", 16)
    ).pack(pady=5)

    # User information

    tk.Label(
        window,
        text=f"User ID: {user_id}    |    Role: {role}",
        font=("Arial", 10)
    ).pack(pady=5)

    # CREATE TICKET

    tk.Button(
        window,
        text="CREATE TICKET",
        width=25,
        height=2,
        command=create_ticket
    ).pack(pady=15)

    # MY TICKETS

    tk.Button(
        window,
        text="MY TICKETS",
        width=25,
        height=2,
        command=view_tickets
    ).pack(pady=5)

    # SEARCH TICKET

    tk.Button(
        window,
        text="SEARCH TICKET",
        width=25,
        height=2,
        command=search_ticket
    ).pack(pady=5)

    # LOGOUT

    tk.Button(
        window,
        text="LOGOUT",
        width=25,
        height=2,
        command=logout
    ).pack(pady=20)

    window.mainloop()
