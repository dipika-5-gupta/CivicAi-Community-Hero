import streamlit as st
import json
import uuid
import os
from datetime import datetime
from google import genai as google_genai

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="CivicAI - Society Manager",
    page_icon="🏘️",
    layout="wide"
)

# ─── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e, #16213e);
        border-right: 1px solid #00d4ff33;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 8px;
        backdrop-filter: blur(10px);
    }
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0099cc, #006699);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    [data-testid="stMetric"] {
        background: rgba(0, 212, 255, 0.08);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0a0 !important;
    }
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0a0a0 !important;
        border-radius: 8px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d4ff22, #0099cc22) !important;
        color: #00d4ff !important;
    }
    .stAlert {
        border-radius: 10px !important;
        border-left: 4px solid #00d4ff !important;
    }
    hr {
        border-color: rgba(0, 212, 255, 0.2) !important;
    }
    .stRadio > div {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 8px;
    }
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.05);
        border: 1px dashed rgba(0, 212, 255, 0.4);
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,212,255,0.15) !important;
        margin-bottom: 8px;
    }
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1a2e; }
    ::-webkit-scrollbar-thumb { background: #00d4ff44; border-radius: 3px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── File Paths ────────────────────────────────────────────
USERS_FILE         = "data/users.json"
ISSUES_FILE        = "data/issues.json"
NOTICES_FILE       = "data/notices.json"
CONTRIBUTIONS_FILE = "data/contributions.json"
TIMERS_FILE        = "data/timers.json"
GAMES_FILE         = "data/games.json"
LOST_FOUND_FILE    = "data/lost_found.json"

# ─── Helpers ───────────────────────────────────────────────
def load(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        default = [] if "timers" not in path else [
            {"name": "Park Cleaning", "interval_days": 7, "last_done": None},
            {"name": "Terrace Cleaning", "interval_days": 14, "last_done": None},
            {"name": "Water Tanker", "interval_days": 3, "last_done": None}
        ]
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, "r") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def generate_society_code():
    return "SOC-" + str(uuid.uuid4())[:4].upper()

def now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

def get_client():
    from gemini_helper import client
    return client

# ─── Session State ─────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ══════════════════════════════════════════════════════════════
#  AUTH SCREEN
# ══════════════════════════════════════════════════════════════
def auth_screen():
    st.markdown("# 🏘️ CivicAI — Society Manager")
    st.markdown("*Report issues. Stay connected. Build better communities.*")
    st.divider()

    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])

    with tab1:
        st.subheader("Welcome back!")
        phone = st.text_input("Phone Number", placeholder="10-digit mobile number", key="si_phone")
        btn = st.button("Sign In", use_container_width=True, key="si_btn")
        if btn:
            if not phone or len(phone) != 10 or not phone.isdigit():
                st.error("Enter a valid 10-digit phone number.")
            else:
                users = load(USERS_FILE)
                user = next((u for u in users if u["phone"] == phone), None)
                if not user:
                    st.error("No account found. Please create one.")
                elif user["role"] == "member" and user["status"] == "pending":
                    st.warning("⏳ Your request is pending. Secretary hasn't approved yet.")
                elif user["role"] == "member" and user["status"] == "rejected":
                    st.error("❌ Your request was rejected. Contact your secretary.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    st.rerun()

    with tab2:
        st.subheader("Join or create a society")
        role = st.radio("I am a", ["Member (joining existing society)", "Secretary (creating new society)"], key="reg_role")
        name = st.text_input("Full Name", key="reg_name")
        phone2 = st.text_input("Phone Number", placeholder="10-digit", key="reg_phone")

        if "Secretary" in role:
            society_name = st.text_input("Society Name", placeholder="e.g. Green Park Apartments", key="reg_soc")
            society_location = st.text_input("Society Location", placeholder="e.g. Boring Road, Patna", key="reg_loc")
            flat = st.text_input("Your Flat / House Number", key="reg_flat_sec")
        else:
            society_code = st.text_input("Society Code (get from your secretary)", placeholder="e.g. SOC-AB12", key="reg_code")
            flat = st.text_input("Your Flat / House Number", key="reg_flat_mem")

        reg_btn = st.button("Create Account", use_container_width=True, key="reg_btn")

        if reg_btn:
            if not name or not phone2:
                st.error("Please fill all fields.")
            elif len(phone2) != 10 or not phone2.isdigit():
                st.error("Enter valid 10-digit phone number.")
            else:
                users = load(USERS_FILE)
                if any(u["phone"] == phone2 for u in users):
                    st.error("An account with this phone already exists.")
                elif "Secretary" in role:
                    if not society_name or not society_location:
                        st.error("Fill society name and location.")
                    else:
                        code = generate_society_code()
                        new_user = {
                            "id": str(uuid.uuid4())[:8],
                            "name": name,
                            "phone": phone2,
                            "flat": flat,
                            "role": "secretary",
                            "status": "approved",
                            "society_name": society_name,
                            "society_location": society_location,
                            "society_code": code,
                            "joined": now(),
                            "points": 0
                        }
                        users.append(new_user)
                        save(USERS_FILE, users)
                        st.success("✅ Society created! Your Society Code is:")
                        st.code(code)
                        st.info("Share this code with your society members so they can join.")
                        st.session_state.logged_in = True
                        st.session_state.current_user = new_user
                        st.rerun()
                else:
                    users = load(USERS_FILE)
                    secretary = next((u for u in users if u.get("society_code") == society_code and u["role"] == "secretary"), None)
                    if not secretary:
                        st.error("Invalid society code. Check with your secretary.")
                    else:
                        new_user = {
                            "id": str(uuid.uuid4())[:8],
                            "name": name,
                            "phone": phone2,
                            "flat": flat,
                            "role": "member",
                            "status": "pending",
                            "society_code": society_code,
                            "society_name": secretary["society_name"],
                            "society_location": secretary["society_location"],
                            "joined": now(),
                            "points": 0
                        }
                        users.append(new_user)
                        save(USERS_FILE, users)
                        st.success("✅ Request sent! Wait for secretary approval.")

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
def main_app():
    user = st.session_state.current_user
    role = user["role"]

    st.sidebar.markdown(f"### 🏘️ {user['society_name']}")
    st.sidebar.markdown(f"📍 {user['society_location']}")
    st.sidebar.divider()
    st.sidebar.markdown(f"👤 **{user['name']}**")
    st.sidebar.markdown(f"🏠 Flat: {user['flat']}")
    st.sidebar.markdown(f"🎖️ Role: {role.capitalize()}")
    st.sidebar.markdown(f"⭐ Points: {user['points']}")
    st.sidebar.divider()

    pages = [
        "🏠 Home",
        "🚨 Report Issue",
        "📋 Issue Tracker",
        "📢 Notice Board",
        "👥 Society Directory",
        "🤝 Contributions",
        "⏰ Maintenance Timers",
        "🔍 Lost & Found",
        "🎮 Brain Games",
        "🤖 AI Insights",
        "💬 AI Chat Assistant"
    ]
    if role == "secretary":
        pages.append("⚙️ Secretary Panel")

    page = st.sidebar.radio("Navigate", pages)

    if st.sidebar.button("🚪 Sign Out"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    if page == "🏠 Home":                show_home(user)
    elif page == "🚨 Report Issue":       show_report(user)
    elif page == "📋 Issue Tracker":      show_tracker(user, role)
    elif page == "📢 Notice Board":       show_notices(user, role)
    elif page == "👥 Society Directory":  show_directory(user, role)
    elif page == "🤝 Contributions":      show_contributions(user)
    elif page == "⏰ Maintenance Timers": show_timers(user, role)
    elif page == "🔍 Lost & Found":       show_lost_found(user)
    elif page == "🎮 Brain Games":        show_games(user)
    elif page == "🤖 AI Insights":        show_insights()
    elif page == "💬 AI Chat Assistant":  show_ai_chat(user)
    elif page == "⚙️ Secretary Panel":    show_secretary_panel(user)

# ══════════════════════════════════════════════════════════════
#  PAGE: HOME
# ══════════════════════════════════════════════════════════════
def show_home(user):
    st.markdown(f"# 🏘️ Welcome, {user['name']}!")
    st.markdown(f"**Society:** {user['society_name']} &nbsp;|&nbsp; 📍 {user['society_location']}")
    if user["role"] == "secretary":
        st.info(f"🔑 Your Society Code: **{user['society_code']}** — Share this with members to let them join.")
    st.divider()

    issues        = load(ISSUES_FILE)
    notices       = load(NOTICES_FILE)
    contributions = load(CONTRIBUTIONS_FILE)

    soc_issues  = [i for i in issues  if i.get("society_code") == user["society_code"]]
    soc_notices = [n for n in notices if n.get("society_code") == user["society_code"]]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚨 Total Issues",  len(soc_issues))
    col2.metric("🔴 Open Issues",   sum(1 for i in soc_issues if i["status"] == "Open"))
    col3.metric("✅ Resolved",      sum(1 for i in soc_issues if i["status"] == "Resolved"))
    col4.metric("📢 Notices",       len(soc_notices))

    st.divider()
    st.subheader("📢 Latest Notice")
    if soc_notices:
        n = soc_notices[-1]
        st.info(f"**{n['title']}** — {n['date']}\n\n{n['content']}")
    else:
        st.write("No notices yet.")

    st.subheader("🚨 Recent Issues")
    recent = sorted(soc_issues, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
    for i in recent:
        badge = "🔴" if i["severity"] == "High" else ("🟡" if i["severity"] == "Medium" else "🟢")
        st.markdown(f"{badge} **{i['category']}** — {i['location']} — *{i['status']}*")

# ══════════════════════════════════════════════════════════════
#  PAGE: REPORT ISSUE
# ══════════════════════════════════════════════════════════════
def show_report(user):
    from gemini_helper import analyze_issue
    st.header("🚨 Report a Society Issue")
    st.info("Fill in details. Gemini AI will auto-categorize your report.")

    with st.form("report_form"):
        description = st.text_area("Describe the issue *", height=120,
            placeholder="e.g. Large pothole near gate B, very dangerous at night")
        location = st.text_input("Location / Landmark *",
            placeholder="e.g. Near Gate B, Building 3")
        photo = st.file_uploader("Upload Photo (optional)", type=["jpg", "jpeg", "png"])
        video = st.file_uploader("Upload Video (optional)", type=["mp4", "mov", "avi"])
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)

    if submitted:
        if not description or not location:
            st.error("Please fill description and location.")
        else:
            with st.spinner("🤖 Gemini AI is analyzing your report..."):
                try:
                    ai = analyze_issue(description, location)
                    photo_path = None
                    video_path = None

                    if photo:
                        from PIL import Image
                        os.makedirs("uploads/photos", exist_ok=True)
                        photo_path = f"uploads/photos/{uuid.uuid4()}.jpg"
                        Image.open(photo).save(photo_path)

                    if video:
                        os.makedirs("uploads/videos", exist_ok=True)
                        video_path = f"uploads/videos/{uuid.uuid4()}.mp4"
                        with open(video_path, "wb") as vf:
                            vf.write(video.read())

                    issue = {
                        "id": str(uuid.uuid4())[:8],
                        "society_code": user["society_code"],
                        "reported_by": user["name"],
                        "flat": user["flat"],
                        "phone": user["phone"],
                        "description": description,
                        "location": location,
                        "photo": photo_path,
                        "video": video_path,
                        "timestamp": now(),
                        "category": ai["category"],
                        "severity": ai["severity"],
                        "priority_score": ai["priority_score"],
                        "suggested_action": ai["suggested_action"],
                        "estimated_resolution": ai["estimated_resolution"],
                        "upvotes": 0,
                        "status": "Open",
                        "resolved_on": None,
                        "resolved_by": None
                    }
                    issues = load(ISSUES_FILE)
                    issues.append(issue)
                    save(ISSUES_FILE, issues)

                    users = load(USERS_FILE)
                    for u in users:
                        if u["phone"] == user["phone"]:
                            u["points"] = u.get("points", 0) + 10
                    save(USERS_FILE, users)
                    st.session_state.current_user["points"] += 10

                    st.success("✅ Issue reported! You earned 10 points.")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Category", ai["category"])
                    c2.metric("Severity", ai["severity"])
                    c3.metric("Priority", f"{ai['priority_score']}/10")
                    st.info(f"💡 {ai['suggested_action']}")
                    st.info(f"⏱️ Est. Resolution: {ai['estimated_resolution']}")
                except Exception as e:
                    st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════
#  PAGE: ISSUE TRACKER
# ══════════════════════════════════════════════════════════════
def show_tracker(user, role):
    st.header("📋 Issue Tracker")
    issues = load(ISSUES_FILE)
    soc_issues = [i for i in issues if i.get("society_code") == user["society_code"]]

    tab1, tab2 = st.tabs(["🔴 Open Issues", "✅ Resolved History"])

    with tab1:
        open_issues = [i for i in soc_issues if i["status"] != "Resolved"]
        if not open_issues:
            st.success("No open issues! Your society is clean 🎉")
        else:
            col1, col2 = st.columns(2)
            cats = ["All"] + list(set(i["category"] for i in open_issues))
            sevs = ["All", "High", "Medium", "Low"]
            sel_cat = col1.selectbox("Category", cats)
            sel_sev = col2.selectbox("Severity", sevs)

            filtered = sorted(open_issues, key=lambda x: x["upvotes"], reverse=True)
            if sel_cat != "All":
                filtered = [i for i in filtered if i["category"] == sel_cat]
            if sel_sev != "All":
                filtered = [i for i in filtered if i["severity"] == sel_sev]

            for issue in filtered:
                badge = "🔴" if issue["severity"] == "High" else ("🟡" if issue["severity"] == "Medium" else "🟢")
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**#{issue['id']} — {issue['category']}** {badge}")
                        st.markdown(f"📍 {issue['location']} | 🏠 {issue['flat']} | 👤 {issue['reported_by']}")
                        st.markdown(f"🕐 {issue['timestamp']} | Status: **{issue['status']}**")
                        st.markdown(issue['description'])
                        st.caption(f"💡 {issue['suggested_action']} | ⏱️ {issue['estimated_resolution']}")

                        if st.button("🔍 Get Resolution Steps", key=f"res_{issue['id']}"):
                            with st.spinner("Gemini is thinking..."):
                                try:
                                    from gemini_helper import suggest_resolution
                                    steps = suggest_resolution(issue)
                                    st.info(f"**Resolution Plan:**\n\n{steps}")
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        if issue.get("photo") and os.path.exists(issue["photo"]):
                            from PIL import Image
                            st.image(Image.open(issue["photo"]), width=300)
                        if issue.get("video") and os.path.exists(issue["video"]):
                            st.video(issue["video"])
                        map_url = f"https://maps.google.com/maps?q={issue['location'].replace(' ', '+')},+{user['society_location'].replace(' ', '+')}&output=embed"
                        st.components.v1.iframe(map_url, height=200)

                    with c2:
                        st.metric("👍 Upvotes", issue["upvotes"])
                        st.metric("🔥 Priority", f"{issue['priority_score']}/10")

                        if st.button("👍 Upvote", key=f"up_{issue['id']}"):
                            all_issues = load(ISSUES_FILE)
                            for i in all_issues:
                                if i["id"] == issue["id"]:
                                    i["upvotes"] += 1
                            save(ISSUES_FILE, all_issues)
                            st.rerun()

                        if role == "secretary":
                            new_status = st.selectbox("Update Status",
                                ["Open", "In Progress", "Resolved"],
                                key=f"st_{issue['id']}")
                            if st.button("Update", key=f"upd_{issue['id']}"):
                                all_issues = load(ISSUES_FILE)
                                for i in all_issues:
                                    if i["id"] == issue["id"]:
                                        i["status"] = new_status
                                        if new_status == "Resolved":
                                            i["resolved_on"] = now()
                                            i["resolved_by"] = user["name"]
                                            contrib = load(CONTRIBUTIONS_FILE)
                                            contrib.append({
                                                "society_code": user["society_code"],
                                                "issue_id": issue["id"],
                                                "issue_desc": issue["description"][:60],
                                                "resolved_by": user["name"],
                                                "date": now()
                                            })
                                            save(CONTRIBUTIONS_FILE, contrib)
                                save(ISSUES_FILE, all_issues)
                                st.rerun()

                            if st.button("📄 Generate Complaint Letter", key=f"letter_{issue['id']}"):
                                with st.spinner("Gemini is drafting a formal complaint letter..."):
                                    try:
                                        client = get_client()
                                        prompt = f"""
                                        You are a professional society secretary.
                                        Write a formal complaint letter to the Municipal Corporation:
                                        Society Name: {user['society_name']}
                                        Society Location: {user['society_location']}
                                        Secretary Name: {user['name']}
                                        Issue Category: {issue['category']}
                                        Issue Description: {issue['description']}
                                        Issue Location: {issue['location']}
                                        Reported On: {issue['timestamp']}
                                        Severity: {issue['severity']}
                                        Suggested Action: {issue['suggested_action']}
                                        Write a professional formal letter with proper salutation,
                                        clear description, impact on residents, requested action
                                        with timeline, and professional closing. Under 300 words.
                                        """
                                        response = client.models.generate_content(
                                            model="gemini-2.5-flash-lite",
                                            contents=prompt
                                        )
                                        letter = response.text
                                        st.success("✅ Complaint Letter Generated!")
                                        st.markdown("### 📄 Formal Complaint Letter")
                                        st.markdown(letter)
                                        st.download_button(
                                            "⬇️ Download Letter",
                                            letter,
                                            file_name=f"complaint_{issue['id']}.txt",
                                            mime="text/plain"
                                        )
                                    except Exception as e:
                                        st.error(f"Error: {e}")

    with tab2:
        resolved = [i for i in soc_issues if i["status"] == "Resolved"]
        if not resolved:
            st.info("No resolved issues yet.")
        else:
            st.markdown(f"**{len(resolved)} issues resolved so far 🎉**")
            for issue in sorted(resolved, key=lambda x: x.get("resolved_on", ""), reverse=True):
                with st.container(border=True):
                    st.markdown(f"✅ **{issue['category']}** — {issue['location']}")
                    st.markdown(f"Reported by: {issue['reported_by']} | Resolved by: {issue.get('resolved_by', '—')} on {issue.get('resolved_on', '—')}")
                    st.caption(issue['description'])

# ══════════════════════════════════════════════════════════════
#  PAGE: NOTICE BOARD
# ══════════════════════════════════════════════════════════════
def show_notices(user, role):
    st.header("📢 Notice Board")
    notices = load(NOTICES_FILE)
    soc_notices = [n for n in notices if n.get("society_code") == user["society_code"]]

    if role == "secretary":
        with st.expander("➕ Post a New Notice", expanded=False):
            with st.form("notice_form"):
                title    = st.text_input("Notice Title *")
                ntype    = st.selectbox("Type", ["🔵 Info", "🟡 Warning", "🔴 Urgent"])
                content  = st.text_area("Content *", height=100)
                post_btn = st.form_submit_button("📢 Post Notice")
            if post_btn:
                if not title or not content:
                    st.error("Fill all fields.")
                else:
                    notices.append({
                        "society_code": user["society_code"],
                        "id": str(uuid.uuid4())[:8],
                        "title": title,
                        "type": ntype,
                        "content": content,
                        "posted_by": user["name"],
                        "date": now()
                    })
                    save(NOTICES_FILE, notices)
                    st.success("Notice posted!")
                    st.rerun()

    if not soc_notices:
        st.info("No notices yet.")
    else:
        for n in reversed(soc_notices):
            color = "🔵" if "Info" in n["type"] else ("🟡" if "Warning" in n["type"] else "🔴")
            with st.container(border=True):
                st.markdown(f"{color} **{n['title']}**")
                st.markdown(n['content'])
                st.caption(f"Posted by {n['posted_by']} on {n['date']}")

# ══════════════════════════════════════════════════════════════
#  PAGE: SOCIETY DIRECTORY
# ══════════════════════════════════════════════════════════════
def show_directory(user, role):
    st.header("👥 Society Directory")
    users = load(USERS_FILE)
    members = [u for u in users
               if u.get("society_code") == user["society_code"]
               and u["status"] == "approved"]

    search = st.text_input("🔍 Search by name or flat")
    if search:
        members = [m for m in members
                   if search.lower() in m["name"].lower()
                   or search.lower() in m.get("flat", "").lower()]

    secretary = next((m for m in members if m["role"] == "secretary"), None)
    if secretary:
        st.subheader("🔑 Secretary")
        with st.container(border=True):
            st.markdown(f"**{secretary['name']}** | 🏠 {secretary['flat']} | 📞 {secretary['phone']}")

    st.subheader("👥 Members")
    res = [m for m in members if m["role"] == "member"]
    if not res:
        st.info("No approved members yet.")
    else:
        for m in res:
            with st.container(border=True):
                st.markdown(f"**{m['name']}** | 🏠 {m['flat']} | 📞 {m['phone']} | ⭐ {m.get('points', 0)} pts")

    if role == "secretary":
        st.divider()
        st.subheader("➕ Add Staff (Watchman / Milkman etc.)")
        STAFF_FILE = "data/staff.json"
        if not os.path.exists(STAFF_FILE):
            save(STAFF_FILE, [])
        staff = load(STAFF_FILE)
        soc_staff = [s for s in staff if s.get("society_code") == user["society_code"]]

        with st.expander("Add new staff member"):
            with st.form("staff_form"):
                sname  = st.text_input("Name")
                srole  = st.selectbox("Role", ["Watchman", "Milkman", "Newspaper Delivery", "Plumber", "Electrician", "Other"])
                sphone = st.text_input("Phone")
                stime  = st.text_input("Shift / Timing", placeholder="e.g. 6 AM - 2 PM")
                sadd   = st.form_submit_button("Add Staff")
            if sadd:
                staff.append({
                    "society_code": user["society_code"],
                    "name": sname,
                    "role": srole,
                    "phone": sphone,
                    "timing": stime
                })
                save(STAFF_FILE, staff)
                st.success("Staff added!")
                st.rerun()

        if soc_staff:
            st.subheader("🛠️ Society Staff")
            for s in soc_staff:
                with st.container(border=True):
                    st.markdown(f"**{s['name']}** — {s['role']} | 📞 {s['phone']} | 🕐 {s['timing']}")

# ══════════════════════════════════════════════════════════════
#  PAGE: CONTRIBUTIONS
# ══════════════════════════════════════════════════════════════
def show_contributions(user):
    st.header("🤝 Contribution Board")
    contrib = load(CONTRIBUTIONS_FILE)
    soc_contrib = [c for c in contrib if c.get("society_code") == user["society_code"]]

    users = load(USERS_FILE)
    members = [u for u in users if u.get("society_code") == user["society_code"] and u["status"] == "approved"]
    top = sorted(members, key=lambda x: x.get("points", 0), reverse=True)

    st.subheader("🏆 Points Leaderboard")
    for i, m in enumerate(top[:10], 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"{i}."))
        st.markdown(f"{medal} **{m['name']}** — {m['flat']} — ⭐ {m.get('points', 0)} pts")

    st.divider()
    st.subheader("📋 Issue Resolution History")
    if not soc_contrib:
        st.info("No contributions recorded yet.")
    else:
        for c in reversed(soc_contrib):
            with st.container(border=True):
                st.markdown(f"✅ **{c['resolved_by']}** resolved: *{c['issue_desc']}*")
                st.caption(f"Date: {c['date']}")

# ══════════════════════════════════════════════════════════════
#  PAGE: MAINTENANCE TIMERS
# ══════════════════════════════════════════════════════════════
def show_timers(user, role):
    from datetime import datetime, timedelta
    st.header("⏰ Maintenance Timers")
    timers = load(TIMERS_FILE)

    for idx, timer in enumerate(timers):
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### {timer['name']}")
                st.markdown(f"🔄 Every **{timer['interval_days']} days**")
                if timer["last_done"]:
                    last = datetime.strptime(timer["last_done"], "%d %b %Y, %I:%M %p")
                    next_due = last + timedelta(days=timer["interval_days"])
                    days_left = (next_due - datetime.now()).days
                    st.markdown(f"✅ Last done: {timer['last_done']}")
                    if days_left < 0:
                        st.error(f"⚠️ OVERDUE by {abs(days_left)} days!")
                    elif days_left == 0:
                        st.warning("⚠️ Due TODAY!")
                    else:
                        st.success(f"⏳ Next due in {days_left} days")
                else:
                    st.warning("Never done — mark complete when first done.")
            with c2:
                if role == "secretary":
                    if st.button("✅ Mark Done", key=f"timer_{idx}"):
                        timers[idx]["last_done"] = now()
                        save(TIMERS_FILE, timers)
                        st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE: LOST & FOUND
# ══════════════════════════════════════════════════════════════
def show_lost_found(user):
    st.header("🔍 Lost & Found")
    tab1, tab2 = st.tabs(["📋 All Posts", "➕ Post an Item"])

    with tab2:
        with st.form("lf_form"):
            item_type   = st.radio("I want to", ["Report Lost Item", "Report Found Item"])
            item_name   = st.text_input("Item Name *", placeholder="e.g. Black wallet, House keys")
            description = st.text_area("Description", placeholder="More details about the item")
            location    = st.text_input("Where lost/found", placeholder="e.g. Near parking, Lift area")
            photo       = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png"])
            submit      = st.form_submit_button("📤 Post", use_container_width=True)

        if submit:
            if not item_name:
                st.error("Item name is required.")
            else:
                photo_path = None
                if photo:
                    from PIL import Image
                    os.makedirs("uploads/photos", exist_ok=True)
                    photo_path = f"uploads/photos/{uuid.uuid4()}.jpg"
                    Image.open(photo).save(photo_path)
                items = load(LOST_FOUND_FILE)
                items.append({
                    "society_code": user["society_code"],
                    "id": str(uuid.uuid4())[:8],
                    "type": "Lost" if "Lost" in item_type else "Found",
                    "item_name": item_name,
                    "description": description,
                    "location": location,
                    "photo": photo_path,
                    "posted_by": user["name"],
                    "flat": user["flat"],
                    "phone": user["phone"],
                    "date": now(),
                    "status": "Active"
                })
                save(LOST_FOUND_FILE, items)
                st.success("✅ Posted successfully!")
                st.rerun()

    with tab1:
        items = load(LOST_FOUND_FILE)
        soc_items = [i for i in items if i.get("society_code") == user["society_code"] and i["status"] == "Active"]
        if not soc_items:
            st.info("No lost & found posts yet.")
        else:
            lost  = [i for i in soc_items if i["type"] == "Lost"]
            found = [i for i in soc_items if i["type"] == "Found"]
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f"😟 Lost Items ({len(lost)})")
                for item in reversed(lost):
                    with st.container(border=True):
                        st.markdown(f"**{item['item_name']}**")
                        if item.get("description"):
                            st.markdown(item["description"])
                        st.caption(f"📍 {item['location']} | 👤 {item['posted_by']} Flat {item['flat']} | 📞 {item['phone']}")
                        if item.get("photo") and os.path.exists(item["photo"]):
                            from PIL import Image
                            st.image(Image.open(item["photo"]), width=200)
                        if st.button("✅ Mark Resolved", key=f"lf_{item['id']}"):
                            all_items = load(LOST_FOUND_FILE)
                            for i in all_items:
                                if i["id"] == item["id"]:
                                    i["status"] = "Resolved"
                            save(LOST_FOUND_FILE, all_items)
                            st.rerun()

            with col2:
                st.subheader(f"😊 Found Items ({len(found)})")
                for item in reversed(found):
                    with st.container(border=True):
                        st.markdown(f"**{item['item_name']}**")
                        if item.get("description"):
                            st.markdown(item["description"])
                        st.caption(f"📍 {item['location']} | 👤 {item['posted_by']} Flat {item['flat']} | 📞 {item['phone']}")
                        if item.get("photo") and os.path.exists(item["photo"]):
                            from PIL import Image
                            st.image(Image.open(item["photo"]), width=200)
                        if st.button("✅ Mark Resolved", key=f"lf2_{item['id']}"):
                            all_items = load(LOST_FOUND_FILE)
                            for i in all_items:
                                if i["id"] == item["id"]:
                                    i["status"] = "Resolved"
                            save(LOST_FOUND_FILE, all_items)
                            st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE: BRAIN GAMES
