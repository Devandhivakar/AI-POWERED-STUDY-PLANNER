from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Store subjects and topics in a dictionary
subjects_data = {}

@app.route("/")
def index():
    return render_template("index.html", subjects=subjects_data)

@app.route("/add_subject", methods=["POST"])
def add_subject():
    subject = request.form.get("subject")
    topics = request.form.getlist("topics[]")
    difficulty_levels = request.form.getlist("difficulty[]")

    if not subject or not topics or not difficulty_levels:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    # Store topics and difficulty levels for the subject
    subjects_data[subject] = []
    for topic, difficulty in zip(topics, difficulty_levels):
        subjects_data[subject].append({"topic": topic, "difficulty": difficulty})

    return redirect(url_for("index"))

@app.route("/get_study_plan", methods=["POST"])
def get_study_plan():
    data = request.json
    subject = data.get("subject")
    deadline = data.get("deadline")
    study_time = data.get("study_time")

    # Validate input
    if not subject or not deadline or not study_time:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    try:
        # Convert study_time to float
        study_time = float(study_time)

        # Convert deadline to a datetime object
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        current_date = datetime.now()

        # Calculate the number of days until the deadline
        days_until_deadline = (deadline_date - current_date).days

        if days_until_deadline < 0:
            return jsonify({"success": False, "error": "Deadline has already passed"}), 400

        # Generate study advice and schedule
        advice = generate_study_advice(subject, study_time, days_until_deadline)
        schedule = generate_study_schedule(subject, study_time, days_until_deadline)

        return jsonify({
            "success": True,
            "advice": advice,
            "schedule": schedule
        })
    except ValueError as e:
        return jsonify({"success": False, "error": f"Invalid input: {str(e)}"}), 400

def generate_study_advice(subject, study_time, days_until_deadline):
    """
    Generate detailed study advice based on subject, study time, and days until deadline.
    """
    if days_until_deadline == 0:
        return f"<div style='color: white;'>Your deadline for {subject} is today! Focus on quick revision and key concepts.</div>"

    # Calculate daily study time
    daily_study_time = study_time / days_until_deadline

    # Get topics for the subject
    topics = subjects_data.get(subject, [])

    # Sort topics by difficulty (hard -> medium -> easy)
    topics.sort(key=lambda x: {"hard": 0, "medium": 1, "easy": 2}[x["difficulty"]])

    # Generate study plan
    study_plan = (
        f"<div style='color: white;'>"
        f"For the subject '{subject}', you have {days_until_deadline} days until your deadline. "
        f"Allocate approximately {daily_study_time:.1f} hours per day.<br><br>"
        f"<strong>Where to Start</strong>: Begin with the most challenging topics.<br>"
        f"<strong>Topics to Study First</strong>:<br>"
    )

    # Add topics to the study plan
    for i, topic_data in enumerate(topics, 1):
        study_plan += f"{i}. {topic_data['topic']} ({topic_data['difficulty'].capitalize()})<br>"

    # Add study techniques
    study_plan += (
        "<br><strong>How to Study</strong>:<br>"
        "1. <strong>Hard Topics</strong>: Spend more time understanding the theory and solving problems. Break them into smaller subtopics.<br>"
        "2. <strong>Medium Topics</strong>: Focus on understanding concepts and practicing problems. Use flashcards for key terms.<br>"
        "3. <strong>Easy Topics</strong>: Review quickly and focus on memorization. Use summaries and mind maps.<br>"
        "4. <strong>Revise Regularly</strong>: Review your notes and key concepts daily.<br>"
        "5. <strong>Take Breaks</strong>: Study in chunks of 25-30 minutes with 5-minute breaks.<br>"
        "6. <strong>Teach Someone</strong>: Explain concepts to a friend or yourself to reinforce learning.<br>"
        "</div>"
    )

    return study_plan


def generate_study_schedule(subject, study_time, days_until_deadline):
    """
    Generate a daily study schedule for the given subject.
    """
    if days_until_deadline == 0:
        return []

    # Get topics for the subject
    topics = subjects_data.get(subject, [])

    # Sort topics by difficulty (hard -> medium -> easy)
    topics.sort(key=lambda x: {"hard": 0, "medium": 1, "easy": 2}[x["difficulty"]])

    # Calculate daily study time
    daily_study_time = study_time / days_until_deadline

    # Distribute topics across days
    schedule = []
    remaining_study_time = study_time

    for day in range(1, days_until_deadline + 1):
        day_schedule = {
            "day": day,
            "topics": [],
            "study_time": 0
        }

        # Allocate time to the day
        total_day_time = 0

        # Iterate through topics and allocate time
        for topic in topics:
            topic_schedule = {
                "topic": topic["topic"],
                "difficulty": topic["difficulty"],
                "study_time": 0
            }
            if topic["difficulty"] == "hard":
                topic_schedule["study_time"] = daily_study_time * 1.5  # 50% more time for hard topics
            elif topic["difficulty"] == "medium":
                topic_schedule["study_time"] = daily_study_time * 1.2  # 20% more time for medium topics
            else:
                topic_schedule["study_time"] = daily_study_time  # Default time for easy topics

            total_day_time += topic_schedule["study_time"]
            day_schedule["topics"].append(topic_schedule)

            # Remove the topic after adding it to the day's schedule
            topics.remove(topic)

        day_schedule["study_time"] = total_day_time
        schedule.append(day_schedule)

        # Stop if there's no time left to allocate
        if remaining_study_time <= 0:
            break

    return schedule

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
