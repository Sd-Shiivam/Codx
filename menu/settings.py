import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from styles import apply_styles
import subprocess
import os
import platform

class SettingsMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.configure(width=900, height=800, padding=20)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # Allow status area to expand

        # Header
        header = ttk.Label(self, text="⚙ SETTINGS", style="Header.TLabel", font=("Arial", 24, "bold"))
        header.grid(row=0, column=0, pady=(0, 30), padx=30)

        # Proxy Settings Frame
        proxy_frame = ttk.LabelFrame(self, text=" Proxy Configuration ", padding=15, style="Modern.TLabelframe")
        proxy_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        proxy_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(proxy_frame, text="Host:", style="SubHeader.TLabel").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.proxy_host = ttk.Entry(proxy_frame, width=25, style="Modern.TEntry")
        self.proxy_host.insert(0, "127.0.0.1")
        self.proxy_host.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(proxy_frame, text="Port:", style="SubHeader.TLabel").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.proxy_port = ttk.Entry(proxy_frame, width=10, style="Modern.TEntry")
        self.proxy_port.insert(0, "8080")
        self.proxy_port.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.apply_btn = ttk.Button(proxy_frame, text="Apply Changes", command=self.apply_proxy_settings, style="Accent.TButton", width=20)
        self.apply_btn.grid(row=2, column=0, columnspan=2, pady=15)

        # Firewall Controls Frame
        firewall_frame = ttk.LabelFrame(self, text=" Firewall Options ", padding=15, style="Modern.TLabelframe")
        firewall_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        firewall_frame.grid_columnconfigure(0, weight=1)

        self.sandbox_var = tk.BooleanVar(value=self.controller.firewall.sandbox_mode)
        self.sandbox_toggle = ttk.Checkbutton(
            firewall_frame, text="Enable Sandbox Mode", variable=self.sandbox_var, 
            command=self.toggle_sandbox, style="Modern.TCheckbutton"
        )
        self.sandbox_toggle.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        btn_frame = ttk.Frame(firewall_frame, style="Content.TFrame")
        btn_frame.grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Button(btn_frame, text="Export Rules", command=self.export_rules, style="Secondary.TButton", width=15).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Import Rules", command=self.import_rules, style="Secondary.TButton", width=15).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Install Trust Certificate", command=self.install_cert, style="Secondary.TButton", width=20).grid(row=0, column=2, padx=5)

        # Status Bar
        self.status_frame = ttk.Frame(self, style="Status.TFrame", padding=10)
        self.status_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.status_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.status_frame, text="Status:", style="SubHeader.TLabel").grid(row=0, column=0, padx=5, sticky="w")
        self.status_label = ttk.Label(self.status_frame, text="Proxy Config : 127.0.0.1:8080", foreground="red", style="Status.TLabel")
        self.status_label.grid(row=0, column=1, padx=5, sticky="w")

        # self.add_tooltips()
        self.apply_initial_status()

    def apply_proxy_settings(self):
        host = self.proxy_host.get()
        port = self.proxy_port.get()

        if not self.validate_ip(host):
            messagebox.showerror("Error", "Invalid IP address format!")
            return
        
        if not port.isdigit() or not (1 <= int(port) <= 65535):
            messagebox.showerror("Error", "Invalid port number! (1-65535)")
            return
        
        self.controller.fhost=host
        self.controller.fport=port
        self.status_label.config(text=f"Proxy config: {host}:{port}", foreground="green")

    def toggle_sandbox(self):
        enabled = self.sandbox_var.get()
        self.controller.firewall.set_sandbox_mode(enabled)
        status = "Enabled" if enabled else "Disabled"
        color = "green" if enabled else "red"
        self.status_label.config(text=f"Sandbox Mode: {status}", foreground=color)
        messagebox.showinfo("Sandbox Mode", f"Sandbox mode {status.lower()}")

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

    def apply_initial_status(self):
        """Set initial status based on sandbox mode."""
        status = "Enabled" if self.sandbox_var.get() else "Disabled"
        color = "green" if self.sandbox_var.get() else "red"
        self.status_label.config(text=f"Sandbox Mode: {status}", foreground=color)


    def install_cert(self):
        try:
            import sys
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            cert_path = os.path.join(base_path, 'images/Codx_ssl.crt')
            if not os.path.exists(cert_path):
                messagebox.showerror("Error", "Certificate file not found!")
                return
                
            os_name = platform.system()
            
            if os_name == "Windows":
                subprocess.run(["certutil", "-addstore", "ROOT", cert_path], check=True)
                messagebox.showinfo("Success", "Certificate has been installed to Windows certificate store.")

        except Exception as e:
            messagebox.showerror("Installation Failed", "Could not install certificate: Need Admin permisson.Try run as adminstration.")

    # def add_tooltips(self):
    #     self.create_tooltip(self.apply_btn, "Apply proxy host and port settings")
    #     self.create_tooltip(self.sandbox_toggle, "Toggle sandbox mode for request interception")
    #     self.create_tooltip(self.status_frame, "Current proxy and sandbox status")

    def create_tooltip(self, widget, text):
        """Creates a tooltip for a widget."""
        def show(event):
            x, y = event.widget.winfo_rootx() + 30, event.widget.winfo_rooty() + 25
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=text, background="#333333", foreground="white", 
                             relief="solid", borderwidth=1, font=("Arial", 10), padx=5, pady=2)
            label.pack()
        
        def hide(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    @staticmethod
    def validate_ip(ip):
        """Validates an IP address."""
        pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        return re.match(pattern, ip) is not None and all(0 <= int(octet) <= 255 for octet in ip.split("."))