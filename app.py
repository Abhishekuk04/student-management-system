"""
School Management System — Streamlit UI
Rebuilt on top of the original OOP logic (Students / Teacher / persons ABC),
with JSON persistence, input validation, and a clean multi-page interface.
"""

import json
import streamlit as st
from pathlib import Path
from abc import ABC, abstractmethod

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
DATABASE = "school_data.json"

st.set_page_config(
    page_title="School Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# DATA LAYER
# ----------------------------------------------------------------------
def load_data():
    if Path(DATABASE).exists():
        with open(DATABASE, "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    return {"students": [], "teachers": []}


def save_data(data):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


def sort_key(value):
    """Sort roll numbers / employee IDs numerically when possible (so '2'
    comes before '10'), falling back to plain text order otherwise."""
    try:
        return (0, float(value))
    except (TypeError, ValueError):
        return (1, str(value).lower())


def sorted_students():
    return sorted(data["students"], key=lambda s: sort_key(s["roll_no"]))


def sorted_teachers():
    return sorted(data["teachers"], key=lambda t: sort_key(t["emp_id"]))


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


def persist():
    save_data(st.session_state.data)


# ----------------------------------------------------------------------
# DOMAIN CLASSES (kept faithful to the original design)
# ----------------------------------------------------------------------
class Persons(ABC):
    @abstractmethod
    def get_role(self):
        pass

    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email and " " not in email


class Students(Persons):
    def get_role(self):
        return "Student"

    def register(self, name, age, email, roll_no):
        if not name or not roll_no:
            return False, "Name and roll number are required."
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                return False, f"A student with roll number '{roll_no}' already exists."
        data["students"].append({
            "name": name,
            "age": age,
            "email": email,
            "roll_no": roll_no,
            "grades": {},
        })
        persist()
        return True, f"Student '{name}' registered successfully."

    def find(self, roll_no):
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                return s
        return None

    def add_grade(self, roll_no, subject, marks):
        s = self.find(roll_no)
        if not s:
            return False, "Student not found."
        if not subject:
            return False, "Subject cannot be empty."
        s["grades"][subject] = marks
        persist()
        return True, f"Grade added for {s['name']} in {subject}."

    def delete(self, roll_no):
        before = len(data["students"])
        data["students"] = [s for s in data["students"] if s["roll_no"] != roll_no]
        persist()
        return len(data["students"]) < before


class Teacher(Persons):
    def get_role(self):
        return "Teacher"

    def register(self, name, age, email, subject, emp_id):
        if not name or not emp_id:
            return False, "Name and employee ID are required."
        if not Persons.validate_email(email):
            return False, "Invalid email address."
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                return False, f"A teacher with employee ID '{emp_id}' already exists."
        data["teachers"].append({
            "name": name,
            "age": age,
            "email": email,
            "subject": subject,
            "emp_id": emp_id,
        })
        persist()
        return True, f"Teacher '{name}' registered successfully."

    def find(self, emp_id):
        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                return t
        return None

    def delete(self, emp_id):
        before = len(data["teachers"])
        data["teachers"] = [t for t in data["teachers"] if t["emp_id"] != emp_id]
        persist()
        return len(data["teachers"]) < before


stud = Students()
tech = Teacher()

# ----------------------------------------------------------------------
# STYLING — "Chalkboard & Chalk": deep slate-green + warm oat paper,
# amber accent. Colors are forced with !important and color-scheme is
# pinned to light so a dark browser/OS setting can't wash anything out.
# ----------------------------------------------------------------------
INK = "#1F3A34"       # deep slate-green — sidebar, headings, primary buttons
PAGE_BG = "#EFE9DC"   # warm oat page background (not stark white)
CARD = "#FBF8F2"      # soft ivory card — one step lighter than the page
FIELD_BG = "#F3EEE2"  # input fields sit between card and page
AMBER = "#C97C2E"     # accent — active nav, metric rule, primary hover
OLIVE = "#5B7A52"     # success
TERRACOTTA = "#B5502F"  # errors / destructive actions
TEXT = "#20241F"      # near-black warm charcoal
MUTED = "#6E6858"
HAIRLINE = "rgba(31,58,52,0.20)"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@500;600;700&family=Work+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    :root, html {{ color-scheme: light !important; }}

    html, body, [class*="css"], .stApp, .stMarkdown, p, span, div {{
        font-family: 'Work Sans', sans-serif !important;
        color: {TEXT} !important;
    }}
    .stApp {{ background-color: {PAGE_BG} !important; }}

    /* Hide Streamlit's built-in header anchor-link icon for cleaner titles */
    [data-testid="stHeaderActionElements"] {{ display: none !important; }}

    /* Buttons carry their own text color on every descendant — the global
       p/span/div rule above would otherwise paint button labels the same
       dark color as the button background, making them unreadable. */
    .stButton button, .stFormSubmitButton button,
    .stButton button *, .stFormSubmitButton button * {{
        color: #FBF8F2 !important;
        -webkit-text-fill-color: #FBF8F2 !important;
    }}
    .stButton button[kind="secondary"], .stButton button[kind="secondary"] * {{
        color: {TERRACOTTA} !important;
        -webkit-text-fill-color: {TERRACOTTA} !important;
    }}

    h1, h2, h3, h1 *, h2 *, h3 * {{
        font-family: 'Zilla Slab', serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em;
        color: {INK} !important;
        -webkit-text-fill-color: {INK} !important;
        opacity: 1 !important;
    }}
    h1 {{ border-bottom: 2px solid {HAIRLINE}; padding-bottom: 0.5rem; margin-bottom: 1.4rem; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background-color: {INK} !important; }}
    section[data-testid="stSidebar"] * {{ color: #F3EEE2 !important; -webkit-text-fill-color: #F3EEE2 !important; }}
    section[data-testid="stSidebar"] h1 {{ border-bottom: none; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.18); }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        padding: 0.45rem 0.6rem;
        border-radius: 6px;
        transition: background-color 0.15s ease, padding-left 0.15s ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background-color: rgba(201,124,46,0.16);
        padding-left: 0.85rem;
    }}
    section[data-testid="stSidebar"] [aria-checked="true"] {{ color: {AMBER} !important; -webkit-text-fill-color: {AMBER} !important; }}

    /* Form containers → cards */
    div[data-testid="stForm"] {{
        border: 1px solid {HAIRLINE};
        border-radius: 10px;
        padding: 1.6rem 1.8rem;
        background: {CARD} !important;
        box-shadow: 0 1px 0 {HAIRLINE};
    }}

    /* Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] > div,
    div[data-baseweb="input"] input, textarea {{
        background-color: {FIELD_BG} !important;
        border: 1px solid {HAIRLINE} !important;
        color: {TEXT} !important;
        -webkit-text-fill-color: {TEXT} !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within > div {{
        border-color: {AMBER} !important;
        box-shadow: 0 0 0 2px rgba(201,124,46,0.25) !important;
    }}
    div[data-testid="stForm"]:hover {{ box-shadow: 0 2px 10px rgba(31,58,52,0.08); }}
    div[data-testid="stForm"] {{ transition: box-shadow 0.2s ease; }}
    div[data-baseweb="input"] input::placeholder, textarea::placeholder {{
        color: {MUTED} !important;
        -webkit-text-fill-color: {MUTED} !important;
        opacity: 1 !important;
    }}
    label, label * {{ color: {INK} !important; -webkit-text-fill-color: {INK} !important; font-weight: 500; font-size: 0.9rem; }}

    /* Buttons */
    .stButton button, .stFormSubmitButton button {{
        background-color: {INK} !important;
        border: 1px solid {INK};
        border-radius: 8px;
        font-weight: 500;
        padding: 0.55rem 1rem;
        transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
    }}
    .stButton button:hover, .stFormSubmitButton button:hover {{
        background-color: #2E5348 !important;
        border-color: {AMBER};
    }}
    .stButton button:active, .stFormSubmitButton button:active {{
        transform: scale(0.98);
    }}
    .stButton button[kind="secondary"] {{
        background-color: transparent !important;
        border: 1px solid {TERRACOTTA} !important;
    }}
    .stButton button[kind="secondary"]:hover {{
        background-color: {TERRACOTTA} !important;
    }}
    .stButton button[kind="secondary"]:hover * {{
        color: #FBF8F2 !important;
        -webkit-text-fill-color: #FBF8F2 !important;
    }}

    /* Metrics */
    div[data-testid="stMetric"] {{
        background: {CARD} !important;
        border: 1px solid {HAIRLINE};
        border-left: 3px solid {AMBER};
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
    }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {{
        color: {MUTED} !important;
        -webkit-text-fill-color: {MUTED} !important;
        font-family: 'Work Sans', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-size: 0.78rem !important;
    }}
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {{
        color: {INK} !important;
        -webkit-text-fill-color: {INK} !important;
        font-family: 'Zilla Slab', serif !important;
        font-weight: 600 !important;
        font-variant-numeric: tabular-nums;
    }}

    /* HTML tables (st.table) — real DOM elements, so fonts apply cleanly.
       (st.dataframe uses a canvas-based grid that ignores page CSS
       entirely, which is why those tables couldn't be restyled — the
       Grades / Dashboard tables below now use st.table instead.) */
    div[data-testid="stTable"] table {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Work Sans', sans-serif !important;
        border: 1px solid {HAIRLINE};
        border-radius: 8px;
        overflow: hidden;
    }}
    div[data-testid="stTable"] thead th {{
        background: {INK} !important;
        color: #F3EEE2 !important;
        -webkit-text-fill-color: #F3EEE2 !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-size: 0.78rem !important;
        text-align: left !important;
        padding: 0.6rem 0.9rem !important;
        border: none !important;
    }}
    div[data-testid="stTable"] tbody td {{
        background: {CARD} !important;
        color: {TEXT} !important;
        -webkit-text-fill-color: {TEXT} !important;
        font-size: 0.95rem;
        padding: 0.55rem 0.9rem !important;
        border-bottom: 1px solid {HAIRLINE} !important;
        border-left: none !important;
        border-right: none !important;
        border-top: none !important;
    }}
    div[data-testid="stTable"] tbody tr:last-child td {{ border-bottom: none !important; }}
    div[data-testid="stTable"] tbody tr:hover td {{ background: {FIELD_BG} !important; }}
    div[data-testid="stTable"] tbody th {{ display: none; }}

    /* Tables */
    div[data-testid="stDataFrame"] {{ border: 1px solid {HAIRLINE}; border-radius: 8px; overflow: hidden; }}

    /* Alerts */
    div[data-testid="stAlertContentSuccess"], div[data-testid="stAlertContentSuccess"] * {{ color: {OLIVE} !important; -webkit-text-fill-color: {OLIVE} !important; }}
    div[data-testid="stAlertContentError"], div[data-testid="stAlertContentError"] * {{ color: {TERRACOTTA} !important; -webkit-text-fill-color: {TERRACOTTA} !important; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------
st.sidebar.title("🎓 School Manager")
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "🧑‍🎓 Register Student",
        "🧑‍🏫 Register Teacher",
        "📝 Add Grade",
        "🔍 Student Details",
        "🔍 Teacher Details",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption(f"Data file: `{DATABASE}`")
st.sidebar.caption(f"Students: {len(data['students'])} · Teachers: {len(data['teachers'])}")

# ----------------------------------------------------------------------
# PAGE: DASHBOARD
# ----------------------------------------------------------------------
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)
    total_students = len(data["students"])
    total_teachers = len(data["teachers"])
    all_grades = [g for s in data["students"] for g in s["grades"].values()]
    avg_grade = sum(all_grades) / len(all_grades) if all_grades else 0

    col1.metric("Total Students", total_students)
    col2.metric("Total Teachers", total_teachers)
    col3.metric("Overall Average Grade", f"{avg_grade:.1f}" if all_grades else "—")

    st.markdown("### Students")
    if data["students"]:
        rows = []
        for s in sorted_students():
            grades = s["grades"]
            avg = sum(grades.values()) / len(grades) if grades else None
            rows.append({
                "Name": s["name"],
                "Roll No": s["roll_no"],
                "Age": s["age"],
                "Email": s["email"],
                "Subjects Graded": len(grades),
                "Average": round(avg, 1) if avg is not None else "—",
            })
        st.table(rows)
    else:
        st.info("No students registered yet.")

    st.markdown("### Teachers")
    if data["teachers"]:
        rows = [
            {
                "Name": t["name"],
                "Employee ID": t["emp_id"],
                "Subject": t["subject"],
                "Age": t["age"],
                "Email": t["email"],
            }
            for t in sorted_teachers()
        ]
        st.table(rows)
    else:
        st.info("No teachers registered yet.")

# ----------------------------------------------------------------------
# PAGE: REGISTER STUDENT
# ----------------------------------------------------------------------
elif page == "🧑‍🎓 Register Student":
    st.title("🧑‍🎓 Register a Student")

    with st.form("register_student_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2.2, 1, 2, 1.5])
        name = c1.text_input("Full Name", placeholder="e.g. Ananya Sharma")
        age = c2.number_input("Age", min_value=3, max_value=100, step=1, value=15)
        email = c3.text_input("Email", placeholder="name@school.edu")
        roll_no = c4.text_input("Roll Number", placeholder="e.g. 24CS041")
        submitted = st.form_submit_button("Register Student", use_container_width=True)

    if submitted:
        ok, msg = stud.register(name.strip(), int(age), email.strip(), roll_no.strip())
        if ok:
            st.success(msg)
        else:
            st.error(msg)
# ----------------------------------------------------------------------
# PAGE: REGISTER TEACHER
# ----------------------------------------------------------------------
elif page == "🧑‍🏫 Register Teacher":
    st.title("🧑‍🏫 Register a Teacher")

    with st.form("register_teacher_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2.2, 1, 2])
        name = c1.text_input("Full Name", placeholder="e.g. Rohan Verma")
        age = c2.number_input("Age", min_value=18, max_value=100, step=1, value=30)
        email = c3.text_input("Email", placeholder="name@school.edu")
        c4, c5 = st.columns(2)
        subject = c4.text_input("Subject", placeholder="e.g. Mathematics")
        emp_id = c5.text_input("Employee ID", placeholder="e.g. T-1042")
        submitted = st.form_submit_button("Register Teacher", use_container_width=True)

    if submitted:
        ok, msg = tech.register(name.strip(), int(age), email.strip(), subject.strip(), emp_id.strip())
        if ok:
            st.success(msg)
        else:
            st.error(msg)
# ----------------------------------------------------------------------
# PAGE: ADD GRADE
# ----------------------------------------------------------------------
elif page == "📝 Add Grade":
    st.title("📝 Add a Grade")

    if not data["students"]:
        st.info("No students registered yet. Add a student first.")
    else:
        roll_options = {f"{s['name']} ({s['roll_no']})": s["roll_no"] for s in sorted_students()}
        with st.form("add_grade_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            choice = c1.selectbox("Student", list(roll_options.keys()))
            subject = c2.text_input("Subject", placeholder="e.g. Physics")
            marks = c3.number_input("Marks", min_value=0.0, max_value=100.0, step=0.5)
            submitted = st.form_submit_button("Add Grade", use_container_width=True)

        if submitted:
            roll_no = roll_options[choice]
            ok, msg = stud.add_grade(roll_no, subject.strip(), float(marks))
            if ok:
                st.success(msg)
            else:
                st.error(msg)
# ----------------------------------------------------------------------
# PAGE: STUDENT DETAILS
# ----------------------------------------------------------------------
elif page == "🔍 Student Details":
    st.title("🔍 Student Details")

    if not data["students"]:
        st.info("No students registered yet.")
    else:
        roll_options = {f"{s['name']} ({s['roll_no']})": s["roll_no"] for s in sorted_students()}
        choice = st.selectbox("Select a student", list(roll_options.keys()))
        s = stud.find(roll_options[choice])

        if s:
            c1, c2, c3 = st.columns(3)
            c1.metric("Name", s["name"])
            c2.metric("Roll No", s["roll_no"])
            c3.metric("Age", s["age"])
            st.write(f"**Email:** {s['email']}")

            st.markdown("#### Grades")
            if s["grades"]:
                st.table([{"Subject": k, "Marks": v} for k, v in s["grades"].items()])
                avg = sum(s["grades"].values()) / len(s["grades"])
                st.metric("Average", f"{avg:.1f}")
                st.bar_chart({k: v for k, v in s["grades"].items()})
            else:
                st.info("No grades recorded yet.")

            st.markdown("---")
            if st.button("🗑️ Delete this student", type="secondary"):
                stud.delete(s["roll_no"])
                st.success("Student deleted.")
                st.rerun()

# ----------------------------------------------------------------------
# PAGE: TEACHER DETAILS
# ----------------------------------------------------------------------
elif page == "🔍 Teacher Details":
    st.title("🔍 Teacher Details")

    if not data["teachers"]:
        st.info("No teachers registered yet.")
    else:
        emp_options = {f"{t['name']} ({t['emp_id']})": t["emp_id"] for t in sorted_teachers()}
        choice = st.selectbox("Select a teacher", list(emp_options.keys()))
        t = tech.find(emp_options[choice])

        if t:
            c1, c2, c3 = st.columns(3)
            c1.metric("Name", t["name"])
            c2.metric("Employee ID", t["emp_id"])
            c3.metric("Subject", t["subject"])
            st.write(f"**Age:** {t['age']}")
            st.write(f"**Email:** {t['email']}")

            st.markdown("---")
            if st.button("🗑️ Delete this teacher", type="secondary"):
                tech.delete(t["emp_id"])
                st.success("Teacher deleted.")
                st.rerun()