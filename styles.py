from tkinter import ttk
import tkinter as tk

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Main.TFrame", background="#000000")
    style.configure("Sidebar.TFrame", background="#1e1e1e", borderwidth=0)
    style.configure("Content.TFrame", background="#000000", borderwidth=0)

    style.configure("Header.TLabel", font=("Arial", 24, "bold"), foreground="#ffffff", background="#000000")
    style.configure("Subheader.TLabel", font=("Arial", 12), foreground="#cccccc", background="#000000")
    style.configure("Logo.TLabel", font=("Arial", 28, "bold"), foreground="#ff4444", background="#1e1e1e")
    style.configure("LogoShadow.TLabel", font=("Arial", 28, "bold"), foreground="#333333", background="#1e1e1e")  # Shadow effect
    style.configure("Date.TLabel", font=("Arial", 12), foreground="#999999", background="#1e1e1e")

    style.configure("Menu.TButton", font=("Arial", 12), foreground="#ffffff", background="#333333", padding=(5, 10))
    style.map("Menu.TButton", background=[("active", "#555555")])

    style.configure("ActiveMenu.TButton", font=("Arial", 12, "bold"), foreground="#ffffff", background="#ff4444", padding=(5, 10))
    style.map("ActiveMenu.TButton", background=[("active", "#cc3333")])

    style.configure("Accent.TButton", font=("Arial", 12, "bold"), foreground="#ffffff", background="#007acc", padding=(8, 5))
    style.map("Accent.TButton", background=[("active", "#005f99")])

    style.configure("Toggle.TCheckbutton", font=("Arial", 12), foreground="#ffffff", background="#000000")
    style.map("Toggle.TCheckbutton", background=[("selected", "#007acc")])
    
    style.configure("status_label.TLabel", font=("Arial", 15), foreground="#ffffff", background="#1e1e1e")

    style.configure("Modern.TLabelframe", background="#1e1e1e", foreground="#ffffff", borderwidth=2, relief="flat")
    style.configure("Modern.TLabelframe.Label", font=("Arial", 11, "bold"), foreground="#cccccc", background="#1e1e1e")

    style.configure("Modern.TEntry", fieldbackground="#333333", foreground="#ffffff", bordercolor="#555555", insertcolor="#ffffff")
    style.map("Modern.TEntry", fieldbackground=[("focus", "#444444")])

    style.configure("Modern.TCheckbutton", font=("Arial", 11), foreground="#ffffff", background="#000000")
    style.map("Modern.TCheckbutton", 
              background=[("selected", "#007acc"), ("active", "#333333")],
              foreground=[("selected", "#ffffff")])

    style.configure("Secondary.TButton", font=("Arial", 11), foreground="#ffffff", background="#6c757d", padding=(8, 5))
    style.map("Secondary.TButton", background=[("active", "#5a6268")])

    style.configure("Status.TFrame", background="#1e1e1e", relief="sunken", borderwidth=1)
    style.configure("Status.TLabel", font=("Arial", 10), foreground="#cccccc", background="#1e1e1e")

def apply_styles(widget):
    if isinstance(widget, (tk.Text, tk.Canvas)):
        widget.configure(bg="#000000", fg="#ffffff")
    if isinstance(widget, tk.Listbox):
        widget.configure(bg="#333333", fg="#ffffff", selectbackground="#007acc", selectforeground="#ffffff")