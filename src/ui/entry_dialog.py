# src/ui/entry_dialog.py
import tkinter as tk
from tkinter import ttk
from src.models.credential_entry import CredentialEntry
from src.ui.password_generator_dialog import PasswordGeneratorDialog

class EntryDialog(tk.Toplevel):
    def __init__(self, parent, category_manager, entry: CredentialEntry = None):
        super().__init__(parent)

        self.entry = entry
        self.category_manager = category_manager
        self.result = None

        is_edit = self.entry is not None
        title = "Edit Entry" if is_edit else "Add New Entry"
        self.title(title)

        self._setup_widgets()

        if is_edit:
            self._populate_data()

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _setup_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill=tk.BOTH)

        # Fields
        fields = ["Service", "Username", "Password", "URL", "Category"]
        self.vars = {}

        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W, pady=2)

            if field == "Password":
                # Password field with a generate button
                password_frame = ttk.Frame(frame)
                self.vars[field] = tk.StringVar()
                password_entry = ttk.Entry(password_frame, textvariable=self.vars[field], show="*")
                password_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

                generate_button = ttk.Button(password_frame, text="Generate", command=self._open_generator, style="secondary.TButton", width=10)
                generate_button.pack(side=tk.RIGHT, padx=(5, 0))
                password_frame.grid(row=i, column=1, sticky=tk.EW, pady=2)
            elif field == "Category":
                categories = self.category_manager.get_category_names()
                self.vars[field] = tk.StringVar()
                if "Uncategorized" not in categories:
                    categories.insert(0, "Uncategorized")
                cat_combo = ttk.Combobox(frame, textvariable=self.vars[field], values=categories, state="readonly")
                cat_combo.grid(row=i, column=1, sticky=tk.EW, pady=2)
            else:
                self.vars[field] = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=self.vars[field])
                entry.grid(row=i, column=1, sticky=tk.EW, pady=2)

        frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(frame, padding=(0, 15, 0, 0))
        button_frame.grid(row=len(fields), column=0, columnspan=2, sticky=tk.EW)

        ttk.Button(button_frame, text="Save", command=self._on_save, style="success.TButton").pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=self.destroy, style="secondary.TButton").pack(side=tk.RIGHT, padx=10)

    def _populate_data(self):
        self.vars["Service"].set(self.entry.service)
        self.vars["Username"].set(self.entry.username)
        self.vars["Password"].set(self.entry.password)
        self.vars["URL"].set(self.entry.url)
        category_name = self.category_manager.get_category_name_by_id(self.entry.category_id)
        self.vars["Category"].set(category_name)

    def _open_generator(self):
        generator_dialog = PasswordGeneratorDialog(self)
        if generator_dialog.result:
            self.vars["Password"].set(generator_dialog.result)
            from src.ui.toast import show_success
            show_success("Password generated and filled.")

    def _on_save(self):
        category_name = self.vars["Category"].get() or "Uncategorized"
        category_id = self.category_manager.get_category_id_by_name(category_name) or "uncategorized"
            
        self.result = {
            "service": self.vars["Service"].get(),
            "username": self.vars["Username"].get(),
            "password": self.vars["Password"].get(),
            "url": self.vars["URL"].get(),
            "category_id": category_id,
            "entry_id": self.entry.entry_id if self.entry else None
        }
        self.destroy()
