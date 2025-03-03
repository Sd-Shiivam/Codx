import tkinter as tk
from tkinter import ttk
import webbrowser
from styles import apply_styles

class AboutMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.configure(width=900, height=800)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="ABOUT", style="Header.TLabel").grid(row=0, column=0, pady=20, padx=20)

        text_frame = ttk.Frame(self)
        text_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)

        self.manual_text = tk.Text(text_frame, height=20, width=60, bg="#1e1e1e", fg="#ffffff", 
                                   font=("Arial", 10), wrap="word", padx=10, pady=10)
        self.manual_text.insert(tk.END, 
            "🔥 Personal Firewall Manual 🔥\n\n"
            "1️⃣ Start the firewall using the Start button.\n"
            "2️⃣ Use the Dashboard to monitor traffic.\n"
            "3️⃣ Block content via Content Block menu.\n"
            "4️⃣ Filter traffic in Traffic Filter.\n"
            "5️⃣ Enable Safety Alerts for HTTP/virus detection.\n"
            "6️⃣ Use Sandbox for manual request control.\n"
            "7️⃣ Configure settings like proxy and logs.\n\n"
        )
        self.manual_text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.manual_text.yview)
        self.manual_text.config(yscrollcommand=scrollbar.set)

        self.manual_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, pady=10)

        ttk.Button(button_frame, text="📋 Copy to Clipboard", command=self.copy_to_clipboard, style="Accent.TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🌐 Open Website", command=self.open_website, style="Accent.TButton").grid(row=0, column=1, padx=10)

    def copy_to_clipboard(self):
        """Copy manual text to clipboard."""
        self.controller.clipboard_clear()
        self.controller.clipboard_append(
            "🔥 Personal Firewall Manual 🔥\n\n"
            "1️⃣ Start the firewall using the Start button.\n"
            "2️⃣ Use the Dashboard to monitor traffic.\n"
            "3️⃣ Block content via Content Block menu.\n"
            "4️⃣ Filter traffic in Traffic Filter.\n"
            "5️⃣ Enable Safety Alerts for HTTP/virus detection.\n"
            "6️⃣ Use Sandbox for manual request control.\n"
            "7️⃣ Configure settings like proxy and logs.\n\n"
        )
        self.controller.update()
        tk.messagebox.showinfo("Copied", "Manual copied to clipboard!")

    def open_website(self):
        """Open official documentation."""
        webbrowser.open("https://github.com/sd-shiivam")

