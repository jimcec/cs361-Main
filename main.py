import tkinter as tk
import json
import os
import tkintermapview

DB_FILE = "campsites.json"

# starter campsites (x and y removed, now using real lat/lng)
INITIAL_CAMPSITES = [
    {
        "id": 1,
        "name": "Pine Ridge Camp",
        "lat": 44.0640,
        "lng": -121.3320,
        "notes": "Vault toilet, shaded tent pads near trailhead.",
        "ratings": [5, 4]
    },
    {
        "id": 2,
        "name": "Mirror Lake Site",
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

        # map widget
        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # set starting map position (Cascade Lakes, OR) and zoom
        self.map_widget.set_position(44.0582, -121.3153)
        self.map_widget.set_zoom(12)

        # on-screen zoom and pan controls frame
        self.controls_frame = tk.Frame(self.map_container, bg="white", bd=2, relief=tk.RAISED)
        self.controls_frame.place(relx=0.97, rely=0.03, anchor="ne")

        # zoom and pan control buttons
        tk.Button(self.controls_frame, text="Zoom +", width=8, command=self.zoom_in).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="Zoom −", width=8, command=self.zoom_out).pack(padx=4, pady=2)

        tk.Button(self.controls_frame, text="▲ Pan Up", width=8, command=lambda: self.pan(1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▼ Pan Down", width=8, command=lambda: self.pan(-1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="◀ Pan Left", width=8, command=lambda: self.pan(0, -1)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="Pan Right ▶", width=8, command=lambda: self.pan(0, 1)).pack(padx=4, pady=1)

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
        """Draw the campsite pins on the real map."""
        self.map_widget.delete_all_marker()

        # draw each campsite pin from our database
        for site in self.campsites:
            avg_text = self.get_average_rating(site["ratings"])
            self.map_widget.set_marker(
                site["lat"],
                site["lng"],
                text=f"{site['name']}\n{avg_text}"
            )

        self.status_label.config(
            text=f"Loaded {len(self.campsites)} campsites | Real map tiles active. You can zoom out and drag the map natively!"
        )

    def zoom_in(self):
        """zoom in map view"""
        self.map_widget.set_zoom(self.map_widget.zoom + 1)

    def zoom_out(self):
        """zoom out map view"""
        self.map_widget.set_zoom(self.map_widget.zoom - 1)

    def pan(self, d_lat, d_lng):
        """pan map via control buttons"""
        # Calculate a shift delta based on current zoom level
        current_pos = self.map_widget.get_position()
        delta = 10 / (2 ** self.map_widget.zoom)

        new_lat = current_pos[0] + (d_lat * delta * 5)
        new_lng = current_pos[1] + (d_lng * delta * 10)

        self.map_widget.set_position(new_lat, new_lng)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrailPinApp(root)
    root.mainloop()