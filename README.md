# 🏘️ CivicAI — Community Hero

An AI-powered society management and civic issue reporting platform built for the Vibe2Ship Hackathon.

## 🌟 Features
- 🔐 Society sign-in with secretary approval system
- 🚨 Report local issues with photo and video upload
- 🤖 Gemini AI auto-categorizes and prioritizes issues
- 📄 Auto complaint letter generation for authorities
- 🔍 AI-powered resolution step suggestions
- 📋 Issue tracker with Open/In Progress/Resolved status
- 📢 Notice board for society announcements
- 👥 Society directory with staff management
- ⏰ Maintenance timers for park, terrace, water tanker
- 🔍 Lost & Found section
- 🎮 Brain games with points leaderboard
- 💬 AI Chat Assistant powered by Gemini
- 🤖 AI Insights and recommendations

## 🛠️ Tech Stack
- Python + Streamlit
- Gemini API (Google AI Studio)
- Google Maps Embed API
- Google Cloud Run (deployment)

## 🚀 How to Run Locally
1. Clone this repo
2. Install dependencies:
   pip install -r requirements.txt
3. Add your Gemini API key in gemini_helper.py
4. Run the app:
   streamlit run app.py

## 📁 Project Structure
civicai/
├── app.py              ← Main application
├── gemini_helper.py    ← Gemini AI functions
├── data/               ← JSON data storage
├── uploads/            ← User uploaded files
└── requirements.txt    ← Dependencies

## 🔑 Google Technologies Used
- Gemini API — Issue categorization, severity analysis, complaint letters, insights, chat
- Google AI Studio — Build and deployment platform
- Google Cloud Run — Application hosting
- Google Maps Embed API — Location display

## 👩‍💻 Built by
Dipika Gupta— Vibe2Ship Hackathon