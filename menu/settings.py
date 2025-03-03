import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re

class SettingsMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller

        ttk.Label(self, text="SETTINGS", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        proxy_frame = ttk.LabelFrame(self, text="Proxy Settings", padding=10)
        proxy_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        ttk.Label(proxy_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.proxy_host = ttk.Entry(proxy_frame, width=20)
        self.proxy_host.insert(0, "127.0.0.1")
        self.proxy_host.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(proxy_frame, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.proxy_port = ttk.Entry(proxy_frame, width=10)
        self.proxy_port.insert(0, "8080")
        self.proxy_port.grid(row=1, column=1, padx=5, pady=5)
        
        self.apply_btn = ttk.Button(proxy_frame, text="Apply", command=self.apply_proxy_settings, style="Accent.TButton")
        self.apply_btn.grid(row=2, column=0, columnspan=2, pady=10)

        firewall_frame = ttk.LabelFrame(self, text="Firewall Controls", padding=10)
        firewall_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.sandbox_var = tk.BooleanVar(value=self.controller.firewall.sandbox_mode)
        self.sandbox_toggle = ttk.Checkbutton(
            firewall_frame, text="Enable Sandbox Mode", variable=self.sandbox_var, command=self.toggle_sandbox
        )
        self.sandbox_toggle.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Button(firewall_frame, text="Export Rules", command=self.export_rules).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(firewall_frame, text="Import Rules", command=self.import_rules).grid(row=1, column=1, padx=5, pady=5)

        self.status_label = ttk.Label(self, text="Proxy Status: Stopped", foreground="red")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.add_tooltips()

    def apply_proxy_settings(self):
        host = self.proxy_host.get()
        port = self.proxy_port.get()

        if not self.validate_ip(host):
            messagebox.showerror("Error", "Invalid IP address format!")
            return
        
        if not port.isdigit() or not (1 <= int(port) <= 65535):
            messagebox.showerror("Error", "Invalid port number! (1-65535)")
            return
        
        self.status_label.config(text=f"Proxy Status: Active ({host}:{port})", foreground="green")
        messagebox.showinfo("Settings", f"Proxy set to {host}:{port}")

    def toggle_sandbox(self):
        enabled = self.sandbox_var.get()
        self.controller.firewall.set_sandbox_mode(enabled)
        status = "enabled" if enabled else "disabled"
        color = "green" if enabled else "red"
        self.status_label.config(text=f"Sandbox Mode: {status.capitalize()}", foreground=color)
        messagebox.showinfo("Sandbox Mode", f"Sandbox mode {status}")

    def export_rules(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Export", f"Rules exported to {file_path} (Functionality TBD)")

    def import_rules(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Import", f"Rules imported from {file_path} (Functionality TBD)")

    def add_tooltips(self):
        """ Adds tooltips to important elements. """
        self.apply_btn.bind("<Enter>", lambda e: self.show_tooltip(self.apply_btn, "Apply proxy settings"))
        self.sandbox_toggle.bind("<Enter>", lambda e: self.show_tooltip(self.sandbox_toggle, "Enable/Disable sandbox mode"))

    def show_tooltip(self, widget, text):
        """ Shows a temporary tooltip. """
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25

        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack(ipadx=5, ipady=2)

        widget.bind("<Leave>", lambda e: tooltip.destroy())

    @staticmethod
    def validate_ip(ip):
        """ Validates an IP address. """
        pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        return re.match(pattern, ip) is not None and all(0 <= int(octet) <= 255 for octet in ip.split("."))

