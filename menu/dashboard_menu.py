import tkinter as tk
from tkinter import ttk, Canvas
from styles import apply_styles
from collections import deque
import time

class DashboardMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Content.TFrame")
        self.controller = controller
        apply_styles(self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_propagate(False)
        self.configure(width=900, height=800)

        header = ttk.Label(self, text="DASHBOARD", style="Header.TLabel", font=("Arial", 16, "bold"))
        header.grid(row=0, column=0, pady=20, padx=20, sticky="ew", columnspan=1)  # Span multiple columns for centering

        self.canvas_frame = ttk.Frame(self, style="Content.TFrame")
        self.canvas_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = Canvas(self.canvas_frame, bg="#121212", height=600, width=860, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", troughcolor="gray", background="black", borderwidth=1, relief="flat")
        self.scrollbar.configure(style="Vertical.TScrollbar")


        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux scroll down

        self.traffic_history = deque(maxlen=30)
        self.alerts_history = deque(maxlen=30)

        self.draw_network_map()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.scroll_target = 0
        self.scrolling = False
        self.last_y = 0

        self.after(2000, self.update_network_map)

    def update_traffic(self, traffic_data):
        self.traffic_history = deque(traffic_data, maxlen=100)
        self.draw_network_map()

    def add_alert_to_timeline(self, alert):
        self.alerts_history.append(alert)
        self.draw_network_map()

    def draw_network_map(self):
        """Draws the network map with sorted and unique entries."""
        self.canvas.delete("all")

        node_height = 30
        y_start = 20
        y_spacing = 45
        x_base = 430

        combined_history = list(self.traffic_history) + list(self.alerts_history)

        def extract_timestamp(entry):
            if isinstance(entry, tuple): 
                return entry[1]
            elif " at " in entry:  
                try:
                    return entry.split(" at ")[1]
                except IndexError:
                    return "00:00:00"
            return "00:00:00" 

        combined_history.sort(key=extract_timestamp, reverse=True)

        unique_history = deque(maxlen=30)
        seen = set()

        for item in combined_history:
            if isinstance(item, tuple): 
                key = item[0] 
            else: 
                key = item.split(" at ")[0] if " at " in item else item

            if key not in seen:
                seen.add(key)
                unique_history.append(item)

        for idx, item in enumerate(reversed(list(unique_history))):
            y = y_start + idx * y_spacing

            if isinstance(item, tuple): 
                domain, timestamp = item
                self.canvas.create_oval(x_base - 12, y - 12, x_base + 12, y + 12, fill="#e74c3c", outline="#c0392b", width=2)
                self.canvas.create_text(x_base - 120, y, text=domain, fill="#ffffff", font=("Arial", 10, "bold"), anchor="e")
                self.canvas.create_text(x_base + 100, y, text=timestamp, fill="#aaaaaa", font=("Arial", 8), anchor="w")

            else:  
                self.canvas.create_oval(x_base - 12, y - 12, x_base + 12, y + 12, fill="#ff5555", outline="#d63031", width=2)
                self.canvas.create_text(x_base, y, text=item, fill="#ffffff", font=("Arial", 9), anchor="center")

            if idx < len(unique_history) - 1:
                next_y = y_start + (idx + 1) * y_spacing
                self.canvas.create_line(x_base, y + 12, x_base, next_y - 12, fill="#66b0ff", width=3, dash=(4, 4))

        self.canvas.configure(scrollregion=(0, 0, 860, y_start + len(unique_history) * y_spacing + 20))

    def update_network_map(self):
        self.draw_network_map()
        self.after(2000, self.update_network_map)

    def on_mousewheel(self, event):
        if event.num == 4: 
            delta = -40
        elif event.num == 5: 
            delta = 40
        else:  
            delta = -event.delta * 10
        self.start_smooth_scroll(self.canvas.yview()[0] * self.canvas.winfo_height() + delta)

    def start_smooth_scroll(self, target_y):
        if not self.scrolling:
            self.scroll_target = target_y / self.canvas.winfo_height()
            self.scrolling = True
            self.smooth_scroll()

    def smooth_scroll(self):
        if not self.scrolling:
            return
        current = self.canvas.yview()[0]
        target = self.scroll_target
        if abs(current - target) < 0.005:
            self.canvas.yview_moveto(target)
            self.scrolling = False
            return
        step = (target - current) * 0.15
        self.canvas.yview_moveto(current + step)
        self.after(16, self.smooth_scroll)
