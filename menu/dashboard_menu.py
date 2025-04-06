import tkinter as tk
from tkinter import ttk, Canvas
from styles import apply_styles  # Assuming this is in a separate styles.py file
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

        # Improved Header with subtle shadow effect
        header_frame = ttk.Frame(self, style="Content.TFrame")
        header_frame.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)  # Make column expandable
        header = ttk.Label(header_frame, text="DASHBOARD", style="Header.TLabel", font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, pady=5, sticky="ew")
        header.configure(anchor="center")  # Center the text in the label
        subheader = ttk.Label(header_frame, text="Network Activity Overview", style="status_label.TLabel", font=("Arial", 10), foreground="#aaaaaa")
        subheader.grid(row=1, column=0, sticky="ew",pady=(5,5))
        subheader.configure(anchor="center")  # Center the text in the label

        # Canvas frame with a slight border for depth
        self.canvas_frame = ttk.Frame(self, style="Content.TFrame")
        self.canvas_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = Canvas(self.canvas_frame, bg="#1e1e1e", height=600, width=860, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", troughcolor="#333333", background="#555555", borderwidth=1, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", "#777777")])  # Hover effect
        self.scrollbar.configure(style="Vertical.TScrollbar")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  
        self.canvas.bind("<Button-5>", self.on_mousewheel)

        self.traffic_history = deque(maxlen=5000)
        self.alerts_history = deque(maxlen=5000)

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
        self.canvas.delete("all")

        node_height = 1000
        y_start = 30
        y_spacing = 50  
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

        unique_history = deque(maxlen=5000)
        seen = set()

        for item in combined_history:
            if isinstance(item, tuple): 
                key = item[0] 
            else: 
                key = item.split(" at ")[0] if " at " in item else item

            if key not in seen:
                seen.add(key)
                unique_history.append(item)

        for idx, item in enumerate((list(unique_history))):
            y = y_start + idx * y_spacing

            if isinstance(item, tuple):  # Traffic data
                domain, timestamp = item
                # Larger node with hoverable tag
                node = self.canvas.create_oval(x_base - 15, y - 15, x_base + 15, y + 15, fill="#00aaff", outline="#0088cc", width=2, tags=f"node_{idx}")
                self.canvas.create_text(x_base - 130, y, text=domain, fill="#ffffff", font=("Arial", 11, "bold"), anchor="e", width=250)
                self.canvas.create_text(x_base + 130, y, text=timestamp, fill="#cccccc", font=("Arial", 9, "italic"), anchor="w")

            else:  # Alert
                node = self.canvas.create_oval(x_base - 15, y - 15, x_base + 15, y + 15, fill="#ff5555", outline="#cc4444", width=2, tags=f"node_{idx}")
                self.canvas.create_text(x_base - 130, y, text=item, fill="#ffffff", font=("Arial", 10, "bold"), anchor="e", width=300)

            # Connection line with gradient-like effect
            if idx < len(unique_history) - 1:
                next_y = y_start + (idx + 1) * y_spacing
                self.canvas.create_line(x_base, y + 15, x_base, next_y - 15, fill="#66b0ff", width=3, dash=(4, 2))

            # Hover effects
            self.canvas.tag_bind(f"node_{idx}", "<Enter>", lambda e, n=node: self.canvas.itemconfig(n, fill="#f1c40f"))
            self.canvas.tag_bind(f"node_{idx}", "<Leave>", lambda e, n=node, c="#00aaff" if isinstance(item, tuple) else "#ff5555": self.canvas.itemconfig(n, fill=c))

        # Add a subtle background grid for context
        for y in range(y_start, int(self.canvas["height"]), 50):
            self.canvas.create_line(0, y, 860, y, fill="#2a2a2a", width=1, dash=(2, 4))

        self.canvas.configure(scrollregion=(0, 0, 860, y_start + len(unique_history) * y_spacing + 30))

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

