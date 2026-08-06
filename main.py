"""
BMI Calculator & Health Tracker - Main Application GUI
=====================================================
A modern, feature-rich Tkinter desktop application for calculating Body Mass Index (BMI),
tracking historical health data with SQLite3, and visualizing trends with matplotlib.

Features included:
- Professional Tkinter GUI with custom theme colors
- Live clock displaying date and time
- Interactive input form with Combobox auto-suggestions for user names
- Calculate, Save, View History, Show Graph, Clear, and Exit controls
- Color-coded BMI result presentation card with health advice
- Secondary Treeview History window with record management
- Hover tooltips on controls
- Keyboard Enter key shortcut support
- Responsive and resizable grid layout
"""

import os
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

# Import custom application modules
from bmi import calculate_bmi, get_bmi_category, validate_inputs
from database import (
    init_db,
    save_record,
    get_user_history,
    get_all_users,
    delete_record,
    clear_user_history,
    DEFAULT_DB_PATH
)
from graph import plot_bmi_trend


class ToolTip:
    """
    Creates a popup tooltip showing helpful text when hovering over a widget.
    """
    def __init__(self, widget: tk.Widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window: Optional[tk.Toplevel] = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None) -> None:
        """Displays the tooltip floating window near the widget cursor position."""
        if self.tip_window or not self.text:
            return
        # Calculate tooltip position relative to widget root coordinates
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window borders
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#0F172A",  # Dark slate background
            foreground="#F8FAFC",  # White text
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9, "normal"),
            padx=8,
            pady=4
        )
        label.pack()

    def hide_tip(self, event=None) -> None:
        """Destroys the tooltip floating window when mouse leaves the widget."""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class HistoryWindow(tk.Toplevel):
    """
    Secondary Toplevel window displaying historical records for a specific user using ttk.Treeview.
    """
    def __init__(self, parent: tk.Tk, username: str, db_path: str = DEFAULT_DB_PATH):
        super().__init__(parent)
        self.parent = parent
        self.username = username
        self.db_path = db_path

        self.title(f"BMI Health History - {username}")
        self.geometry("750x450")
        self.minsize(650, 350)
        self.configure(bg="#F1F5F9")

        # Make modal window relative to parent
        self.transient(parent)
        self.focus_set()

        self._build_ui()
        self.load_data()

    def _build_ui(self) -> None:
        """Constructs the Treeview UI elements and control buttons."""
        # Header title frame
        header_frame = tk.Frame(self, bg="#1E293B", pady=12, padx=16)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text=f"📊 Historical BMI Records: {self.username}",
            font=("Segoe UI", 14, "bold"),
            bg="#1E293B",
            fg="#F8FAFC"
        )
        title_lbl.pack(side=tk.LEFT)

        # Table Container Frame
        table_frame = ttk.Frame(self, padding=12)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview Widget setup
        columns = ("id", "date", "weight", "height", "bmi", "category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Define Column Headings
        self.tree.heading("id", text="Record ID")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("height", text="Height (m)")
        self.tree.heading("bmi", text="BMI Value")
        self.tree.heading("category", text="Category")

        # Configure Column Widths & Alignments
        self.tree.column("id", width=70, anchor=tk.CENTER)
        self.tree.column("date", width=160, anchor=tk.CENTER)
        self.tree.column("weight", width=100, anchor=tk.CENTER)
        self.tree.column("height", width=100, anchor=tk.CENTER)
        self.tree.column("bmi", width=90, anchor=tk.CENTER)
        self.tree.column("category", width=130, anchor=tk.CENTER)

        # Add Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Action Buttons Frame
        btn_frame = tk.Frame(self, bg="#F1F5F9", pady=10, padx=12)
        btn_frame.pack(fill=tk.X)

        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=("Segoe UI", 9, "bold"),
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.load_data
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(refresh_btn, "Reload history data from database")

        delete_btn = tk.Button(
            btn_frame,
            text="🗑️ Delete Selected",
            font=("Segoe UI", 9, "bold"),
            bg="#EF4444",
            fg="white",
            activebackground="#DC2626",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.delete_selected
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(delete_btn, "Delete the highlighted record entry")

        clear_btn = tk.Button(
            btn_frame,
            text="⚠️ Clear All User Data",
            font=("Segoe UI", 9, "bold"),
            bg="#F59E0B",
            fg="white",
            activebackground="#D97706",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.clear_user_data
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(clear_btn, "Delete all saved records for this user")

        close_btn = tk.Button(
            btn_frame,
            text="❌ Close",
            font=("Segoe UI", 9, "bold"),
            bg="#64748B",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5)

    def load_data(self) -> None:
        """Clears existing Treeview items and loads fresh user history from database."""
        # Clear treeview items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            records = get_user_history(self.username, db_path=self.db_path)
            for r in records:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        r["id"],
                        r["date"],
                        f"{r['weight']:.1f}",
                        f"{r['height']:.2f}",
                        f"{r['bmi']:.2f}",
                        r["category"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {str(e)}", parent=self)

    def delete_selected(self) -> None:
        """Deletes the currently selected record row from database and treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select Record", "Please select a record row to delete.", parent=self)
            return

        values = self.tree.item(selected_item, "values")
        record_id = int(values[0])

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Record ID #{record_id}?",
            parent=self
        )
        if confirm:
            try:
                delete_record(record_id, db_path=self.db_path)
                self.tree.delete(selected_item)
                messagebox.showinfo("Success", "Record deleted successfully.", parent=self)
                self.parent.refresh_user_dropdown()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}", parent=self)

    def clear_user_data(self) -> None:
        """Clears all records belonging to the active user."""
        confirm = messagebox.askyesno(
            "Confirm Clear All",
            f"Are you sure you want to PERMANENTLY delete all records for '{self.username}'?",
            parent=self
        )
        if confirm:
            try:
                count = clear_user_history(self.username, db_path=self.db_path)
                self.load_data()
                messagebox.showinfo("Success", f"Deleted {count} record(s) for user '{self.username}'.", parent=self)
                self.parent.refresh_user_dropdown()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear user records: {str(e)}", parent=self)


class BMICalculatorApp(tk.Tk):
    """
    Main Application Window for BMI Calculator & Health Tracker.
    """
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        super().__init__()
        self.db_path = db_path

        # Ensure database is initialized
        init_db(self.db_path)

        # Window Configurations
        self.title("BMI Calculator & Health Tracker")
        self.geometry("680x700")
        self.minsize(580, 620)
        self.configure(bg="#F8FAFC")

        # Custom Styling setup
        self._setup_styles()

        # Build Main User Interface
        self._build_header()
        self._build_input_form()
        self._build_action_buttons()
        self._build_result_card()
        self._build_status_bar()

        # Keyboard Shortcut Bindings
        self.bind("<Return>", lambda event: self.action_calculate())

        # Start Clock Updates
        self._update_clock()

        # Load initial user list
        self.refresh_user_dropdown()

        # Active calculation cache
        self.last_calculated_data = None

    def _setup_styles(self) -> None:
        """Sets up ttk widget styling."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Combobox style
        self.style.configure("TCombobox", padding=5, font=("Segoe UI", 10))
        self.style.configure("TFrame", background="#F8FAFC")

    def _build_header(self) -> None:
        """Creates the app header banner and live clock label."""
        header_frame = tk.Frame(self, bg="#0F172A", pady=15, padx=20)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="⚖️ BMI Calculator & Health Tracker",
            font=("Segoe UI", 16, "bold"),
            bg="#0F172A",
            fg="#F8FAFC"
        )
        title_label.pack(side=tk.LEFT)

        # Live Clock Label
        self.clock_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 9, "normal"),
            bg="#0F172A",
            fg="#94A3B8"
        )
        self.clock_label.pack(side=tk.RIGHT)

    def _update_clock(self) -> None:
        """Updates the current date and time label every 1000ms (1 second)."""
        now_str = datetime.datetime.now().strftime("%a, %b %d, %Y  %I:%M:%S %p")
        self.clock_label.config(text=now_str)
        self.after(1000, self._update_clock)

    def _build_input_form(self) -> None:
        """Constructs the user entry fields inside a card frame."""
        form_card = tk.LabelFrame(
            self,
            text=" User Information ",
            font=("Segoe UI", 11, "bold"),
            bg="#FFFFFF",
            fg="#1E293B",
            bd=1,
            relief=tk.SOLID,
            padx=20,
            pady=15
        )
        form_card.pack(fill=tk.X, padx=20, pady=15)

        # Grid configuration for form
        form_card.columnconfigure(1, weight=1)

        # 1. User Name Entry with Combobox
        lbl_user = tk.Label(form_card, text="User Name:", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        lbl_user.grid(row=0, column=0, sticky="w", pady=8)

        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(form_card, textvariable=self.user_var, font=("Segoe UI", 10))
        self.user_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=8)
        ToolTip(self.user_combo, "Enter a new username or select an existing user profile")

        # 2. Weight Entry
        lbl_weight = tk.Label(form_card, text="Weight (kg):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        lbl_weight.grid(row=1, column=0, sticky="w", pady=8)

        self.weight_var = tk.StringVar()
        self.weight_entry = tk.Entry(
            form_card,
            textvariable=self.weight_var,
            font=("Segoe UI", 10),
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightcolor="#3B82F6"
        )
        self.weight_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=8)
        ToolTip(self.weight_entry, "Enter your current body weight in kilograms (e.g. 70.5)")

        # 3. Height Entry
        lbl_height = tk.Label(form_card, text="Height (m):", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#334155")
        lbl_height.grid(row=2, column=0, sticky="w", pady=8)

        self.height_var = tk.StringVar()
        self.height_entry = tk.Entry(
            form_card,
            textvariable=self.height_var,
            font=("Segoe UI", 10),
            bd=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightcolor="#3B82F6"
        )
        self.height_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=8)
        ToolTip(self.height_entry, "Enter your height in meters (e.g. 1.75 for 175 cm)")

    def _build_action_buttons(self) -> None:
        """Creates action buttons for application tasks."""
        btn_container = tk.Frame(self, bg="#F8FAFC")
        btn_container.pack(fill=tk.X, padx=20, pady=5)

        # Top row buttons
        row1 = tk.Frame(btn_container, bg="#F8FAFC")
        row1.pack(fill=tk.X, pady=4)
        row1.columnconfigure((0, 1, 2), weight=1)

        btn_calc = tk.Button(
            row1,
            text="🧮 Calculate BMI",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_calculate
        )
        btn_calc.grid(row=0, column=0, sticky="ew", padx=4)
        ToolTip(btn_calc, "Calculate BMI and category (Shortcut: Press Enter)")

        btn_save = tk.Button(
            row1,
            text="💾 Save Record",
            font=("Segoe UI", 10, "bold"),
            bg="#16A34A",
            fg="white",
            activebackground="#15803D",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_save
        )
        btn_save.grid(row=0, column=1, sticky="ew", padx=4)
        ToolTip(btn_save, "Save the calculated BMI entry into SQLite database")

        btn_history = tk.Button(
            row1,
            text="📜 View History",
            font=("Segoe UI", 10, "bold"),
            bg="#0284C7",
            fg="white",
            activebackground="#0369A1",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_view_history
        )
        btn_history.grid(row=0, column=2, sticky="ew", padx=4)
        ToolTip(btn_history, "Open secondary window to view history table for selected user")

        # Bottom row buttons
        row2 = tk.Frame(btn_container, bg="#F8FAFC")
        row2.pack(fill=tk.X, pady=4)
        row2.columnconfigure((0, 1, 2), weight=1)

        btn_graph = tk.Button(
            row2,
            text="📈 Show BMI Graph",
            font=("Segoe UI", 10, "bold"),
            bg="#9333EA",
            fg="white",
            activebackground="#7E22CE",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_show_graph
        )
        btn_graph.grid(row=0, column=0, sticky="ew", padx=4)
        ToolTip(btn_graph, "Display visual progress trend line graph using matplotlib")

        btn_clear = tk.Button(
            row2,
            text="🧹 Clear Fields",
            font=("Segoe UI", 10, "bold"),
            bg="#64748B",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_clear
        )
        btn_clear.grid(row=0, column=1, sticky="ew", padx=4)
        ToolTip(btn_clear, "Reset input fields and clear calculated results")

        btn_exit = tk.Button(
            row2,
            text="🚪 Exit App",
            font=("Segoe UI", 10, "bold"),
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief=tk.FLAT,
            pady=8,
            command=self.action_exit
        )
        btn_exit.grid(row=0, column=2, sticky="ew", padx=4)
        ToolTip(btn_exit, "Safely close the application")

    def _build_result_card(self) -> None:
        """Constructs the dynamic BMI result and health message card."""
        self.result_card = tk.Frame(
            self,
            bg="#FFFFFF",
            bd=1,
            relief=tk.SOLID,
            padx=20,
            pady=15
        )
        self.result_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Header tag label inside card
        card_header = tk.Label(
            self.result_card,
            text="CALCULATION RESULT",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#64748B"
        )
        card_header.pack(anchor="w")

        # Main numeric BMI display
        self.bmi_value_lbl = tk.Label(
            self.result_card,
            text="--.--",
            font=("Segoe UI", 32, "bold"),
            bg="#FFFFFF",
            fg="#94A3B8"
        )
        self.bmi_value_lbl.pack(pady=(5, 0))

        # Category Badge Banner
        self.category_badge = tk.Label(
            self.result_card,
            text="Enter details and click 'Calculate BMI'",
            font=("Segoe UI", 11, "bold"),
            bg="#F1F5F9",
            fg="#475569",
            padx=14,
            pady=4
        )
        self.category_badge.pack(pady=8)

        # Health Message Label
        self.message_lbl = tk.Label(
            self.result_card,
            text="Health recommendations will appear here after calculation.",
            font=("Segoe UI", 9, "italic"),
            bg="#FFFFFF",
            fg="#64748B",
            wraplength=520,
            justify=tk.CENTER
        )
        self.message_lbl.pack(pady=(5, 10))

    def _build_status_bar(self) -> None:
        """Bottom status bar indicating app readiness."""
        self.status_bar = tk.Label(
            self,
            text=" Ready",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            fg="#475569",
            anchor="w",
            padx=10,
            pady=4
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def refresh_user_dropdown(self) -> None:
        """Fetches distinct usernames from SQLite database and populates Combobox."""
        try:
            users = get_all_users(self.db_path)
            self.user_combo['values'] = users
        except Exception as e:
            print(f"[Error] Could not update user list: {e}")

    # -------------------------------------------------------------------------
    # ACTION HANDLERS
    # -------------------------------------------------------------------------

    def action_calculate(self) -> Optional[dict]:
        """Handles BMI calculation logic and updates UI result card."""
        is_valid, error_msg, username, weight, height = validate_inputs(
            self.user_var.get(),
            self.weight_var.get(),
            self.height_var.get()
        )

        if not is_valid:
            messagebox.showerror("Input Error", error_msg)
            self.status_bar.config(text=f" Error: {error_msg}")
            return None

        # Calculate BMI
        bmi_val = calculate_bmi(weight, height)
        category_info = get_bmi_category(bmi_val)

        # Update Result Card Display
        self.bmi_value_lbl.config(text=f"{bmi_val:.2f}", fg=category_info["color"])
        self.category_badge.config(
            text=f"Category: {category_info['category'].upper()}",
            bg=category_info["color"],
            fg="#FFFFFF"
        )
        self.message_lbl.config(text=category_info["message"], fg="#1E293B")

        # Cache calculation result
        self.last_calculated_data = {
            "username": username,
            "weight": weight,
            "height": height,
            "bmi": bmi_val,
            "category": category_info["category"]
        }

        self.status_bar.config(text=f" Successfully calculated BMI for '{username}' ({bmi_val:.2f} - {category_info['category']})")
        return self.last_calculated_data

    def action_save(self) -> None:
        """Saves current BMI calculation to SQLite database."""
        # Calculate if not already done or inputs changed
        data = self.action_calculate()
        if not data:
            return

        try:
            row_id = save_record(
                username=data["username"],
                weight=data["weight"],
                height=data["height"],
                bmi=data["bmi"],
                category=data["category"],
                db_path=self.db_path
            )
            messagebox.showinfo(
                "Record Saved",
                f"Successfully saved record ID #{row_id} for user '{data['username']}'!\n\n"
                f"BMI: {data['bmi']:.2f} ({data['category']})"
            )
            self.status_bar.config(text=f" Saved record ID #{row_id} for user '{data['username']}'")
            self.refresh_user_dropdown()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save record: {str(e)}")
            self.status_bar.config(text=" Error: Failed to save record to database")

    def action_view_history(self) -> None:
        """Opens secondary history Treeview window for selected user."""
        username = self.user_var.get().strip()
        if not username:
            messagebox.showwarning("User Required", "Please enter or select a user name first.")
            return

        HistoryWindow(self, username, db_path=self.db_path)
        self.status_bar.config(text=f" Opened history view for user '{username}'")

    def action_show_graph(self) -> None:
        """Launches matplotlib trend graph for selected user."""
        username = self.user_var.get().strip()
        if not username:
            messagebox.showwarning("User Required", "Please enter or select a user name to view graph.")
            return

        self.status_bar.config(text=f" Plotting BMI trend graph for user '{username}'...")
        plot_bmi_trend(username, db_path=self.db_path)
        self.status_bar.config(text=" Ready")

    def action_clear(self) -> None:
        """Resets all input entry fields and restores result card state."""
        self.user_var.set("")
        self.weight_var.set("")
        self.height_var.set("")

        self.bmi_value_lbl.config(text="--.--", fg="#94A3B8")
        self.category_badge.config(
            text="Enter details and click 'Calculate BMI'",
            bg="#F1F5F9",
            fg="#475569"
        )
        self.message_lbl.config(
            text="Health recommendations will appear here after calculation.",
            fg="#64748B"
        )
        self.last_calculated_data = None
        self.status_bar.config(text=" Fields cleared")

    def action_exit(self) -> None:
        """Prompts user confirmation and closes application."""
        confirm = messagebox.askyesno("Exit Application", "Are you sure you want to exit?")
        if confirm:
            self.destroy()


def main():
    """Application entry point."""
    app = BMICalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
