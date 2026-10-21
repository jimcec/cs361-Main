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
        "reviews": [
            {"stars": 5, "comment": "Quiet pine forest, easy road access."},
            {"stars": 4, "comment": "Chilly at night, great fire rings."}
        ]
    },
    {
        "id": 2,
        "name": "Hurricane River Campground",
        "lat": 46.6730,
        "lng": -86.1390,
        "notes": "Located where the Hurricane River flows into Lake Superior near the Au Sable Light Station.",
        "reviews": [
            {"stars": 5, "comment": "Incredible sunrise views over Lake Superior!"},
            {"stars": 5, "comment": "Clean level ground right by the water."}
        ]
    }
]


class TrailPinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrailPin Campsite Map — Final Version (with Reviews)")
        self.root.geometry("1000x750")

        # load campsites from local JSON file
        self.campsites = self.load_database()

        # IH#5: Undo and Redo stacks
        self.undo_stack = []
        self.redo_stack = []

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

        # Undo / Redo / Reset Map Buttons in Top Bar
        tk.Button(self.top_bar, text="Reset Map", command=self.reset_map).pack(side=tk.RIGHT, padx=5)
        self.btn_redo = tk.Button(self.top_bar, text="↷ Redo (Y)", command=self.redo_action, state=tk.DISABLED)
        self.btn_redo.pack(side=tk.RIGHT, padx=5)
        self.btn_undo = tk.Button(self.top_bar, text="↶ Undo (Z)", command=self.undo_action, state=tk.DISABLED)
        self.btn_undo.pack(side=tk.RIGHT, padx=5)
        tk.Button(self.top_bar, text="+ Add Campsite (N)", bg="#2563eb", fg="white",
                  command=lambda: self.open_add_popup(self.map_widget.get_position())).pack(side=tk.RIGHT, padx=15)

        # Info Banner for IH#1, IH#2, IH#3
        self.info_frame = tk.Frame(self.root, bg="#eff6ff", pady=5, padx=10)
        self.info_frame.pack(fill=tk.X)
        tk.Label(self.info_frame, text="★ Why Plot & Rate Campsites? (Feature Benefits & Costs)",
                 font=("Arial", 10, "bold"), bg="#eff6ff", fg="#1e3a8a").pack(anchor="w")
        tk.Label(self.info_frame,
                 text="• Benefit (IH#1): Save unlisted campsites & view community star averages to plan trips faster.",
                 bg="#eff6ff", fg="#1e40af").pack(anchor="w")
        tk.Label(self.info_frame,
                 text="• Cost (IH#2): Takes ~15s, saves ~1 KB to local DB, and is visible on map (Undoable anytime).",
                 bg="#eff6ff", fg="#9a3412").pack(anchor="w")

        # map container frame
        self.map_container = tk.Frame(self.root)
        self.map_container.pack(fill=tk.BOTH, expand=True)

        # real map widget
        self.map_widget = tkintermapview.TkinterMapView(self.map_container, corner_radius=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.pack(fill=tk.BOTH, expand=True)

        # set starting map position
        self.map_widget.set_position(46.6550, -86.1800)
        self.map_widget.set_zoom(11)

        # add right-click context menu
        self.map_widget.add_right_click_menu_command(label="[+] Add Campsite Here", command=self.open_add_popup,
                                                     pass_coords=True)

        # on-screen zoom and pan controls frame
        self.controls_frame = tk.Frame(self.map_container, bg="white", bd=2, relief=tk.RAISED)
        self.controls_frame.place(relx=0.97, rely=0.03, anchor="ne")

        tk.Button(self.controls_frame, text="Zoom +", width=8, command=self.zoom_in).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="Zoom −", width=8, command=self.zoom_out).pack(padx=4, pady=2)
        tk.Button(self.controls_frame, text="▲", width=8, command=lambda: self.pan(1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▼", width=8, command=lambda: self.pan(-1, 0)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="◀", width=8, command=lambda: self.pan(0, -1)).pack(padx=4, pady=1)
        tk.Button(self.controls_frame, text="▶", width=8, command=lambda: self.pan(0, 1)).pack(padx=4, pady=1)

        # bottom status bar
        self.status_label = tk.Label(
            self.root,
            text=f"Loaded {len(self.campsites)} campsites | Click an existing pin to Rate & Review it, or Right-click to Add!",
            bg="#e2e8f0",
            fg="#1e293b",
            anchor="w",
            padx=10,
            pady=4
        )
        self.status_label.pack(fill=tk.X)

        # Global Keyboard Bindings
        self.root.bind("<z>", lambda e: self.undo_action())
        self.root.bind("<y>", lambda e: self.redo_action())
        self.root.bind("<n>", lambda e: self.open_add_popup(self.map_widget.get_position()))

        # draw starter pins
        self.draw_map()

    def load_database(self):
        if not os.path.exists(DB_FILE):
            self.save_database(INITIAL_CAMPSITES)
            return INITIAL_CAMPSITES
        with open(DB_FILE, "r") as file:
            return json.load(file)

    def save_database(self, data):
        with open(DB_FILE, "w") as file:
            json.dump(data, file, indent=2)

    def save_state_for_undo(self):
        self.undo_stack.append(json.dumps(self.campsites))
        self.redo_stack.clear()
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        self.btn_undo.config(state=tk.NORMAL if self.undo_stack else tk.DISABLED)
        self.btn_redo.config(state=tk.NORMAL if self.redo_stack else tk.DISABLED)

    def undo_action(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(json.dumps(self.campsites))
        previous_state = self.undo_stack.pop()
        self.campsites = json.loads(previous_state)
        self.save_database(self.campsites)
        self.draw_map()
        self.update_undo_redo_buttons()
        self.status_label.config(text="↶ Last action undone.")

    def redo_action(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(json.dumps(self.campsites))
        next_state = self.redo_stack.pop()
        self.campsites = json.loads(next_state)
        self.save_database(self.campsites)
        self.draw_map()
        self.update_undo_redo_buttons()
        self.status_label.config(text="↷ Action redone.")

    def get_average_rating(self, reviews):
        if not reviews:
            return "No ratings"
        avg = sum(r["stars"] for r in reviews) / len(reviews)
        return f"★ {avg:.1f} ({len(reviews)})"

    def draw_map(self):
        self.map_widget.delete_all_marker()
        for site in self.campsites:
            # Handle old databases seamlessly if they still use 'ratings' instead of 'reviews'
            if "reviews" not in site:
                site["reviews"] = [{"stars": r, "comment": ""} for r in site.get("ratings", [])]

            avg_text = self.get_average_rating(site["reviews"])
            marker = self.map_widget.set_marker(
                site["lat"],
                site["lng"],
                text=f"{site['name']}\n{avg_text}",
                command=self.marker_click_handler
            )
            marker.site_data = site

    def marker_click_handler(self, marker):
        self.open_rate_popup(marker.site_data)

    # ==========================================
    # ADD CAMPSITE POPUP (USER STORY 2)
    # ==========================================
    def open_add_popup(self, coords):
        popup = tk.Toplevel(self.root)
        popup.title("Add New Campsite Pin")
        popup.geometry("380x360")
        popup.grab_set()

        tk.Label(popup, text="Step 1: Pick Location [✓] -> Step 2: Details [●] -> Step 3: Save [○]", bg="#dbeafe",
                 fg="#1e3a8a").pack(fill=tk.X, pady=(0, 10))

        tk.Label(popup, text="Campsite Name (Required):", font=("Arial", 10, "bold")).pack()
        name_entry = tk.Entry(popup, width=40)
        name_entry.pack(pady=5)

        tk.Label(popup, text=f"Coordinates: {coords[0]:.4f}° N, {coords[1]:.4f}° W", fg="#475569").pack()

        tk.Label(popup, text="Amenities / Notes (Optional):", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        notes_entry = tk.Entry(popup, width=40)
        notes_entry.pack(pady=5)

        preview_frame = tk.Frame(popup, bg="#fffbeb", bd=1, relief=tk.SOLID)
        preview_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(preview_frame, text="🔍 [PREVIEW] Unsaved Pin Preview:", font=("Arial", 9, "bold"), bg="#fffbeb",
                 fg="#92400e").pack(anchor="w", padx=5)
        tk.Label(preview_frame, text="• Nothing is written to the database until you click 'Save'.", font=("Arial", 8),
                 bg="#fffbeb", fg="#15803d").pack(anchor="w", padx=5)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel", command=popup.destroy, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Save Pin", bg="#16a34a", fg="white", width=10,
                  command=lambda: self.save_new_campsite(name_entry.get(), coords[0], coords[1], notes_entry.get(),
                                                         popup)).pack(side=tk.LEFT, padx=10)

        name_entry.focus()

    def save_new_campsite(self, name, lat, lng, notes, popup):
        if not name.strip():
            messagebox.showwarning("Missing Info", "Please enter a Campsite Name.", parent=popup)
            return

        self.save_state_for_undo()

        new_site = {
            "id": len(self.campsites) + 1,
            "name": name.strip(),
            "lat": lat,
            "lng": lng,
            "notes": notes.strip(),
            "reviews": []
        }

        self.campsites.append(new_site)
        self.save_database(self.campsites)
        self.draw_map()
        self.status_label.config(text=f"Saved '{new_site['name']}'! You can Undo (Z) if needed.")
        popup.destroy()

    # ==========================================
    # RATE CAMPSITE POPUP (USER STORY 3)
    # ==========================================
    def open_rate_popup(self, site):
        self.rate_popup = tk.Toplevel(self.root)
        self.rate_popup.title("Rate & Review Campsite")
        self.rate_popup.geometry("380x480")
        self.rate_popup.grab_set()

        self.current_rating = tk.IntVar(value=5)

        tk.Label(self.rate_popup, text="Step 1: Pick 1-5 Stars [●] -> Step 2: Note [○] -> Step 3: Submit [○]",
                 bg="#dcfce7", fg="#14532d").pack(fill=tk.X, pady=(0, 10))

        # Header info
        tk.Label(self.rate_popup, text=site["name"], font=("Arial", 12, "bold"), fg="#14532d").pack()
        avg_text = self.get_average_rating(site["reviews"])
        tk.Label(self.rate_popup, text=f"Current Average: {avg_text}", fg="#b45309").pack()

        # Show recent reviews (Progressive Disclosure / IH#3)
        if site["reviews"]:
            reviews_frame = tk.Frame(self.rate_popup, bg="#f8fafc", bd=1, relief=tk.SOLID)
            reviews_frame.pack(fill=tk.X, padx=15, pady=5)
            tk.Label(reviews_frame, text="▾ Past Reviews (Showing latest 2):", font=("Arial", 8, "bold"), bg="#f8fafc",
                     fg="#1e3a8a").pack(anchor="w", padx=5)
            for r in site["reviews"][-2:]:
                comment = r.get("comment", "")
                display_comment = f'"{comment}"' if comment else "(Star rating only)"
                tk.Label(reviews_frame, text=f"★ {r['stars']}/5 — {display_comment}", font=("Arial", 8), bg="#f8fafc",
                         fg="#475569").pack(anchor="w", padx=5)

        tk.Label(self.rate_popup, text="Select 1–5 Stars:", font=("Arial", 10, "bold")).pack(pady=(10, 0))

        # Star selection frame
        star_frame = tk.Frame(self.rate_popup)
        star_frame.pack(pady=5)

        for i in range(1, 6):
            tk.Radiobutton(
                star_frame, text=f"{i} ★", variable=self.current_rating, value=i,
                command=lambda: self.update_live_preview(site),
                indicatoron=0, width=5, bg="#fef08a", selectcolor="#ca8a04", font=("Arial", 10, "bold")
            ).pack(side=tk.LEFT, padx=2)

        tk.Label(self.rate_popup, text="Hint: You can press keys [1]-[5]", fg="#1d4ed8", font=("Arial", 8)).pack()

        # WRITTEN REVIEW ENTRY
        tk.Label(self.rate_popup, text="Review Comment (Optional):", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.review_entry = tk.Entry(self.rate_popup, width=40)
        self.review_entry.pack(pady=5)

        self.preview_label = tk.Label(self.rate_popup, text="Live Preview: (Select a star to see updated average)",
                                      fg="#92400e", font=("Arial", 8, "italic"))
        self.preview_label.pack(pady=5)
        self.update_live_preview(site)

        # Action buttons
        btn_frame = tk.Frame(self.rate_popup)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Cancel (Esc)", command=self.rate_popup.destroy, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑 Delete Pin", fg="red", command=lambda: self.delete_pin(site), width=10).pack(
            side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Submit (Enter)", bg="#16a34a", fg="white", width=12,
                  command=lambda: self.submit_rating(site, self.current_rating.get(), self.review_entry.get())).pack(
            side=tk.LEFT, padx=5)

        # Keyboard bindings
        self.rate_popup.bind("<Key-1>", lambda e: [self.current_rating.set(1), self.update_live_preview(site)])
        self.rate_popup.bind("<Key-2>", lambda e: [self.current_rating.set(2), self.update_live_preview(site)])
        self.rate_popup.bind("<Key-3>", lambda e: [self.current_rating.set(3), self.update_live_preview(site)])
        self.rate_popup.bind("<Key-4>", lambda e: [self.current_rating.set(4), self.update_live_preview(site)])
        self.rate_popup.bind("<Key-5>", lambda e: [self.current_rating.set(5), self.update_live_preview(site)])
        self.rate_popup.bind("<Return>",
                             lambda e: self.submit_rating(site, self.current_rating.get(), self.review_entry.get()))
        self.rate_popup.bind("<Escape>", lambda e: self.rate_popup.destroy())

        self.review_entry.focus()

    def update_live_preview(self, site):
        test_stars = [r["stars"] for r in site["reviews"]] + [self.current_rating.get()]
        new_avg = sum(test_stars) / len(test_stars)
        self.preview_label.config(text=f"Preview: New average will be ★ {new_avg:.1f} ({len(test_stars)})")

    def submit_rating(self, site, stars, comment):
        self.save_state_for_undo()
        site["reviews"].append({"stars": stars, "comment": comment.strip()})
        self.save_database(self.campsites)
        self.draw_map()

        new_avg = self.get_average_rating(site["reviews"])
        self.status_label.config(text=f"✓ Rating & Review Saved! {site['name']} is now {new_avg}.")
        self.rate_popup.destroy()

    def delete_pin(self, site_to_delete):
        self.save_state_for_undo()
        self.campsites = [s for s in self.campsites if s["id"] != site_to_delete["id"]]
        self.save_database(self.campsites)
        self.draw_map()
        self.status_label.config(text=f"🗑 Deleted '{site_to_delete['name']}'. Press Undo (Z) to restore.")
        self.rate_popup.destroy()

    # ==========================================
    # MAP NAVIGATION CONTROLS
    # ==========================================
    def zoom_in(self):
        self.map_widget.set_zoom(self.map_widget.zoom + 1)

    def zoom_out(self):
        self.map_widget.set_zoom(self.map_widget.zoom - 1)

    def pan(self, d_lat, d_lng):
        current_pos = self.map_widget.get_position()
        delta = 10 / (2 ** self.map_widget.zoom)
        self.map_widget.set_position(current_pos[0] + (d_lat * delta * 5), current_pos[1] + (d_lng * delta * 10))

    def reset_map(self):
        self.map_widget.set_position(46.6550, -86.1800)
        self.map_widget.set_zoom(11)


if __name__ == "__main__":
    root = tk.Tk()
    app = TrailPinApp(root)
    root.mainloop()