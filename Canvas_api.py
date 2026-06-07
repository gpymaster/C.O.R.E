import requests
import json
from datetime import datetime, timezone
import os
import subprocess


# ====== CONFIG ======
API_KEY = "-----API KEY----"
BASE_URL = "https://acalanes.instructure.com/api/v1"
OUTPUT_FILE = "/Users/graysonkeenan/Desktop/C.O.R.E/canvas_data.json"
DESKTOP_PATH = "/Users/graysonkeenan/Desktop"
HTML_FILE_PATH = os.path.join(DESKTOP_PATH, "TODOlist.html")
PDF_FILE_PATH = os.path.join(DESKTOP_PATH, "TODOlist.pdf")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json+canvas-string-ids"  # Ensures all IDs are returned as strings
}

# Fetch all courses
def get_courses():
    url = f"{BASE_URL}/courses?per_page=100&enrollment_state=active"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Fetch assignments for a course
def get_assignments(course_id):
    url = f"{BASE_URL}/courses/{course_id}/assignments?per_page=100"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# Save Canvas data
def get_canvas_data():
    all_data = {"courses": []}
    today = datetime.now(timezone.utc)

    # Calculate end of week (Sunday)
    days_until_sunday = (6 - today.weekday()) % 7
    if days_until_sunday == 0:
        days_until_sunday = 7
    end_of_week = today.replace(hour=23, minute=59, second=59) + __import__('datetime').timedelta(days=days_until_sunday)

    courses = get_courses()
    for course in courses:
        course_id = course.get("id")
        course_name = course.get("name", "Unnamed Course")

        assignments_raw = get_assignments(course_id)
        assignments_filtered = []

        for a in assignments_raw:
            due_date_str = a.get("due_at")
            has_submitted = a.get("has_submitted_submissions", False)

            # Include assignment if:
            # 1. It's due this week AND not submitted, OR
            # 2. It hasn't been submitted and is due within this week
            include_assignment = False

            if due_date_str:
                due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                # Check if assignment is due this week (from today to end of week)
                if today <= due_date <= end_of_week and not has_submitted:
                    include_assignment = True

            if not include_assignment:
                continue

            assignments_filtered.append({
                "id": a.get("id"),
                "name": a.get("name"),
                "score": a.get("score"),  # assignment score
                "url": a.get("html_url"),
                "max_points": a.get("points_possible"),
                "due_date": due_date_str,
                "date_made": a.get("created_at"),
                "submission_types": a.get("submission_types"),
                "Submited": a.get("has_submitted_submissions", False)
            })

        all_data["courses"].append({
            "id": course_id,
            "name": course_name,
            "assignments": assignments_filtered
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print(f"✅ Data saved to {OUTPUT_FILE}")











