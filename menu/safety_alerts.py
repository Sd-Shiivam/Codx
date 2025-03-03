import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from styles import apply_styles

class SafetyAlertsMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.configure(width=900, height=800)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="SAFETY ALERTS", style="Header.TLabel").grid(row=0, column=0, pady=20, padx=20)

        self.alerts = scrolledtext.ScrolledText(self, height=20, width=60, bg="#1e1e1e", fg="#ff5555", font=("Arial", 10), state=tk.DISABLED)
        self.alerts.grid(row=1, column=0, padx=20, pady=10)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=10)

        ttk.Button(button_frame, text="🗑 Clear Alerts", command=self.clear_alerts, style="Accent.TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="💾 Export Alerts", command=self.export_alerts, style="Accent.TButton").grid(row=0, column=1, padx=10)

    def add_alert(self, alert, level="warning"):
        """Adds an alert to the text box and optionally displays a warning popup."""
        self.alerts.config(state=tk.NORMAL)
        color = "#ff5555" if level == "critical" else "#ffaa00"

        self.alerts.insert(tk.END, f"{alert}\n", level)
        self.alerts.tag_config(level, foreground=color)
        self.alerts.config(state=tk.DISABLED)
        self.alerts.see(tk.END)

        if level == "critical":
            messagebox.showerror("🚨 CRITICAL ALERT", alert)
        else:
            messagebox.showwarning("⚠ SAFETY ALERT", alert)

    def clear_alerts(self):
        """Clears all alerts from the text box."""
        self.alerts.config(state=tk.NORMAL)
        self.alerts.delete(1.0, tk.END)
        self.alerts.config(state=tk.DISABLED)

    def export_alerts(self):
        """Saves alerts to a file."""
        with open("safety_alerts.log", "w") as f:
            f.write(self.alerts.get(1.0, tk.END).strip())
        messagebox.showinfo("Export Successful", "Alerts saved to safety_alerts.log")

