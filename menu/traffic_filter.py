import tkinter as tk
from tkinter import ttk
from styles import apply_styles

class TrafficFilterMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.configure(width=900, height=800, padding=20)

        ttk.Label(self, text="TRAFFIC FILTER", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Find Pattern:", style="SubHeader.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        self.find_entry = ttk.Entry(self, width=60, style="Custom.TEntry")
        self.find_entry.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

        ttk.Label(self, text="Replace With:", style="SubHeader.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        self.replace_entry = ttk.Entry(self, width=60, style="Custom.TEntry")
        self.replace_entry.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

        ttk.Label(self, text="Scope:", style="SubHeader.TLabel").grid(row=5, column=0, sticky="w", pady=5)
        self.scope_var = tk.StringVar(value="Request")
        self.scope_menu = ttk.OptionMenu(self, self.scope_var, "Request", "Request", "Response")
        self.scope_menu.grid(row=5, column=1, pady=5, padx=10, sticky="ew")

        self.add_button = ttk.Button(self, text="➕ Add Rule", command=self.add_rule, style="Accent.TButton")
        self.add_button.grid(row=6, column=0, columnspan=2, pady=15, padx=10, sticky="ew")

        self.rules_frame = ttk.Frame(self, style="List.TFrame")
        self.rules_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.rules_list = tk.Listbox(self.rules_frame, height=12, width=60, bg="#1e1e1e", fg="#ffffff", font=("Arial", 12), relief="flat", highlightthickness=0, selectbackground="#333333")
        self.rules_scroll = ttk.Scrollbar(self.rules_frame, orient="vertical", command=self.rules_list.yview)
        self.rules_list.config(yscrollcommand=self.rules_scroll.set)

        self.rules_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.rules_scroll.pack(side="right", fill="y")

    def add_rule(self):
        find = self.find_entry.get().strip()
        replace = self.replace_entry.get().strip()
        scope = self.scope_var.get()
        if find and replace:
            rule = f"{scope}: '{find}' -> '{replace}'"
            self.rules_list.insert(tk.END, rule)
            self.find_entry.delete(0, tk.END)
            self.replace_entry.delete(0, tk.END)
            self.controller.firewall.add_traffic_rule(find, replace, scope)
 