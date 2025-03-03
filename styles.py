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

def apply_styles(widget):
    if isinstance(widget, (tk.Text, tk.Canvas)):
        widget.configure(bg="#000000", fg="#ffffff")