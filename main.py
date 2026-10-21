import tkinter as tk
import json
import os
import time

DB_FILE = "campsites.json"

# starter campsites
INITIAL_CAMPSITES = [
    {
        "id": 1,
        "name": "Pine Ridge Camp",
        "x": 280,
        "y": 200,
        "lat": 44.0640,
        "lng": -121.3320,
        "notes": "Vault toilet, shaded tent pads near trailhead.",
        "ratings": [5, 4]
    },
    {
        "id": 2,
        "name": "Mirror Lake Site",
        "x": 520,
        "y": 320,
        "lat": 44.0480,
        "lng": -121.2980,
        "notes": "Lakeside tent spots; pack out all trash.",
        "ratings": [5, 5]
    }
]


class TrailPinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrailPin Campsite Map")
        self.root.geometry("1000x700")

        # load campsites from local JSON file
        self.campsites = self.load_database()

        # map navigation state for pan and zoom
        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0

        # top nav bar
        self.top_bar = tk.Frame(self.root, bg="#1e3a8a", pady=8, padx=10)
        self.top_bar.pack(fill=tk.X)

        self.title_label = tk.Label(
            self.top_bar,
            text="▲ TrailPin Campsite Map",
            fg="white",
            bg="#1e3a8a",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        # map container frame for canvas and controls
        self.map_container = tk.Frame(self.root)
        self.map_container.pack(fill=tk.BOTH, expand=True)

        # map canvas
        self.canvas = tk.Canvas(self.map_container, bg="#e8f5e9", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # on-screen zoom and pan controls frame
        self.controls_frame = tk.Frame(self.map_container, bg="white", bd=2, relief=tk.RAISED)
        self.controls_frame.place(relx=0.97, rely=0.03, anchor="ne")

        # zoom and pan control buttons
        tk.Button(self.controls_frame, text="Zoom +", width=8, command=self.zoom_in).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="Zoom −", width=8, command=self.zoom_out).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="▲ Pan Up", width=8, command=lambda: self.pan(0, -50)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="◀ Pan ▶", width=8, command=lambda: self.pan(50, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▼ Pan Down", width=8, command=lambda: self.pan(0, 50)).pack(padx=4, pady=1)

        # bottom status bar
        self.status_label = tk.Label(
            self.root,
            text=f"Loaded {len(self.campsites)} campsites from {DB_FILE}.",
            bg="#e2e8f0",
            fg="#1e293b",
            anchor="w",
            padx=10,
            pady=4
        )
        self.status_label.pack(fill=tk.X)

        # bind mouse events for pan and zoom
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_zoom)
        self.canvas.bind("<Button-4>", self.mouse_wheel_zoom)
        self.canvas.bind("<Button-5>", self.mouse_wheel_zoom)

        # draw starter pins
        self.draw_map()

    def load_database(self):
        """Load campsites from local JSON file, or create it if it doesn't exist."""
        if not os.path.exists(DB_FILE):
            self.save_database(INITIAL_CAMPSITES)
            return INITIAL_CAMPSITES
        with open(DB_FILE, "r") as file:
            return json.load(file)

    def save_database(self, data):
        """Save campsites list to local JSON file."""
        with open(DB_FILE, "w") as file:
            json.dump(data, file, indent=2)

    def get_average_rating(self, ratings):
        """Calculate the average star rating for a campsite."""
        if not ratings:
            return "No ratings"
        avg = sum(ratings) / len(ratings)
        return f"★ {avg:.1f} ({len(ratings)})"

    def draw_map(self):
        """Draw the map background and campsite pins on the canvas."""
        start_time = time.time()
        self.canvas.delete("all")

        # draw grid lines for terrain background
        for gx in range(-500, 2000, 80):
            rx = gx + self.pan_offset_x
            self.canvas.create_line(rx, 0, rx, 2000, fill="#c8e6c9", width=1)
        for gy in range(-500, 2000, 80):
            ry = gy + self.pan_offset_y
            self.canvas.create_line(0, ry, 2000, ry, fill="#c8e6c9", width=1)

        # draw river feature
        self.canvas.create_line(
            100 + self.pan_offset_x, 50 + self.pan_offset_y,
            400 + self.pan_offset_x, 600 + self.pan_offset_y,
            fill="#93c5fd", width=14
        )

        # draw each campsite pin from our database with zoom and pan applied
        for site in self.campsites:
            px = site["x"] * self.zoom_level + self.pan_offset_x
            py = site["y"] * self.zoom_level + self.pan_offset_y
            avg_text = self.get_average_rating(site["ratings"])

            r = max(5, int(8 * self.zoom_level))
            # pin circle
            self.canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill="#16a34a", outline="white", width=2
            )
            # label next to pin
            self.canvas.create_text(
                px + r + 6, py,
                text=f"{site['name']}\n{avg_text}",
                anchor="w",
                font=("Arial", max(8, int(10 * self.zoom_level)), "bold"),
                fill="#0f172a"
            )

        # calculate render time for responsiveness metric
        render_time = (time.time() - start_time) * 1000
        self.status_label.config(
            text=f"Loaded {len(self.campsites)} campsites | Zoom: {self.zoom_level:.1f}x | Render time: {render_time:.1f}ms (< 1000ms NFR)"
        )

    def start_pan(self, event):
        """start mouse drag panning"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def do_pan(self, event):
        """execute mouse drag panning offset"""
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.pan_offset_x += dx
        self.pan_offset_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.draw_map()

    def zoom_in(self):
        """zoom in map view"""
        if self.zoom_level < 2.5:
            self.zoom_level += 0.2
            self.draw_map()

    def zoom_out(self):
        """zoom out map view"""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.2
            self.draw_map()

    def pan(self, dx, dy):
        """pan map via control buttons"""
        self.pan_offset_x += dx
        self.pan_offset_y += dy
        self.draw_map()

    def mouse_wheel_zoom(self, event):
        """handle mouse wheel zoom event"""
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:
            self.zoom_out()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrailPinApp(root)
    root.mainloop()