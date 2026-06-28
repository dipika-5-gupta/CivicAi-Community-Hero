import json
import os

# Create directories
os.makedirs("data", exist_ok=True)
os.makedirs("uploads/photos", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# Create empty JSON files if they don't exist
files = {
    "data/users.json": [],
    "data/issues.json": [],
    "data/notices.json": [],
    "data/contributions.json": [],
    "data/games.json": [],
    "data/lost_found.json": [],
    "data/staff.json": [],
    "data/timers.json": [
        {"name": "Park Cleaning", "interval_days": 7, "last_done": None},
        {"name": "Terrace Cleaning", "interval_days": 14, "last_done": None},
        {"name": "Water Tanker", "interval_days": 3, "last_done": None}
    ]
}

for path, default in files.items():
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
        print(f"Created {path}")
    else:
        print(f"Already exists: {path}")