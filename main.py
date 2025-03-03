import tkinter as tk
from tkinter import ttk, messagebox
from dashboard import Dashboard
from firewall_logic import FirewallLogic, run_proxy
import threading
import queue
from styles import apply_theme

class FirewallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Firewall - SDF")
        self.geometry("1200x800")  
        self.minsize(1200, 800)   
        self.maxsize(1200, 800)    
        apply_theme(self)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_columnconfigure(0, weight=0)

        self.container = ttk.Frame(self, style="Main.TFrame")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_propagate(False)
        self.container.configure(width=1200, height=800)


        self.queue = queue.Queue()


        self.firewall = FirewallLogic(self, self.queue)
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
        status_label = ttk.Label(self, textvariable=self.status_var, style="Subheader.TLabel")
        status_label.place(x=10, y=50)

        self.update_ui()

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

    def start_firewall(self):
        if not self.running:
            if messagebox.askyesno("Start Firewall", "Are you sure you want to start the firewall?"):
                self.running = True
                self.proxy_thread = threading.Thread(target=run_proxy, args=(self.firewall,))
                self.proxy_thread.daemon = True
                self.proxy_thread.start()
                self.status_var.set("Firewall: Running")
                messagebox.showinfo("Firewall", "Firewall started successfully!")
                logging.info("Firewall started")

    def stop_firewall(self):
        if self.running:
            if messagebox.askyesno("Stop Firewall", "Are you sure you want to stop the firewall?"):
                self.running = False
                if self.proxy_thread:
                    self.firewall.master.shutdown()
                self.status_var.set("Firewall: Stopped")
                messagebox.showinfo("Firewall", "Firewall stopped.")
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    app = FirewallApp()
    app.mainloop()