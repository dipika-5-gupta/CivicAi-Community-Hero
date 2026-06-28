from google import genai
import json

try:
    import streamlit as st
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = "YOUR_API_KEY_HERE"

client = genai.Client(api_key=API_KEY)

def analyze_issue(description, location):
    prompt = f"""
    You are a civic issue analyst for an Indian society/community.
    A resident has reported this problem:
    Description: "{description}"
    Location: "{location}"

    Respond ONLY in this exact JSON format, nothing else:
    {{
        "category": "one of: Pothole, Water Leakage, Broken Streetlight, Waste Management, Electrical Issue, Security Issue, Other",
        "severity": "one of: Low, Medium, High",
        "priority_score": a number from 1 to 10,
        "suggested_action": "one specific action the society should take",
        "estimated_resolution": "estimated time like: 1-2 days, 1 week, 2-3 weeks"
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def generate_insights(issues):
    if not issues:
        return "No issues reported yet."
    summary = json.dumps(issues[:20], indent=2)
    prompt = f"""
    You are a civic data analyst for a housing society.
    Here are recent community issues:
    {summary}
    Give a brief analysis in plain text (no JSON) with:
    1. Top 3 most urgent issues right now
    2. Most common problem type
    3. One recommendation for the society secretary
    Keep it under 150 words.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text


def suggest_resolution(issue):
    prompt = f"""
    You are a society management expert.
    Issue Category: {issue['category']}
    Description: {issue['description']}
    Location: {issue['location']}
    Severity: {issue['severity']}

    Give exactly 3 step-by-step resolution suggestions:
    Step 1: [action]
    Step 2: [action]
    Step 3: [action]
    Mention who is responsible. Under 100 words.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text