# ══════════════════════════════════════════════════════════════
def show_games(user):
    st.header("🎮 Brain Games")
    tab1, tab2, tab3 = st.tabs(["🔢 Sudoku", "🔤 Word Scramble", "📸 Festival Contest"])

    with tab1:
        st.subheader("🔢 Sudoku Puzzle")
        st.info("Fill in the grid so every row, column, and 3×3 box has digits 1–9.")
        puzzle = [
            [5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],
            [4,0,0,8,0,3,0,0,1],
            [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],
            [0,0,0,4,1,9,0,0,5],
            [0,0,0,0,8,0,0,7,9]
        ]
        solution = [
            [5,3,4,6,7,8,9,1,2],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9]
        ]
        if "sudoku_grid" not in st.session_state:
            st.session_state.sudoku_grid = [row[:] for row in puzzle]

        grid = st.session_state.sudoku_grid
        for i in range(9):
            cols = st.columns(9)
            for j in range(9):
                if puzzle[i][j] != 0:
                    cols[j].markdown(f"<div style='text-align:center;font-weight:bold;font-size:18px'>{puzzle[i][j]}</div>", unsafe_allow_html=True)
                else:
                    val = cols[j].text_input(" ", value="" if grid[i][j] == 0 else str(grid[i][j]),
                        key=f"s_{i}_{j}", max_chars=1, label_visibility="collapsed")
                    if val.isdigit():
                        st.session_state.sudoku_grid[i][j] = int(val)

        if st.button("✅ Check Solution"):
            if st.session_state.sudoku_grid == solution:
                st.success("🎉 Correct! You solved it! +50 points")
                users = load(USERS_FILE)
                for u in users:
                    if u["phone"] == user["phone"]:
                        u["points"] = u.get("points", 0) + 50
                save(USERS_FILE, users)
                st.session_state.current_user["points"] += 50
            else:
                st.error("Not quite right. Keep trying!")
        if st.button("🔄 Reset"):
            st.session_state.sudoku_grid = [row[:] for row in puzzle]
            st.rerun()

    with tab2:
        st.subheader("🔤 Word Scramble")
        words = [
            ("COMMUNITY",   "A group of people living together"),
            ("SOCIETY",     "An organized group with common goals"),
            ("CLEANLINESS", "State of being clean"),
            ("FESTIVAL",    "A celebration or holiday"),
            ("NEIGHBOUR",   "Person living next to you")
        ]
        if "word_idx" not in st.session_state:
            st.session_state.word_idx = 0
        if "word_score" not in st.session_state:
            st.session_state.word_score = 0

        idx = st.session_state.word_idx % len(words)
        word, hint = words[idx]
        import random
        scrambled = list(word)
        random.shuffle(scrambled)
        scrambled = "".join(scrambled)

        st.markdown(f"**Hint:** {hint}")
        st.markdown(f"### Scrambled: `{scrambled}`")
        answer = st.text_input("Your answer", key=f"word_{idx}").upper()
        if st.button("Submit Answer"):
            if answer == word:
                st.success(f"🎉 Correct! The word was **{word}** — +20 points!")
                st.session_state.word_score += 20
                st.session_state.word_idx += 1
                users = load(USERS_FILE)
                for u in users:
                    if u["phone"] == user["phone"]:
                        u["points"] = u.get("points", 0) + 20
                save(USERS_FILE, users)
                st.session_state.current_user["points"] += 20
                st.rerun()
            else:
                st.error("Wrong! Try again.")
        st.markdown(f"**Session Score: {st.session_state.word_score} pts**")

    with tab3:
        st.subheader("📸 Festival Photo Contest")
        entries = load(GAMES_FILE)
        soc_entries = [e for e in entries if e.get("society_code") == user["society_code"]]

        with st.form("contest_form"):
            festival = st.text_input("Festival Name", placeholder="e.g. Diwali, Holi, Eid")
            caption  = st.text_input("Caption")
            photo    = st.file_uploader("Upload your festival photo", type=["jpg", "jpeg", "png"])
            post_btn = st.form_submit_button("📤 Submit Entry")

        if post_btn and photo:
            from PIL import Image
            os.makedirs("uploads/photos", exist_ok=True)
            path = f"uploads/photos/{uuid.uuid4()}.jpg"
            Image.open(photo).save(path)
            entries.append({
                "society_code": user["society_code"],
                "id": str(uuid.uuid4())[:8],
                "festival": festival,
                "caption": caption,
                "photo": path,
                "posted_by": user["name"],
                "flat": user["flat"],
                "votes": 0,
                "date": now()
            })
            save(GAMES_FILE, entries)
            st.success("Entry submitted! +10 points")
            users = load(USERS_FILE)
            for u in users:
                if u["phone"] == user["phone"]:
                    u["points"] = u.get("points", 0) + 10
            save(USERS_FILE, users)
            st.session_state.current_user["points"] += 10
            st.rerun()

        if soc_entries:
            st.divider()
            st.subheader("🏆 Contest Entries")
            for e in sorted(soc_entries, key=lambda x: x["votes"], reverse=True):
                with st.container(border=True):
                    from PIL import Image
                    if e.get("photo") and os.path.exists(e["photo"]):
                        st.image(Image.open(e["photo"]), width=300)
                    st.markdown(f"**{e['festival']}** — {e['caption']}")
                    st.caption(f"By {e['posted_by']} | 🗳️ {e['votes']} votes")
                    if st.button(f"👍 Vote", key=f"vote_{e['id']}"):
                        all_entries = load(GAMES_FILE)
                        for entry in all_entries:
                            if entry["id"] == e["id"]:
                                entry["votes"] += 1
                        save(GAMES_FILE, all_entries)
                        st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE: AI INSIGHTS
