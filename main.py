import tkinter as tk
import json
import os

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
        self.root.geometry("900x650")

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

        # map canvas
        self.canvas = tk.Canvas(self.root, bg="#e8f5e9", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

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
        """Draw the map background and campsite pins on the canvas."""
        self.canvas.delete("all")

        # draw each campsite pin from our database
        for site in self.campsites:
            x, y = site["x"], site["y"]
            avg_text = self.get_average_rating(site["ratings"])

            # pin circle
            self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                fill="#16a34a", outline="white", width=2
            )
            # label next to pin
            self.canvas.create_text(
                x + 14, y,
                text=f"{site['name']}\n{avg_text}",
                anchor="w",
                font=("Arial", 10, "bold"),
                fill="#0f172a"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = TrailPinApp(root)
    root.mainloop()