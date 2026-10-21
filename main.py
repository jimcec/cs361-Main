import tkinter as tk
from tkinter import messagebox
import json
import os
import tkintermapview

DB_FILE = "campsites.json"

# starter campsites for Pictured Rocks National Lakeshore
INITIAL_CAMPSITES = [
    {
        "id": 1,
        "name": "Twelvemile Beach Campground",
        "lat": 46.6391,
        "lng": -86.2177,
        "notes": "Pictured Rocks National Lakeshore; situated on a high sandy plateau above Lake Superior.",
        "ratings": [5, 4]
    },
    {
        "id": 2,
        "name": "Hurricane River Campground",
        "lat": 46.6730,
        "lng": -86.1390,
        "notes": "Located where the Hurricane River flows into Lake Superior near the Au Sable Light Station.",
        "ratings": [5, 5]
    }
]


class TrailPinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrailPin Campsite Map — Step 4 (Rate Campsites)")
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

        # real map widget
        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # set starting map position (Pictured Rocks National Lakeshore, MI) and zoom
        self.map_widget.set_position(46.6550, -86.1800)
        self.map_widget.set_zoom(11)

        # add right-click context menu to plot new campsite
        self.map_widget.add_right_click_menu_command(label="[+] Add Campsite Here", command=self.open_add_popup,
                                                     pass_coords=True)

        # on-screen zoom and pan controls frame
        self.controls_frame = tk.Frame(self.map_container, bg="white", bd=2, relief=tk.RAISED)
        self.controls_frame.place(relx=0.97, rely=0.03, anchor="ne")

        # zoom and pan control buttons
        tk.Button(self.controls_frame, text="Zoom +", width=8, command=self.zoom_in).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="Zoom −", width=8, command=self.zoom_out).pack(padx=4, pady=2)

        tk.Button(self.controls_frame, text="▲", width=8, command=lambda: self.pan(1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▼", width=8, command=lambda: self.pan(-1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="◀", width=8, command=lambda: self.pan(0, -1)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▶", width=8, command=lambda: self.pan(0, 1)).pack(padx=4, pady=1)

        # bottom status bar
        self.status_label = tk.Label(
            self.root,
            text=f"Loaded {len(self.campsites)} campsites | Click an existing pin to Rate it, or Right-click to Add!",
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

            # add command to marker so clicking it opens the Rating Popup
            marker = self.map_widget.set_marker(
                site["lat"],
                site["lng"],
                text=f"{site['name']}\n{avg_text}",
                command=self.marker_click_handler
            )
            # attach the site dictionary to the marker object so we know which one was clicked
            marker.site_data = site

    def marker_click_handler(self, marker):
        """Handler triggered when a map marker is clicked."""
        self.open_rate_popup(marker.site_data)

    # ==========================================
    # ADD CAMPSITE POPUP (USER STORY 2)
    # ==========================================
    def open_add_popup(self, coords):
        """Open a popup window to enter details for a new campsite pin."""
        popup = tk.Toplevel(self.root)
        popup.title("Add New Campsite Pin")
        popup.geometry("350x250")
        popup.grab_set()  # Lock interaction to this window until closed

        tk.Label(popup, text="Campsite Name (Required):", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        name_entry = tk.Entry(popup, width=40)
        name_entry.pack(pady=5)

        tk.Label(popup, text=f"Coordinates: {coords[0]:.4f}° N, {coords[1]:.4f}° W", fg="#475569").pack(pady=5)

        tk.Label(popup, text="Amenities / Notes (Optional):", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        notes_entry = tk.Entry(popup, width=40)
        notes_entry.pack(pady=5)

        # action Buttons
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Cancel", command=popup.destroy, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Save Pin", bg="#16a34a", fg="white", width=10,
                  command=lambda: self.save_new_campsite(name_entry.get(), coords[0], coords[1], notes_entry.get(),
                                                         popup)).pack(side=tk.LEFT, padx=10)

        name_entry.focus()

    def save_new_campsite(self, name, lat, lng, notes, popup):
        """Save the new campsite to the database and redraw the map."""
        if not name.strip():
            messagebox.showwarning("Missing Info", "Please enter a Campsite Name.", parent=popup)
            return

        new_site = {
            "id": len(self.campsites) + 1,
            "name": name.strip(),
            "lat": lat,
            "lng": lng,
            "notes": notes.strip(),
            "ratings": []
        }

        self.campsites.append(new_site)
        self.save_database(self.campsites)
        self.draw_map()

        self.status_label.config(
            text=f"Saved '{new_site['name']}' to local database. Total sites: {len(self.campsites)}")
        popup.destroy()

    # ==========================================
    # RATE CAMPSITE POPUP (USER STORY 3)
    # ==========================================
    def open_rate_popup(self, site):
        """Open a popup window to rate an existing campsite."""
        self.rate_popup = tk.Toplevel(self.root)
        self.rate_popup.title("Rate Campsite")
        self.rate_popup.geometry("350x250")
        self.rate_popup.grab_set()

        self.current_rating = tk.IntVar(value=5)  # Default to 5 stars

        # header info
        tk.Label(self.rate_popup, text=site["name"], font=("Arial", 12, "bold"), fg="#14532d").pack(pady=(10, 0))
        avg_text = self.get_average_rating(site["ratings"])
        tk.Label(self.rate_popup, text=f"Current Average: {avg_text}", fg="#b45309").pack(pady=5)

        tk.Label(self.rate_popup, text="Select 1–5 Stars:", font=("Arial", 10, "bold")).pack(pady=(10, 5))

        # star selection frame
        star_frame = tk.Frame(self.rate_popup)
        star_frame.pack(pady=5)

        for i in range(1, 6):
            tk.Radiobutton(
                star_frame, text=f"{i} ★", variable=self.current_rating, value=i,
                indicatoron=0, width=5, bg="#fef08a", selectcolor="#ca8a04", font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=2)

        tk.Label(self.rate_popup, text="Hint: You can press keys [1]-[5] and [Enter]", fg="#1d4ed8",
                 font=("Arial", 8)).pack()

        # action buttons
        btn_frame = tk.Frame(self.rate_popup)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Cancel (Esc)", command=self.rate_popup.destroy, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Submit (Enter)", bg="#16a34a", fg="white", width=12,
                  command=lambda: self.submit_rating(site, self.current_rating.get())).pack(side=tk.LEFT, padx=10)

        # keyboard navigation bindings (Usability Requirement & IH#7)
        self.rate_popup.bind("<Key-1>", lambda e: self.current_rating.set(1))
        self.rate_popup.bind("<Key-2>", lambda e: self.current_rating.set(2))
        self.rate_popup.bind("<Key-3>", lambda e: self.current_rating.set(3))
        self.rate_popup.bind("<Key-4>", lambda e: self.current_rating.set(4))
        self.rate_popup.bind("<Key-5>", lambda e: self.current_rating.set(5))
        self.rate_popup.bind("<Return>", lambda e: self.submit_rating(site, self.current_rating.get()))
        self.rate_popup.bind("<Escape>", lambda e: self.rate_popup.destroy())

        self.rate_popup.focus_set()

    def submit_rating(self, site, stars):
        """Save the new rating to the database and recalculate."""
        site["ratings"].append(stars)
        self.save_database(self.campsites)
        self.draw_map()

        new_avg = self.get_average_rating(site["ratings"])
        self.status_label.config(text=f"✓ Rating Saved! {site['name']} is now {new_avg}.")
        self.rate_popup.destroy()

    # ==========================================
    # MAP NAVIGATION CONTROLS
    # ==========================================
    def zoom_in(self):
        """zoom in map view"""
        self.map_widget.set_zoom(self.map_widget.zoom + 1)

    def zoom_out(self):
        """zoom out map view"""
        self.map_widget.set_zoom(self.map_widget.zoom - 1)

    def pan(self, d_lat, d_lng):
        """pan map via control buttons"""
        current_pos = self.map_widget.get_position()
        delta = 10 / (2 ** self.map_widget.zoom)
        new_lat = current_pos[0] + (d_lat * delta * 5)
        new_lng = current_pos[1] + (d_lng * delta * 10)
        self.map_widget.set_position(new_lat, new_lng)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrailPinApp(root)
    root.mainloop()