from llama_text_no_history import *
import time
import json
from Google_calendar import *
from datetime import datetime
from zoneinfo import ZoneInfo



from Canvas_api import *


with open('/Users/graysonkeenan/Desktop/C.O.R.E/Canvas_data.json', "r", encoding="utf-8") as f:
    canvas_data = json.load(f)



def start_notifiction_outburst_function():
    time_now = datetime.now(ZoneInfo("America/Los_Angeles"))
    # Ai prompt for autonomous outward communication decision
    Calendar_data = get_data()
    with open('/Users/graysonkeenan/Desktop/C.O.R.E/Canvas_data.json', "r", encoding="utf-8") as f:
        canvas_data = json.load(f)

    # Create a clean summary of canvas assignments
    canvas_summary = []
    for course in canvas_data.get("courses", []):
        course_name = course.get("name", "Unknown Course")
        for assignment in course.get("assignments", []):
            canvas_summary.append({
                "course": course_name,
                "assignment": assignment.get("name"),
                "due_date": assignment.get("due_date"),
                "submitted": assignment.get("Submited")
            })

    # Save canvas summary to JSON file
    with open('/Users/graysonkeenan/Desktop/C.O.R.E/Canvas_summary.json', 'w', encoding='utf-8') as f:
        json.dump(canvas_summary, f, indent=2)
        print("[Saved canvas summary to Canvas_summary.json]")

    # Format current date and time for the AI to understand
    current_date_str = time_now.strftime("%A, %B %d, %Y")
    current_time_str = time_now.strftime("%I:%M %p")


    prompt = f'''
    You are CORE's autonomous notification system, running silently in the background.

    CONTEXT:
    - The user (Grayson) is NOT currently interacting with you
    - You are in STANDBY mode, monitoring calendar and time data
    - This is a PROACTIVE INTERRUPTION decision - you must evaluate if the data warrants breaking the user's focus
    - The wake word "Jarvis" has NOT been spoken

    YOUR MISSION:
    Analyze the provided data and determine if it's critical enough to proactively speak to the user WITHOUT being prompted.

    INTERRUPTION CRITERIA - Only set talk: true for:
    1. IMMINENT EVENTS: Events happening within the next 30 minutes that require preparation or action
    2. SAME-DAY URGENT REMINDERS: Important events later today that the user may have forgotten (e.g., exam in 3 hours, meeting at 2pm when it's currently 11am)
    3. SAFETY/CRITICAL: Situations affecting wellbeing, safety, or preventing significant negative consequences
    4. EXPLICIT REQUESTS: User previously asked to be notified about this specific type of information

    DO NOT INTERRUPT for:
    - Events more than a day away (unless it's the night before something major)
    - Routine status updates or general observations
    - Information that can wait until the user initiates conversation
    - Events the user is already aware of or adequately prepared for

    TIMING IS CRITICAL:
    - Always calculate the time difference between current time and event time
    - Consider context: An exam in 7 days does NOT warrant interruption today
    - An exam tomorrow morning might warrant a brief reminder the night before
    - A meeting in 15 minutes DOES warrant immediate interruption

    RESPONSE FORMAT (STRICT JSON ONLY - NO OTHER TEXT):
    {{
        "reasoning": "Explain your thought process: time calculations, urgency assessment, and why you chose to interrupt or not",
        "response": "Your concise message to the user (if talk is true, leave empty or 'NONE' if false)",
        "talk": "True or False"
    }}

    CRITICAL: You MUST respond with ONLY valid JSON. No additional text, explanations, or commentary outside the JSON object.

    GOOD INTERRUPTION EXAMPLE:
    Calendar: "PHYSICS exam, 10am today"
    Current Date/Time: Friday, October 31, 2025 at 9:30 AM
    {{
        "reasoning": "Physics exam starts in 30 minutes (10am - 9:30am = 30min). This is imminent and requires immediate preparation. Interruption is warranted.",
        "response": "Sir, your physics exam starts in 30 minutes. Would you like me to prepare any review materials?",
        "talk": "True"
    }}

    BAD INTERRUPTION EXAMPLE:
    Calendar: "PHYSICS exam, Friday October 31st, 10am"
    Current Date/Time: Thursday, October 24, 2025 at 2:00 PM
    {{
        "reasoning": "Physics exam is 7 days away (Oct 31 - Oct 24 = 7 days). This is far too early to interrupt. User has plenty of time to prepare. Will remind closer to the date.",
        "response": "NONE",
        "talk": "False"
    }}

    GOOD NON-INTERRUPTION EXAMPLE:
    Calendar: "Soccer game Saturday 3pm, PHYSICS exam Monday 10am"
    Current Date/Time: Thursday, October 23, 2025 at 8:00 PM
    {{
        "reasoning": "Soccer game is 1.5 days away, exam is 3.5 days away. Neither event is imminent or requires immediate action tonight. No interruption needed at this time.",
        "response": "NONE",
        "talk": "False"
    }}

    KEY REMINDERS:
    - Default to NOT interrupting - silence is often the right choice
    - You will frequently return talk: False - this is expected and correct
    - Respect the user's attention as their most valuable resource
    - When in doubt, don't interrupt
    - Keep responses under 2 sentences if you do interrupt
    - Be natural and conversational, like a helpful assistant tapping on the shoulder
    - responde in english


    DATA TO ANALYZE:
    Calendar: {Calendar_data}
    Canvas(school): {json.dumps(canvas_summary)}
    Current Date: {current_date_str}
    Current Time: {current_time_str}

    Make your decision: Does this information warrant interrupting the user RIGHT NOW?
    ONLY RESPONDE IN JSON FORMAT:
    this is a example:
    {{
        "reasoning": "Soccer game is 1.5 days away, exam is 3.5 days away. Neither event is imminent or requires immediate action tonight. No interruption needed at this time.",
        "response": "NONE",
        "talk": "False"
    }}
    '''

    response = ask_ollama_NH(prompt)
    try:
        # Try to extract JSON from the response (in case there's extra text)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            json_response = json.loads(json_str)
        else:
            json_response = json.loads(response)

        print("\n[Parsed Response]")
        print(json.dumps(json_response, indent=2))

        # Save to Notifiction.json
        with open('/Users/graysonkeenan/Desktop/C.O.R.E/Notifiction.json', 'w', encoding='utf-8') as f:
            json.dump(json_response, f, indent=2)
            print("[Saved to Notifiction.json]")
    except json.JSONDecodeError as e:
            print("\n[Warning: Response was not valid JSON]")
            print(f"Error: {e}")
            print(f"Response: {response}")





start_notifiction_outburst_function()