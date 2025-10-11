# src/ui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyperclip
from src.ui.entry_dialog import EntryDialog
from src.models.credential_entry import CredentialEntry
from src.ui.toast import show_info, show_success, show_error

class MainWindow(tk.Toplevel):
    def __init__(self, parent, category_manager, **callbacks):
        super().__init__(parent)
        self.parent = parent
        self.category_manager = category_manager
        self.callbacks = callbacks

        self.title("PyVault - Main")
        self.geometry("1024x600")

        self.all_data_models = []
        self.current_filter = {"search": "", "category_id": None}

        self._setup_widgets()
        self.populate_categories()

    def _setup_widgets(self):
        # Main layout with a PanedWindow
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane for categories
        sidebar_frame = self._create_sidebar(paned_window)
        paned_window.add(sidebar_frame, weight=1)

        # Right pane for entries
        main_content_frame = self._create_main_content(paned_window)
        paned_window.add(main_content_frame, weight=4)

    def _create_sidebar(self, parent):
        sidebar = ttk.Frame(parent, padding=5)
        
        # Category list
        ttk.Label(sidebar, text="Categories", font=("-size", 12, "-weight", "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.category_tree = ttk.Treeview(sidebar, show="tree", selectmode="browse")
        self.category_tree.pack(fill=tk.BOTH, expand=True)
        self.category_tree.bind("<<TreeviewSelect>>", self._on_category_select)

        # Category management buttons
        cat_btn_frame = ttk.Frame(sidebar)
        cat_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(cat_btn_frame, text="Add", command=self._handle_category_add, style="success.TButton").pack(side=tk.LEFT, expand=True)
        ttk.Button(cat_btn_frame, text="Edit", command=self._handle_category_edit, style="secondary.TButton").pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(cat_btn_frame, text="Delete", command=self._handle_category_delete, style="danger.TButton").pack(side=tk.LEFT, expand=True)

        return sidebar

    def _create_main_content(self, parent):
        main_frame = ttk.Frame(parent, padding=5)

        # Toolbar with search and main actions
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="Add Entry", command=self._handle_add, style='success.TButton').pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Edit Entry", command=self._handle_edit, style='secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Delete Entry", command=self._handle_delete, style='danger.TButton').pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.RIGHT, padx=(0, 5))
        search_entry.bind("<Return>", lambda e: self._handle_search())
        ttk.Label(toolbar, text="Search:").pack(side=tk.RIGHT)

        # Entries Treeview
        columns = ('service', 'username')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', selectmode='browse')
        self.tree.heading('service', text='Service')
        self.tree.heading('username', text='Username')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Password", command=self._copy_password)
        self.context_menu.add_command(label="Copy Username", command=self._copy_username)
        self.tree.bind("<Button-3>", self._show_context_menu)

        return main_frame

    # --- Data Population and Filtering ---
    def populate_all_data(self, data_models: list[CredentialEntry]):
        self.all_data_models = data_models
        self._apply_filters()

    def populate_categories(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        self.category_tree.insert("", "end", "all", text="All Entries")
        for cat_id, category in self.category_manager.categories.items():
            self.category_tree.insert("", "end", cat_id, text=category.name)
        self.category_tree.selection_set("all")

    def _apply_filters(self):
        search_term = self.current_filter["search"].lower()
        category_id = self.current_filter["category_id"]

        filtered_entries = self.all_data_models

        # Filter by category
        if category_id and category_id != "all":
            filtered_entries = [e for e in filtered_entries if e.category_id == category_id]

        # Filter by search term
        if search_term:
            filtered_entries = [
                e for e in filtered_entries
                if search_term in e.service.lower() or search_term in e.username.lower()
            ]

        # Populate the table with filtered results
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in filtered_entries:
            self.tree.insert('', tk.END, values=(entry.service, entry.username), iid=entry.entry_id)

    # --- Event Handlers ---
    def _on_category_select(self, event):
        selected_id = self.category_tree.selection()[0] if self.category_tree.selection() else "all"
        self.current_filter["category_id"] = selected_id
        self._apply_filters()

    def _handle_search(self):
        self.current_filter["search"] = self.search_var.get()
        self._apply_filters()

    def _handle_add(self):
        dialog = EntryDialog(self, self.category_manager)
        if dialog.result:
            self.callbacks.get("on_add")(dialog.result)

    def _handle_edit(self):
        entry_id = self._get_selected_entry_id()
        if not entry_id: return show_info("Please select an entry.")
        entry_model = self._get_entry_model_by_id(entry_id)
        if entry_model:
            dialog = EntryDialog(self, self.category_manager, entry=entry_model)
            if dialog.result:
                self.callbacks.get("on_edit")(dialog.result)

    def _handle_delete(self):
        entry_id = self._get_selected_entry_id()
        if not entry_id: return show_info("Please select an entry.")
        if messagebox.askyesno("Confirm Delete", "Delete this entry permanently?"):
            self.callbacks.get("on_delete")(entry_id)
    
    # --- Category Management Handlers ---
    def _handle_category_add(self):
        name = simpledialog.askstring("Add Category", "Enter new category name:", parent=self)
        if name:
            self.callbacks.get("on_category_add")(name)

    def _handle_category_edit(self):
        cat_id = self.category_tree.selection()[0] if self.category_tree.selection() else None
        if not cat_id or cat_id == "all" or cat_id == "uncategorized":
            return show_error("This category cannot be edited.")

        old_name = self.category_manager.get_category_name_by_id(cat_id)
        new_name = simpledialog.askstring("Edit Category", "Enter new name:", initialvalue=old_name, parent=self)
        if new_name and new_name != old_name:
            self.callbacks.get("on_category_edit")(cat_id, new_name)

    def _handle_category_delete(self):
        cat_id = self.category_tree.selection()[0] if self.category_tree.selection() else None
        if not cat_id or cat_id == "all" or cat_id == "uncategorized":
            return show_error("This category cannot be deleted.")

        cat_name = self.category_manager.get_category_name_by_id(cat_id)
        if messagebox.askyesno("Confirm Delete", f"Delete category '{cat_name}'? Entries will be moved to Uncategorized."):
            self.callbacks.get("on_category_delete")(cat_id)
    
    # --- Helper and Context Menu Methods ---
    def _get_selected_entry_id(self):
        return self.tree.selection()[0] if self.tree.selection() else None

    def _get_entry_model_by_id(self, entry_id):
        return next((e for e in self.all_data_models if e.entry_id == entry_id), None)

    def _copy_password(self):
        entry_id = self._get_selected_entry_id()
        if entry_id and (entry := self._get_entry_model_by_id(entry_id)):
            pyperclip.copy(entry.password)
            show_success("Password copied to clipboard!")

    def _copy_username(self):
        entry_id = self._get_selected_entry_id()
        if entry_id and (entry := self._get_entry_model_by_id(entry_id)):
            pyperclip.copy(entry.username)
            show_success("Username copied to clipboard!")

    def _show_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)
