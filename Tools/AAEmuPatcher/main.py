import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
import csv
from collections import defaultdict
from tkinter import font as tkfont
from tkinter.scrolledtext import ScrolledText


class AAEmuSQLPatchGenerator:
    def __init__(self, master):
        self.master = master
        self.master.title("AAEmu SQL Patch Generator v3.3")
        self.master.geometry("1200x800")
        self.master.minsize(1000, 700)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Initialize data storage
        self.records = defaultdict(list)
        self.current_table = ""
        self.table_columns = defaultdict(list)
        self.sql_mode = "INSERT"  # Can be "INSERT" or "UPDATE"
        self.columns_to_update = []  # Stores user-selected columns
        self.update_all_columns = True  # Default behavior

        # Fonts
        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.button_font = tkfont.Font(family="Segoe UI", size=10)
        self.sql_font = tkfont.Font(family="Consolas", size=10)

        # Create UI
        self.create_widgets()

        # Initialize UI state
        self.update_toggle_appearance()
        self.update_sql_mode()

    def configure_styles(self):
        """Configure ttk styles for the application"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6)
        self.style.configure('TCombobox', padding=5)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        self.style.map('TButton',
                       foreground=[('active', 'black'), ('!disabled', 'black')],
                       background=[('active', '#d9d9d9'), ('!disabled', '#e6e6e6')])

        # Toggle button style
        self.style.configure('Toggle.TButton',
                             padding=6,
                             background='#e6e6e6',
                             foreground='black')
        self.style.map('Toggle.TButton',
                       background=[('selected', '#4CAF50'), ('!selected', '#e6e6e6')],
                       foreground=[('selected', 'white'), ('!selected', 'black')])

    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(header_frame,
                  text="AAEmu SQL Patch Generator",
                  font=self.title_font).pack(side='left')

        # File Operations
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding=10)
        file_frame.pack(fill='x', pady=5)

        ttk.Button(file_frame,
                   text="📂 Load CSV Files",
                   command=self.load_csv,
                   width=20).pack(side='left', padx=5)
        ttk.Button(file_frame,
                   text="⚡ Generate SQL",
                   command=self.generate_sql,
                   width=20).pack(side='left', padx=5)

        # Table Configuration
        config_frame = ttk.LabelFrame(main_frame, text="Table Configuration", padding=10)
        config_frame.pack(fill='x', pady=5)

        # Table selection
        ttk.Label(config_frame, text="Selected Table:").grid(row=0, column=0, sticky='w')
        self.table_var = tk.StringVar()
        self.table_dropdown = ttk.Combobox(config_frame,
                                           textvariable=self.table_var,
                                           state='readonly',
                                           width=30)
        self.table_dropdown.grid(row=0, column=1, padx=5, sticky='ew')
        self.table_dropdown.bind('<<ComboboxSelected>>', self.update_display)

        # SQL Generation Options
        option_frame = ttk.LabelFrame(main_frame, text="SQL Generation Options", padding=10)
        option_frame.pack(fill='x', pady=5)

        # Mode Selection
        mode_frame = ttk.Frame(option_frame)
        mode_frame.pack(side='left', padx=10, fill='y')

        ttk.Label(mode_frame, text="SQL Mode:").pack(anchor='w')
        self.sql_mode_var = tk.StringVar(value="INSERT")

        # Mode radio buttons
        mode_btn_frame = ttk.Frame(mode_frame)
        mode_btn_frame.pack(fill='x')
        ttk.Radiobutton(mode_btn_frame,
                        text="INSERT - Add new records",
                        variable=self.sql_mode_var,
                        value="INSERT",
                        command=self.update_sql_mode).pack(side='left')
        ttk.Radiobutton(mode_btn_frame,
                        text="UPDATE - Modify existing records",
                        variable=self.sql_mode_var,
                        value="UPDATE",
                        command=self.update_sql_mode).pack(side='left', padx=5)

        # UPDATE-Specific Controls
        self.update_controls_frame = ttk.Frame(option_frame)

        # WHERE Condition Selection with Select Columns button
        where_frame = ttk.Frame(self.update_controls_frame)
        where_frame.pack(side='left', padx=10, fill='x', expand=True)

        # Select Columns button on the left
        self.select_columns_btn = ttk.Button(where_frame,
                                             text="✏️ Edit Select Column",
                                             command=self.select_columns,
                                             width=20)
        self.select_columns_btn.pack(side='left', padx=(0, 10))  # Right padding only

        # WHERE Condition dropdown on the right
        where_condition_frame = ttk.Frame(where_frame)
        where_condition_frame.pack(side='left', fill='x', expand=True)
        ttk.Label(where_condition_frame, text="WHERE Condition:").pack(anchor='w')
        self.where_column_var = tk.StringVar()
        self.where_column_dropdown = ttk.Combobox(where_condition_frame,
                                                  textvariable=self.where_column_var,
                                                  state='readonly',
                                                  width=25)
        self.where_column_dropdown.pack(fill='x', expand=True)
        ttk.Label(where_condition_frame,
                  text="(Column for WHERE clause in UPDATE statements)",
                  foreground="#666",
                  font=('Segoe UI', 8)).pack()

        # Generate All Tables
        gen_all_frame = ttk.Frame(option_frame)
        gen_all_frame.pack(side='right', padx=10)
        self.generate_all_var = tk.BooleanVar(value=False)
        self.generate_all_toggle = ttk.Checkbutton(gen_all_frame,
                                                   text="Generate All Tables",
                                                   variable=self.generate_all_var,
                                                   style='Toggle.TButton',
                                                   command=self.update_toggle_appearance)
        self.generate_all_toggle.pack()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame,
                                    textvariable=self.status_var,
                                    relief='sunken',
                                    anchor='w',
                                    padding=5)
        self.status_bar.pack(fill='x', pady=(10, 0))

        # SQL Preview
        preview_frame = ttk.LabelFrame(main_frame, text="SQL Preview", padding=5)
        preview_frame.pack(fill='both', expand=True)
        self.sql_preview = ScrolledText(preview_frame,
                                        font=self.sql_font,
                                        wrap='none',
                                        padx=10,
                                        pady=10)
        self.sql_preview.pack(fill='both', expand=True)

        # Context Menu
        self.setup_context_menu()

    def setup_context_menu(self):
        """Set up right-click context menu for SQL preview"""
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Copy SQL", command=self.copy_sql)
        self.sql_preview.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Display context menu on right-click"""
        self.context_menu.post(event.x_root, event.y_root)

    def copy_sql(self):
        """Copy SQL preview to clipboard"""
        sql_text = self.sql_preview.get("1.0", tk.END)
        if sql_text.strip():
            self.master.clipboard_clear()
            self.master.clipboard_append(sql_text)
            self.status_var.set("SQL copied to clipboard")

    def update_sql_mode(self):
        """Handle SQL mode changes and toggle UI elements"""
        self.sql_mode = self.sql_mode_var.get()

        # Show/hide UPDATE-specific controls
        if self.sql_mode == "UPDATE":
            self.update_controls_frame.pack(side='left', padx=10, fill='x', expand=True)
        else:
            self.update_controls_frame.pack_forget()

        self.status_var.set(f"SQL generation mode set to {self.sql_mode}")
        self.update_display()

    def update_toggle_appearance(self):
        """Update the appearance of the toggle button"""
        if self.generate_all_var.get():
            self.style.map('Toggle.TButton',
                           background=[('selected', '#4CAF50')],
                           foreground=[('selected', 'white')])
        else:
            self.style.map('Toggle.TButton',
                           background=[('!selected', '#e6e6e6')],
                           foreground=[('!selected', 'black')])
        self.generate_all_toggle.update()

    def select_columns(self):
        """Open column selection dialog"""
        if not self.current_table:
            messagebox.showwarning("Warning", "No table selected!")
            return

        # Create popup window
        popup = tk.Toplevel()
        popup.title(f"Select Columns for {self.current_table}")

        # Listbox with multiselect
        columns = self.table_columns[self.current_table]
        lb = tk.Listbox(popup, selectmode=tk.MULTIPLE, height=15)
        for col in columns:
            lb.insert(tk.END, col)
        lb.pack(padx=10, pady=10)

        # Preselect currently selected columns
        for i, col in enumerate(columns):
            if col in self.columns_to_update:
                lb.selection_set(i)

        # Confirm button
        def apply_selection():
            self.columns_to_update = [lb.get(i) for i in lb.curselection()]
            self.update_all_columns = not bool(self.columns_to_update)
            popup.destroy()
            self.update_display()

        ttk.Button(popup, text="Apply", command=apply_selection).pack(pady=5)

    def load_csv(self):
        """Load CSV files into the application"""
        file_paths = filedialog.askopenfilenames(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select CSV Files"
        )
        if not file_paths:
            return

        try:
            # Don't clear existing data - append to it
            for file_path in file_paths:
                with open(file_path, newline='', encoding='utf-8') as f:
                    # Detect delimiter
                    sample = f.read(1024)
                    f.seek(0)

                    # Check for common delimiters
                    if '\t' in sample:
                        delimiter = '\t'
                    elif ';' in sample and ',' not in sample[:100]:  # Handle European CSVs
                        delimiter = ';'
                    else:
                        delimiter = ','

                    reader = csv.DictReader(f, delimiter=delimiter)

                    # Get clean table name from filename
                    table_name = os.path.splitext(os.path.basename(file_path))[0]

                    # Validate CSV structure
                    if not reader.fieldnames:
                        raise ValueError("CSV has no headers!")
                    if len(reader.fieldnames) != len(set(reader.fieldnames)):
                        raise ValueError("Duplicate column names found!")

                    # Initialize table if it doesn't exist
                    if table_name not in self.table_columns:
                        self.table_columns[table_name] = reader.fieldnames

                    # Read and process all rows
                    for row in reader:
                        if not row:  # Skip empty rows
                            continue

                        processed_row = {
                            key: self.clean_csv_value(value)
                            for key, value in row.items()
                        }
                        self.records[table_name].append(processed_row)

            # Update UI after loading
            self.update_ui_after_loading()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
            self.status_var.set(f"Error loading file: {str(e)}")

    def clean_csv_value(self, value):
        """Clean and standardize CSV values"""
        value = value.strip() if value else ''
        return 'NULL' if value == '' else value

    def update_ui_after_loading(self):
        """Update UI elements after CSV loading"""
        self.table_dropdown['values'] = list(self.records.keys())

        if not self.table_var.get() and self.records:
            self.table_var.set(next(iter(self.records)))

        record_count = sum(len(v) for v in self.records.values())
        table_count = len(self.records)
        self.status_var.set(f"Loaded {record_count} records from {table_count} tables")

        # Refresh the SQL preview
        self.update_display()

    def update_where_dropdown(self):
        """Update WHERE condition dropdown based on current table"""
        if self.current_table in self.table_columns:
            where_options = ["All Rows"] + self.table_columns[self.current_table]
            self.where_column_dropdown['values'] = where_options

            # Keep current selection if it's still valid
            current_where = self.where_column_var.get()
            if current_where in where_options:
                self.where_column_var.set(current_where)
            else:
                # Set default based on common patterns
                for preferred in ['id', 'ID', 'Id', 'skill_id', 'item_id']:
                    if preferred in where_options:
                        self.where_column_var.set(preferred)
                        break
                else:
                    # Fallback to first column if no standard PK found
                    if len(where_options) > 1:  # Skip "All Rows"
                        self.where_column_var.set(where_options[1])

    def update_display(self, event=None):
        """Update the SQL preview display"""
        self.current_table = self.table_var.get()
        if not self.current_table or self.current_table not in self.records:
            self.sql_preview.delete('1.0', tk.END)
            return

        self.update_where_dropdown()

        # Clear previous preview
        self.sql_preview.delete('1.0', tk.END)

        # Generate SQL preview
        sql_text = self._generate_sql_text(self.current_table)
        self.sql_preview.insert(tk.END, sql_text)

        # Highlight SQL syntax
        self.highlight_sql()

        # Update status
        where_col = self.where_column_var.get()
        where_status = f"WHERE: {where_col}" if where_col else "Updating ALL rows"
        self.status_var.set(
            f"Previewing: {self.current_table} | {len(self.records[self.current_table])} records | {where_status}")

    def highlight_sql(self):
        """Basic SQL syntax highlighting"""
        self.sql_preview.tag_configure('keyword', foreground='blue', font=self.sql_font)
        self.sql_preview.tag_configure('string', foreground='green', font=self.sql_font)
        self.sql_preview.tag_configure('comment', foreground='gray', font=self.sql_font)
        self.sql_preview.tag_configure('table', foreground='purple', font=self.sql_font)

        # Highlight keywords
        keywords = ['INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'WHERE', 'NULL']
        for word in keywords:
            start = '1.0'
            while True:
                start = self.sql_preview.search(word, start, stopindex=tk.END, nocase=1)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.sql_preview.tag_add('keyword', start, end)
                start = end

        # Highlight strings (text between single quotes)
        start = '1.0'
        while True:
            start = self.sql_preview.search("'", start, stopindex=tk.END)
            if not start:
                break
            end = self.sql_preview.search("'", f"{start}+1c", stopindex=tk.END)
            if not end:
                break
            self.sql_preview.tag_add('string', start, f"{end}+1c")
            start = f"{end}+1c"

        # Highlight comments
        start = '1.0'
        while True:
            start = self.sql_preview.search("--", start, stopindex=tk.END)
            if not start:
                break
            end = self.sql_preview.search("\n", start, stopindex=tk.END)
            if not end:
                end = tk.END
            self.sql_preview.tag_add('comment', start, end)
            start = end

        # Highlight table names
        if self.current_table:
            start = '1.0'
            while True:
                start = self.sql_preview.search(self.current_table, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(self.current_table)}c"
                self.sql_preview.tag_add('table', start, end)
                start = end

    def _generate_sql_text(self, table_name):
        """Generate SQL text for preview with enhanced WHERE condition handling"""
        if not table_name or table_name not in self.records:
            return ""

        sql_lines = []
        columns = self.table_columns.get(table_name, [])
        columns_to_update = self.columns_to_update if self.columns_to_update else columns

        # Get the WHERE condition column
        where_column = self.where_column_var.get()

        # Header information
        sql_lines.append(f"-- SQL {self.sql_mode} statements for {table_name}\n")
        if self.sql_mode == "UPDATE":
            sql_lines.append(f"-- WHERE Condition: {where_column if where_column else 'All Rows'}\n")
        sql_lines.append(f"-- Columns to update: {', '.join(columns_to_update) if columns_to_update else 'ALL'}\n")
        sql_lines.append(f"-- Record count: {len(self.records[table_name])}\n\n")

        if self.sql_mode == "INSERT":
            # INSERT mode generation
            for record in self.records[table_name][:10]:  # Preview first 10
                values = []
                for col in columns:
                    value = record.get(col, '')
                    if value == 'NULL':
                        values.append('NULL')
                    elif value == '':
                        values.append('NULL')
                    elif value.replace('.', '', 1).isdigit():
                        values.append(value)
                    else:
                        values.append(f"'{str(value).replace("'", "''")}'")

                sql_lines.append(
                    f"INSERT INTO {table_name} ({', '.join(columns)})\n"
                    f"VALUES ({', '.join(values)});\n\n"
                )

            if len(self.records[table_name]) > 10:
                sql_lines.append(f"-- ... plus {len(self.records[table_name]) - 10} more records\n\n")

        else:  # UPDATE mode
            if not where_column or where_column == "All Rows":
                # Mass update warning
                sql_lines.append("-- WARNING: This will update ALL rows in the table!\n")
                sample_record = next(iter(self.records[table_name]), {})
                set_clauses = []

                for col in columns_to_update:
                    value = sample_record.get(col, '')
                    set_clauses.append(self._build_set_clause(col, value))

                if set_clauses:
                    sql_lines.append(
                        f"UPDATE {table_name}\n"
                        f"SET {', '.join(set_clauses)};\n\n"
                    )
            else:
                # Targeted updates with WHERE clause
                for record in self.records[table_name][:10]:  # Preview first 10
                    set_clauses = []
                    where_value = record.get(where_column, '')

                    # Build WHERE clause
                    where_clause = self._build_where_clause(where_column, where_value)

                    # Build SET clauses - use columns_to_update but exclude the WHERE column
                    for col in columns_to_update:
                        if col == where_column:  # Skip WHERE column in SET
                            continue
                        value = record.get(col, '')
                        set_clauses.append(self._build_set_clause(col, value))

                    if set_clauses:
                        sql_lines.append(
                            f"UPDATE {table_name}\n"
                            f"SET {', '.join(set_clauses)}\n"
                            f"WHERE {where_clause};\n\n"
                        )

                if len(self.records[table_name]) > 10:
                    sql_lines.append(f"-- ... plus {len(self.records[table_name]) - 10} more records\n\n")

        return ''.join(sql_lines)

    def _build_set_clause(self, column, value):
        """Helper to build SET clause components"""
        if value == 'NULL' or value == '':
            return f"{column} = NULL"
        elif value.replace('.', '', 1).isdigit():
            return f"{column} = {value}"
        else:
            return f"{column} = '{str(value).replace("'", "''")}'"

    def _build_where_clause(self, column, value):
        """Helper to build WHERE clause components"""
        if value == 'NULL' or value == '':
            return f"{column} IS NULL"
        elif value.replace('.', '', 1).isdigit():
            return f"{column} = {value}"
        else:
            return f"{column} = '{str(value).replace("'", "''")}'"

    def generate_sql(self):
        """Main SQL generation function"""
        if not self.records or not self.current_table:
            messagebox.showerror("Error", "No table selected or no data loaded!")
            return

        if self.generate_all_var.get():
            self._generate_all_tables()
        else:
            self._generate_single_table()

    def _generate_single_table(self):
        """Generate SQL for the currently selected table"""
        if not self.current_table or self.current_table not in self.records:
            messagebox.showerror("Error", "No table selected or no data loaded!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
            initialfile=f"patch_{self.current_table}.sql",
            title="Save SQL File As"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                columns = self.table_columns.get(self.current_table, [])
                columns_to_update = self.columns_to_update if self.columns_to_update else columns
                where_column = self.where_column_var.get()

                # Write header information
                f.write(f"-- SQL Patch for {self.current_table}\n")
                f.write(f"-- Generated by AAEmu SQL Patch Generator ({self.sql_mode} mode)\n")
                if self.sql_mode == "UPDATE":
                    f.write(f"-- WHERE Condition: {where_column}\n")
                f.write(f"-- Columns updated: {', '.join(columns_to_update) if columns_to_update else 'ALL'}\n\n")

                if self.sql_mode == "INSERT":
                    for record in self.records[self.current_table]:
                        values = []
                        for col in columns:
                            value = record.get(col, '')
                            if value == 'NULL' or value == '':
                                values.append('NULL')
                            elif value.replace('.', '', 1).isdigit():
                                values.append(value)
                            else:
                                safe_value = str(value).replace("'", "''")
                                values.append(f"'{safe_value}'")

                        f.write(
                            f"INSERT INTO {self.current_table} ({', '.join(columns)})\n"
                            f"VALUES ({', '.join(values)});\n\n"
                        )
                else:  # UPDATE mode
                    if not where_column or where_column == "All Rows":
                        # Generate one update for all rows
                        set_clauses = []
                        sample_record = self.records[self.current_table][0] if self.records[self.current_table] else {}

                        for col in columns_to_update:
                            value = sample_record.get(col, '')
                            if value == 'NULL' or value == '':
                                set_clauses.append(f"{col} = NULL")
                            elif value.replace('.', '', 1).isdigit():
                                set_clauses.append(f"{col} = {value}")
                            else:
                                safe_value = str(value).replace("'", "''")
                                set_clauses.append(f"{col} = '{safe_value}'")

                        if set_clauses:
                            f.write(
                                f"UPDATE {self.current_table}\n"
                                f"SET {', '.join(set_clauses)};\n\n"
                            )
                    else:
                        # Generate individual updates with WHERE clauses
                        for record in self.records[self.current_table]:
                            set_clauses = []
                            where_value = record.get(where_column, '')

                            if where_value == 'NULL' or where_value == '':
                                where_clause = f"{where_column} IS NULL"
                            elif where_value.replace('.', '', 1).isdigit():
                                where_clause = f"{where_column} = {where_value}"
                            else:
                                safe_value = str(where_value).replace("'", "''")
                                where_clause = f"{where_column} = '{safe_value}'"

                            for col in columns_to_update:
                                if col == where_column:  # Skip WHERE column in SET
                                    continue
                                value = record.get(col, '')
                                if value == 'NULL' or value == '':
                                    set_clauses.append(f"{col} = NULL")
                                elif value.replace('.', '', 1).isdigit():
                                    set_clauses.append(f"{col} = {value}")
                                else:
                                    safe_value = str(value).replace("'", "''")
                                    set_clauses.append(f"{col} = '{safe_value}'")

                            if set_clauses:
                                f.write(
                                    f"UPDATE {self.current_table}\n"
                                    f"SET {', '.join(set_clauses)}\n"
                                    f"WHERE {where_clause};\n\n"
                                )

            self.status_var.set(f"SQL saved to: {file_path}")
            messagebox.showinfo("Success", f"SQL {self.sql_mode} statements saved to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SQL:\n{str(e)}")
            self.status_var.set("Error generating SQL")

    def _generate_all_tables(self):
        """Generate SQL for all loaded tables in one file"""
        if not self.records:
            messagebox.showerror("Error", "No data loaded to generate SQL!")
            return

        where_column = self.where_column_var.get()
        if self.sql_mode == "UPDATE" and (not where_column or where_column == "All Rows"):
            if not messagebox.askyesno("Warning",
                                       "You are about to generate UPDATE statements that will modify ALL ROWS in ALL TABLES.\n"
                                       "This cannot be undone. Are you sure you want to continue?"):
                return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")],
            initialfile=f"patch_all_{datetime.now().strftime('%Y%m%d_%H%M')}.sql",
            title="Save Combined SQL File As"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"-- Combined SQL Patch for {len(self.records)} tables\n")
                f.write(f"-- Generated by AAEmu SQL Patch Generator ({self.sql_mode} mode)\n")
                f.write(f"-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for table_name, records in self.records.items():
                    if not records:  # Skip empty tables
                        continue

                    f.write(f"-- TABLE: {table_name}\n")
                    columns = self.table_columns.get(table_name, [])
                    if not columns:
                        f.write(f"-- WARNING: No columns found for table {table_name}\n\n")
                        continue

                    # Use selected columns or all columns if none selected
                    columns_to_update = self.columns_to_update if self.columns_to_update else columns

                    if self.sql_mode == "INSERT":
                        for record in records:
                            values = []
                            for col in columns:
                                value = record.get(col, '')
                                if value == 'NULL' or value == '':
                                    values.append('NULL')
                                elif value.replace('.', '', 1).isdigit():
                                    values.append(value)
                                else:
                                    safe_value = str(value).replace("'", "''")
                                    values.append(f"'{safe_value}'")

                            f.write(
                                f"INSERT INTO {table_name} ({', '.join(columns)})\n"
                                f"VALUES ({', '.join(values)});\n\n"
                            )
                    else:  # UPDATE mode
                        if not where_column or where_column == "All Rows":
                            # Generate one update for all rows
                            set_clauses = []
                            sample_record = records[0] if records else {}

                            for col in columns_to_update:
                                value = sample_record.get(col, '')
                                if value == 'NULL' or value == '':
                                    set_clauses.append(f"{col} = NULL")
                                elif value.replace('.', '', 1).isdigit():
                                    set_clauses.append(f"{col} = {value}")
                                else:
                                    safe_value = str(value).replace("'", "''")
                                    set_clauses.append(f"{col} = '{safe_value}'")

                            if set_clauses:
                                f.write(
                                    f"UPDATE {table_name}\n"
                                    f"SET {', '.join(set_clauses)};\n\n"
                                )
                        else:
                            # Generate individual updates with WHERE clauses
                            for record in records:
                                set_clauses = []
                                where_value = record.get(where_column, '')

                                if where_value == 'NULL' or where_value == '':
                                    where_clause = f"{where_column} IS NULL"
                                elif where_value.replace('.', '', 1).isdigit():
                                    where_clause = f"{where_column} = {where_value}"
                                else:
                                    safe_value = str(where_value).replace("'", "''")
                                    where_clause = f"{where_column} = '{safe_value}'"

                                for col in columns_to_update:
                                    if col == where_column:  # Skip WHERE column in SET clause
                                        continue
                                    value = record.get(col, '')
                                    if value == 'NULL' or value == '':
                                        set_clauses.append(f"{col} = NULL")
                                    elif value.replace('.', '', 1).isdigit():
                                        set_clauses.append(f"{col} = {value}")
                                    else:
                                        safe_value = str(value).replace("'", "''")
                                        set_clauses.append(f"{col} = '{safe_value}'")

                                if set_clauses:
                                    f.write(
                                        f"UPDATE {table_name}\n"
                                        f"SET {', '.join(set_clauses)}\n"
                                        f"WHERE {where_clause};\n\n"
                                    )

            self.status_var.set(f"Combined SQL saved to: {file_path}")
            messagebox.showinfo("Success", f"SQL {self.sql_mode} statements for all tables saved to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SQL:\n{str(e)}")
            self.status_var.set("Error generating SQL")


if __name__ == "__main__":
    root = tk.Tk()
    app = AAEmuSQLPatchGenerator(root)
    root.mainloop()