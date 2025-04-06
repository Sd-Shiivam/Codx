import tkinter as tk
from tkinter import ttk, messagebox
from dashboard import Dashboard
from firewall_logic import FirewallLogic, run_proxy,remove_system_proxy,setup_system_proxy
import threading
import queue
from styles import apply_theme,apply_styles

class FirewallApp(tk.Tk):
    def __init__(self):
        super().__init__()
    
        self.title("Personal Firewall - SDF")
        self.geometry("1200x800")  
        self.minsize(1200, 800)   
        self.maxsize(1200, 800)    
        apply_theme(self)
        apply_styles(self)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_columnconfigure(0, weight=0)

        self.container = ttk.Frame(self, style="Main.TFrame")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_propagate(False)
        self.container.configure(width=1200, height=800)


        self.queue = queue.Queue()


        self.firewall = FirewallLogic(self, self.queue)
        self.fhost = "127.0.0.1"
        self.fport = 8080
        self.running = False
        self.proxy_thread = None
        self.pages = {}

        self.dashboard = Dashboard(self.container, self)
        self.pages["Dashboard"] = self.dashboard
        self.dashboard.grid(row=0, column=0, sticky="nsew")
        self.dashboard.grid_propagate(False)
        self.dashboard.configure(width=1200, height=800)

        self.show_page("Dashboard")

        self.status_var = tk.StringVar(value="Firewall: Stopped")
        status_label = ttk.Label(self, textvariable=self.status_var, style="status_label.TLabel")
        status_label.place(x=50, y=80)

        self.update_ui()

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

    def start_firewall(self):
        if not self.running:
            if messagebox.askyesno("Start Firewall", "Are you sure you want to start the firewall?"):
                self.running = True
                self.proxy_thread = threading.Thread(target=run_proxy, args=(self.firewall,self.fhost,self.fport,))
                setup_system_proxy(self.fhost,self.fport)
                self.proxy_thread.daemon = True
                self.proxy_thread.start()
                self.status_var.set("Firewall: Running")
                logging.info("Firewall started")

    def stop_firewall(self):
        if self.running:
            if messagebox.askyesno("Stop Firewall", "Are you sure you want to stop the firewall?"):
                if self.proxy_thread:
                    self.firewall.master.shutdown()
                remove_system_proxy()
                self.running = False
                self.status_var.set("Firewall: Stopped")
                logging.info("Firewall stopped")

    def update_ui(self):
        try:
            while not self.queue.empty():
                message, data = self.queue.get_nowait()
                if message == "TRAFFIC":
                    self.dashboard.update_traffic(data)
                elif message == "ALERT":
                    self.dashboard.show_alert(data)
                elif message == "SANDBOX_UPDATE":
                    self.dashboard.show_sandbox_update(data)
                elif message == "SETTINGS_UPDATE":
                    self.update_settings(data)
        except queue.Empty:
            pass
        except Exception as e:
            logging.error(f"UI update error: {e}")
        self.after(50, self.update_ui) 

    def update_settings(self, data):
        if "proxy_port" in data:
            self.firewall.set_proxy_port(data["proxy_port"])
        if "log_location" in data:
            self.firewall.set_log_location(data["log_location"])
        if "sandbox_mode" in data:
            self.firewall.set_sandbox_mode(data["sandbox_mode"])
        logging.info(f"Settings updated: {data}")

    def update_block_rules(self, rules):
        self.firewall.rules = rules
        logging.info(f"Block rules updated: {rules}")

    def update_traffic_rules(self, rules):
        self.firewall.traffic_rules = rules
        logging.info(f"Traffic rules updated: {rules}")

if __name__ == "__main__":
    import logging
    import ctypes
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    app = FirewallApp()
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    if not is_admin():
        messagebox.showwarning(
            "Administrator Privileges Required", 
            "Some firewall features may not work properly without administrator privileges. "
            "Please restart the application as administrator."
        )
    else:
        logging.info("Running with administrator privileges")
    app.mainloop()