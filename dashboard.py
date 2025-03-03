import tkinter as tk
from tkinter import ttk
from menu.dashboard_menu import DashboardMenu
from menu.content_block import ContentBlockMenu
from menu.traffic_filter import TrafficFilterMenu
from menu.safety_alerts import SafetyAlertsMenu
from menu.sandbox import SandboxMenu
from menu.settings import SettingsMenu
from menu.about import AboutMenu
from styles import apply_styles
import time

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        apply_styles(self)
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.left_panel = self.create_sidebar()
        self.right_panel = self.create_content_area()
        
        self.pages = {}
        self.load_pages()
        self.create_menu()
        self.show_page("DashboardMenu")

    def create_sidebar(self):
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=300, height=800)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        return sidebar

    def create_content_area(self):
        content = ttk.Frame(self, style="Content.TFrame", width=900, height=800)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_propagate(False)
        return content

    def create_menu(self):
        menu_items = [
            ("Dashboard", "📋", DashboardMenu),
            ("Content Block", "🔒", ContentBlockMenu),
            ("Traffic Filter", "🔍", TrafficFilterMenu),
            ("Safety Alerts", "⚠️", SafetyAlertsMenu),
            ("Sandbox", "🧪", SandboxMenu),
            ("Settings", "⚙️", SettingsMenu),
            ("About", "❓", AboutMenu),
        ]
        self.menu_buttons = {}
        
        logo = ttk.Label(self.left_panel, text="SDF", style="Logo.TLabel", font=("Arial", 28, "bold"))
        logo.grid(row=0, column=0, pady=(15, 5), padx=15)
        
        for idx, (text, icon, page) in enumerate(menu_items):
            btn = ttk.Button(self.left_panel, text=f"{icon} {text}", command=lambda p=page: self.show_page(p.__name__), 
                             style="Menu.TButton", padding=(5, 10))
            btn.grid(row=idx + 1, column=0, pady=5, padx=15, sticky="ew")
            self.menu_buttons[page.__name__] = btn
        
        date_label = ttk.Label(self.left_panel, text=f"Date: {time.strftime('%d %b %Y')}", style="Date.TLabel")
        date_label.grid(row=len(menu_items) + 1, column=0, pady=(5, 10), padx=15)
        
        self.create_firewall_controls()

    def create_firewall_controls(self):
        start_btn = ttk.Button(self.left_panel, text="Start Firewall", command=self.controller.start_firewall, 
                               style="Accent.TButton", padding=(8, 5))
        start_btn.grid(row=9, column=0, pady=(5, 5), padx=15, sticky="w")
        
        stop_btn = ttk.Button(self.left_panel, text="Stop Firewall", command=self.controller.stop_firewall, 
                              style="Accent.TButton", padding=(8, 5))
        stop_btn.grid(row=10, column=0, pady=(5, 15), padx=15, sticky="w")
    
    def load_pages(self):
        for PageClass in (DashboardMenu, ContentBlockMenu, TrafficFilterMenu, SafetyAlertsMenu, SandboxMenu, SettingsMenu, AboutMenu):
            page = PageClass(self.right_panel, self.controller)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
            page.grid_propagate(False)
            page.configure(width=900, height=800)
    
    def show_page(self, page_name):
        if page_name in self.pages:
            self.pages[page_name].tkraise()
            for btn in self.menu_buttons.values():
                btn.configure(style="Menu.TButton")
            if page_name in self.menu_buttons:
                self.menu_buttons[page_name].configure(style="ActiveMenu.TButton")

    def update_traffic(self, traffic_data):
        if hasattr(self.pages.get("DashboardMenu"), "update_traffic"):
            self.pages["DashboardMenu"].update_traffic(traffic_data)
    
    def show_alert(self, alert_data):
        if hasattr(self.pages.get("SafetyAlertsMenu"), "add_alert"):
            self.pages["SafetyAlertsMenu"].add_alert(alert_data)
        if hasattr(self.pages.get("DashboardMenu"), "add_alert_to_timeline"):
            self.pages["DashboardMenu"].add_alert_to_timeline(alert_data)
    
    def toggle_proxy(self, enable):
        if hasattr(self.pages.get("SettingsMenu"), "toggle_proxy"):
            self.pages["SettingsMenu"].toggle_proxy(enable)
    
    def toggle_sandbox(self, enable):
        if hasattr(self.pages.get("SandboxMenu"), "toggle_sandbox"):
            self.pages["SandboxMenu"].toggle_sandbox(enable)