# ══════════════════════════════════════════════════════════════
def show_insights():
    from gemini_helper import generate_insights
    st.header("🤖 AI Insights")
    st.info("Gemini AI analyzes all your society issues and gives recommendations.")
    issues = load(ISSUES_FILE)
    if st.button("🔍 Generate Insights", use_container_width=True):
        with st.spinner("Gemini is thinking..."):
            result = generate_insights(issues)
            st.success("Done!")
            st.markdown(result)

# ══════════════════════════════════════════════════════════════
#  PAGE: AI CHAT ASSISTANT
# ══════════════════════════════════════════════════════════════
def show_ai_chat(user):
    st.header("💬 AI Chat Assistant")
    st.info("Ask CivicAI anything about your society — issues, notices, maintenance, and more.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    issues        = load(ISSUES_FILE)
    notices       = load(NOTICES_FILE)
    timers        = load(TIMERS_FILE)
    contributions = load(CONTRIBUTIONS_FILE)
    users         = load(USERS_FILE)

    soc_issues  = [i for i in issues  if i.get("society_code") == user["society_code"]]
    soc_notices = [n for n in notices if n.get("society_code") == user["society_code"]]
    soc_members = [u for u in users   if u.get("society_code") == user["society_code"] and u["status"] == "approved"]
    soc_contrib = [c for c in contributions if c.get("society_code") == user["society_code"]]

    open_issues   = [i for i in soc_issues if i["status"] == "Open"]
    resolved      = [i for i in soc_issues if i["status"] == "Resolved"]
    high_severity = [i for i in soc_issues if i["severity"] == "High" and i["status"] == "Open"]

    society_context = f"""
    You are CivicAI, a smart assistant for {user['society_name']} located at {user['society_location']}.
    Current Society Data:
    - Total Members: {len(soc_members)}
    - Total Issues: {len(soc_issues)}
    - Open Issues: {len(open_issues)}
    - Resolved Issues: {len(resolved)}
    - High Severity Issues: {len(high_severity)}
    - Total Notices: {len(soc_notices)}
    Open Issues: {json.dumps(open_issues[:10], indent=2)}
    Recent Notices: {json.dumps(soc_notices[-5:], indent=2)}
    Timers: {json.dumps(timers, indent=2)}
    Instructions:
    - Answer only society related questions
    - Be helpful, friendly and concise
    - Respond in same language as user (Hindi or English)
    - Don't share personal phone numbers
    """

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        col1, col2 = st.columns(2)
        suggestions = [
            "What are the most urgent issues?",
            "How many issues are resolved?",
            "What is the latest notice?",
            "When is the next park cleaning?",
            "How many members are in our society?",
            "Which issues are high severity?"
        ]
        for i, suggestion in enumerate(suggestions):
            col = col1 if i % 2 == 0 else col2
            if col.button(suggestion, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": suggestion})
                with st.spinner("CivicAI is thinking..."):
                    try:
                        client = get_client()
                        response = client.models.generate_content(
                            model="gemini-2.5-flash-lite",
                            contents=society_context + "\n\nUser: " + suggestion + "\nCivicAI:"
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.session_state.chat_history.append({"role": "assistant", "content": f"Sorry, error: {e}"})
                st.rerun()

    user_input = st.chat_input("Ask CivicAI anything about your society...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("CivicAI is thinking..."):
            try:
                client = get_client()
                full_conversation = society_context + "\n\n"
                for msg in st.session_state.chat_history:
                    role_label = "User" if msg["role"] == "user" else "CivicAI"
                    full_conversation += f"{role_label}: {msg['content']}\n"
                full_conversation += "CivicAI:"
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=full_conversation
                )
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "content": f"Sorry, error: {e}"})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

# ══════════════════════════════════════════════════════════════
#  PAGE: SECRETARY PANEL
# ══════════════════════════════════════════════════════════════
def show_secretary_panel(user):
    st.header("⚙️ Secretary Panel")
    users = load(USERS_FILE)
    pending = [u for u in users
               if u.get("society_code") == user["society_code"]
               and u["role"] == "member"
               and u["status"] == "pending"]

    st.subheader(f"⏳ Pending Requests ({len(pending)})")
    if not pending:
        st.success("No pending requests!")
    else:
        for m in pending:
            with st.container(border=True):
                st.markdown(f"**{m['name']}** | 🏠 {m['flat']} | 📞 {m['phone']}")
                st.caption(f"Requested on: {m['joined']}")
                c1, c2 = st.columns(2)
                if c1.button(f"✅ Approve", key=f"app_{m['id']}"):
                    for u in users:
                        if u["id"] == m["id"]:
                            u["status"] = "approved"
                    save(USERS_FILE, users)
                    st.rerun()
                if c2.button(f"❌ Reject", key=f"rej_{m['id']}"):
                    for u in users:
                        if u["id"] == m["id"]:
                            u["status"] = "rejected"
                    save(USERS_FILE, users)
                    st.rerun()

    st.divider()
    st.subheader("👥 All Members")
    approved = [u for u in users
                if u.get("society_code") == user["society_code"]
                and u["status"] == "approved"]
    for m in approved:
        st.markdown(f"{'🔑' if m['role'] == 'secretary' else '👤'} **{m['name']}** | {m['flat']} | {m['phone']} | ⭐ {m.get('points', 0)} pts")

# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
# Auto setup data files
import setup
setup

if not st.session_state.logged_in:
    auth_screen()
else:
    main_app()