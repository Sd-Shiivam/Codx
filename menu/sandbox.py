import tkinter as tk
from tkinter import ttk, messagebox
from styles import apply_styles
from mitmproxy import http

class SandboxMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.configure(width=900, height=800)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="SANDBOX", style="Header.TLabel").grid(row=0, column=0, pady=20, padx=20)

        self.intercept_enabled = tk.BooleanVar(value=False)
        self.toggle_button = ttk.Button(self, text="🔴 Interception Off", command=self.toggle_interception, style="Accent.TButton")
        self.toggle_button.grid(row=1, column=0, pady=10)

        list_frame = ttk.Frame(self)
        list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)

        self.request_list = tk.Listbox(list_frame, height=15, width=60, bg="#1e1e1e", fg="#ffffff", font=("Arial", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.request_list.yview)
        self.request_list.config(yscrollcommand=scrollbar.set)

        self.request_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.details_text = tk.Text(self, height=5, width=60, bg="#2b2b2b", fg="#ffffff", font=("Arial", 10))
        self.details_text.grid(row=3, column=0, padx=20, pady=10)
        self.details_text.insert(tk.END, "Request details will appear here...")
        self.details_text.config(state=tk.DISABLED)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, pady=10)

        ttk.Button(button_frame, text="✔ Allow Request", command=self.allow_request, style="Accent.TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="❌ Block Request", command=self.block_request, style="Accent.TButton").grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="🗑 Clear List", command=self.clear_requests, style="Accent.TButton").grid(row=0, column=2, padx=10)

        self.current_request = None

    def toggle_interception(self):
        self.intercept_enabled.set(not self.intercept_enabled.get())
        if self.intercept_enabled.get():
            self.toggle_button.config(text="🟢 Interception On")
        else:
            self.toggle_button.config(text="🔴 Interception Off")

    def handle_sandbox(self, flow):
        if not self.intercept_enabled.get():
            return 
        
        self.current_request = flow
        self.request_list.insert(tk.END, f"{flow.request.method} {flow.request.pretty_url}")
        self.request_list.see(tk.END)
        
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, f"🔹 Method: {flow.request.method}\n")
        self.details_text.insert(tk.END, f"🔹 URL: {flow.request.pretty_url}\n")
        self.details_text.insert(tk.END, f"🔹 Headers: {flow.request.headers}\n")
        self.details_text.insert(tk.END, f"🔹 Body: {flow.request.content[:500]}\n")
        self.details_text.config(state=tk.DISABLED)

    def allow_request(self):
        if not self.current_request:
            messagebox.showwarning("No Request", "No request selected to allow.")
            return

        self.controller.firewall.allow_sandbox_request(self.current_request)
        self.remove_last_request()
        self.current_request = None

    def block_request(self):
        if not self.current_request:
            messagebox.showwarning("No Request", "No request selected to block.")
            return

        self.current_request.response = http.Response.make(403, b"Blocked in Sandbox")
        self.controller.firewall.queue.put(("ALERT", f"Blocked: {self.current_request.request.pretty_url}"))
        self.remove_last_request()
        self.current_request = None

    def remove_last_request(self):
        if self.request_list.size() > 0:
            self.request_list.delete(tk.END)
        
        # Clear details panel
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Request details will appear here...")
        self.details_text.config(state=tk.DISABLED)

    def clear_requests(self):
        self.request_list.delete(0, tk.END)
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Request details will appear here...")
        self.details_text.config(state=tk.DISABLED)
        self.current_request = None