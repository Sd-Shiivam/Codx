import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from styles import apply_styles

class ContentBlockMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.configure(width=900, height=800)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="🛑 CONTENT BLOCK", style="Header.TLabel").grid(row=0, column=0, pady=25, padx=30)

        rules_frame = ttk.Frame(self, style="Content.TFrame")
        rules_frame.grid(row=1, column=0, pady=15, padx=30, sticky="nsew")
        rules_frame.grid_columnconfigure(0, weight=1)

        self.rules = {
            "Block JS Files": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block Image Files": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block CSS Files": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block Malware Domains": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block Specific URL": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block Specific Text": {"enabled": tk.BooleanVar(value=False), "list": []},
            "Block Ads": {"enabled": tk.BooleanVar(value=False), "list": []},
        }

        self.rule_widgets = {}
        row = 0
        for rule_name, data in self.rules.items():
            toggle = ttk.Checkbutton(rules_frame, text=rule_name, variable=data["enabled"], style="Toggle.TCheckbutton", command=lambda r=rule_name: self.toggle_rule(r))
            toggle.grid(row=row, column=0, pady=8, padx=10, sticky="w")

            listbox = tk.Listbox(rules_frame, height=3, width=50, bg="#000000", fg="#ffffff")
            listbox.grid(row=row, column=1, pady=8, padx=10, sticky="ew")
            for item in data["list"]:
                listbox.insert(tk.END, item)
            
            btn_frame = ttk.Frame(rules_frame)
            btn_frame.grid(row=row, column=2, pady=8, padx=5, sticky="w")
            ttk.Button(btn_frame, text="➕ Add", command=lambda r=rule_name, l=listbox: self.add_to_list(r, l)).grid(row=0, column=0, padx=5)
            ttk.Button(btn_frame, text="🗑 Remove", command=lambda l=listbox: self.remove_from_list(l)).grid(row=0, column=1, padx=5)

            self.rule_widgets[rule_name] = {"toggle": toggle, "listbox": listbox}
            row += 1

        custom_frame = ttk.Frame(self, style="Content.TFrame")
        custom_frame.grid(row=2, column=0, pady=20, padx=30, sticky="nsew")
        custom_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(custom_frame, text="Add Custom Block Rule:").grid(row=0, column=0, pady=10, padx=10)
        self.pattern_entry = ttk.Entry(custom_frame, width=50)
        self.pattern_entry.grid(row=1, column=0, pady=5, padx=10)
        
        button_frame = ttk.Frame(custom_frame)
        button_frame.grid(row=2, column=0, pady=10)
        ttk.Button(button_frame, text="➕ Add Rule", command=self.add_rule, style="Accent.TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🗑 Remove Rule", command=self.remove_rule, style="Accent.TButton").grid(row=0, column=1, padx=10)

    def toggle_rule(self, rule_name):
        enabled = self.rules[rule_name]["enabled"].get()
        self.controller.firewall.add_block_rule(rule_name, enabled)

    def add_to_list(self, rule_name, listbox):
        if "URL" in rule_name:
            prompt = "Enter URL to Block:"
        elif "Text" in rule_name:
            prompt = "Enter Text to Block:"
        elif "Domains" in rule_name:
            prompt = "Enter Domain to Block:"
        else:
            prompt = "Enter Item to Block:"

        item = simpledialog.askstring("Add Item", prompt)
        if item and item not in self.rules[rule_name]["list"]:
            self.rules[rule_name]["list"].append(item)
            listbox.insert(tk.END, item)
            self.controller.firewall.update_rule_list(rule_name, self.rules[rule_name]["list"])

    def remove_from_list(self, listbox):
        selected = listbox.curselection()
        if selected:
            item = listbox.get(selected)
            rule_name = next(r for r, data in self.rules.items() if listbox in [data["listbox"] for data in self.rule_widgets.values()])
            self.rules[rule_name]["list"].remove(item)
            listbox.delete(selected)
            self.controller.firewall.update_rule_list(rule_name, self.rules[rule_name]["list"])

    def add_rule(self):
        pattern = self.pattern_entry.get().strip()
        if not pattern:
            messagebox.showerror("Error", "Rule cannot be empty!")
            return
        if pattern in self.rules:
            messagebox.showerror("Error", "Rule already exists!")
            return

        self.rules[pattern] = {"enabled": tk.BooleanVar(value=True), "list": []}
        toggle = ttk.Checkbutton(self, text=pattern, variable=self.rules[pattern]["enabled"], style="Toggle.TCheckbutton", command=lambda r=pattern: self.toggle_rule(r))
        toggle.grid(row=len(self.rules) - 1, column=0, pady=8, padx=10, sticky="w")
        
        listbox = tk.Listbox(self, height=3, width=50, bg="#000000", fg="#ffffff")
        listbox.grid(row=len(self.rules) - 1, column=1, pady=8, padx=10, sticky="ew")
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=len(self.rules) - 1, column=2, pady=8, padx=5, sticky="w")
        ttk.Button(btn_frame, text="➕ Add", command=lambda r=pattern, l=listbox: self.add_to_list(r, l)).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🗑 Remove", command=lambda l=listbox: self.remove_from_list(l)).grid(row=0, column=1, padx=5)

        self.rule_widgets[pattern] = {"toggle": toggle, "listbox": listbox}
        self.pattern_entry.delete(0, tk.END)
        self.controller.firewall.add_block_rule(pattern, True)

    def remove_rule(self):
        selected = None
        for rule, widgets in self.rule_widgets.items():
            if widgets["toggle"].winfo_exists():
                selected = rule
                break
        if not selected:
            messagebox.showerror("Error", "Select a rule to remove!")
            return

        del self.rules[selected]
        self.rule_widgets[selected]["toggle"].destroy()
        self.rule_widgets[selected]["listbox"].destroy()
        self.rule_widgets[selected]["btn_frame"].destroy()
        del self.rule_widgets[selected]
        self.controller.firewall.remove_block_rule(selected)

    def update_rule_list(self, rule_name, rule_list):
        self.rules[rule_name]["list"] = rule_list
        listbox = self.rule_widgets[rule_name]["listbox"]
        listbox.delete(0, tk.END)
        for item in rule_list:
            listbox.insert(tk.END, item)