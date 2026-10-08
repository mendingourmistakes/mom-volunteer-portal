import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF


def get_gsheets_conn():
    try:
        from streamlit_gsheets import GSheetsConnection
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        pass
    return None

def sync_to_gsheets(sheet_name, df_data):
    conn = get_gsheets_conn()
    if conn:
        try:
            conn.update(worksheet=sheet_name, data=df_data)
            return True, "Successfully synced to Google Sheets!"
        except Exception as e:
            return False, f"Google Sheets Sync Error: {str(e)}"
    return False, "Google Sheets not configured in secrets.toml"

DB_FILE = "mom_volunteers.db"
UPLOAD_DIR = "uploaded_resources"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def clean_pdf_text(text):
    if not text:
        return ""
    text = (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    return text.encode("latin-1", "ignore").decode("latin-1").strip()

def generate_pdf_letter(full_name, username, total_hours, tier, badges):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    pdf.set_fill_color(46, 26, 71)
    pdf.rect(0, 0, 210, 35, "F")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "MENDING OUR MISTAKES, INC.", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 5, "Restoring Families. Rebuilding Stability. Renewing Communities.", ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(46, 26, 71)
    pdf.cell(0, 10, "OFFICIAL SERVICE VERIFICATION & IMPACT LETTER", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(44, 44, 44)

    date_str = pd.Timestamp.now().strftime("%B %d, %Y")
    pdf.cell(0, 8, clean_pdf_text(f"Date: {date_str}"), ln=True)
    record_id = hashlib.md5(username.encode()).hexdigest()[:8].upper()
    pdf.cell(0, 8, clean_pdf_text(f"Volunteer Record ID: MOM-VOL-{record_id}"), ln=True)
    pdf.ln(5)

    clean_name = clean_pdf_text(full_name)
    clean_user = clean_pdf_text(username)
    clean_badge = clean_pdf_text(badges) if badges else "Active Contributor"

    text_body = (
        f"This letter serves as official verification that {clean_name} "
        f"({clean_user}) has actively contributed valuable volunteer service "
        "hours to Mending Our Mistakes, Inc. (M.O.M.) across our integrated "
        "Continuum of Care (CoC) and regional site network in Central Arkansas.\n\n"
        f"Verified Service Credentials:\n - Total Authenticated Service Hours: {total_hours:.1f} Hours\n "
        f"- Approved Security & Clearance Level: Tier {tier}\n - Earned Badges & Distinctions: {clean_badge}\n\n"
        "This service record is officially certified in the M.O.M. Master Operations Database."
    )

    pdf.multi_cell(0, 7, clean_pdf_text(text_body))
    pdf.ln(15)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Certified by:", ln=True)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 6, "Executive Director & Board of Directors", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Mending Our Mistakes, Inc. (d.b.a. The M.O.M. Project)", ln=True)
    pdf.cell(0, 6, "mendingourmistakes.org | Malvern & Traskwood, AR", ln=True)

    return pdf.output()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Volunteer',
            tier INTEGER NOT NULL DEFAULT 1,
            logged_hours REAL DEFAULT 0.0,
            badges TEXT DEFAULT ''
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_code TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Community Outreach & Fundraising',
            site_node TEXT NOT NULL,
            module TEXT NOT NULL,
            tier_required INTEGER NOT NULL,
            time_est REAL NOT NULL DEFAULT 2.0,
            file_path TEXT DEFAULT '',
            file_name TEXT DEFAULT '',
            why_it_matters TEXT NOT NULL,
            instructions TEXT NOT NULL,
            expected_deliverable TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            assigned_volunteer TEXT DEFAULT NULL,
            submission_notes TEXT DEFAULT NULL,
            proof_file_path TEXT DEFAULT '',
            proof_file_name TEXT DEFAULT '',
            completed_date TEXT DEFAULT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS time_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            task_code TEXT NOT NULL,
            task_title TEXT NOT NULL,
            hours_logged REAL NOT NULL,
            work_date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS active_timers (
            username TEXT PRIMARY KEY,
            task_code TEXT NOT NULL,
            start_time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS housing_pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unit_code TEXT NOT NULL,
            site_location TEXT NOT NULL,
            participant_name TEXT NOT NULL,
            construction_status TEXT DEFAULT 'Under Construction',
            monthly_rent REAL DEFAULT 0.0,
            total_credited REAL DEFAULT 0.0,
            purchase_price REAL DEFAULT 150000.0,
            deed_transfer_status TEXT DEFAULT 'In Lease Agreement'
        )
    """)

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_users = [
            ("admin", hash_pass("mom2026"), "Volunteer Coordinator", "admin@mendingourmistakes.org", "Coordinator", 3, 0.0, "🌟 Master Coordinator"),
            ("volunteer1", hash_pass("mom2026"), "Jane Doe", "jane@example.com", "Volunteer", 1, 12.5, "🌱 Active Contributor"),
        ]
        c.executemany("INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours, badges) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", default_users)

    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        sample_tasks = [
            ("FUND-101", "Community Outreach & Donation Requests", "Community Outreach & Fundraising", "Node 1: Dyer St Plaza Hub (Malvern)", "Grants", 1, 2.0, "", "", "Securing community sponsors funds emergency assistance.", "1. Contact 5 local businesses.\n2. Submit confirmation proof.", "List of 5 contacts.", "Open", None, None, "", "", None),
            ("ANN-101", "Legal Readiness Binder Audit", "Civil Legal Navigation", "Node 1: Dyer St Plaza Hub (Malvern)", "ANN", 1, 2.0, "", "", "Organizes binders to prevent warrants.", "1. Review checklist.\n2. Verify tabs 1-5.", "5-Tab Digital Index PDF.", "Open", None, None, "", "", None),
        ]
        c.executemany("INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable, status, assigned_volunteer, submission_notes, proof_file_path, proof_file_name, completed_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", sample_tasks)

    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="M.O.M. Volunteer Portal", page_icon="💜", layout="wide")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    body, .stApp {
        background: linear-gradient(90deg, rgb(245, 239, 230), rgb(232, 221, 208)) !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #1a1a1a !important;
    }
    .mom-header {
        background: #2E1A47;
        padding: 2.2rem 2.2rem;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(46, 26, 71, 0.15);
    }
    .mom-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.2rem;
        color: #ffffff !important;
        margin: 0 0 0.3rem 0;
    }
    .mom-header p {
        color: #d1c4e9;
        margin: 0;
    }
    .task-card {
        background-color: #fffdf1;
        border: 1px solid #e9e5e1;
        border-left: 5px solid #2E1A47;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.02);
    }
    .stButton>button, div.stDownloadButton>button {
        background-color: #2E1A47 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.4rem 1.1rem !important;
    }
    .stButton>button:hover {
        background-color: #7e57c2 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f7f4ec !important;
        border-right: 1px solid #ded8c9 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

st.sidebar.markdown(
    """
<div style="text-align: center; padding-bottom: 1rem;">
    <h2 style="font-family: 'Playfair Display', serif; color: #2E1A47; margin: 0; font-size: 1.3rem;">Mending Our Mistakes</h2>
    <p style="font-size: 0.75rem; color: #7e57c2; font-style: italic;">Parental Restoration Continuum</p>
</div>
""",
    unsafe_allow_html=True,
)

if not st.session_state["logged_in"]:
    st.sidebar.subheader("🔒 Account Sign In")
    login_user = st.sidebar.text_input("Username:")
    login_pass = st.sidebar.text_input("Password:", type="password")

    if st.sidebar.button("Sign In", type="primary"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, username, full_name, email, role, tier, logged_hours, badges FROM users WHERE username=? AND password_hash=?", (login_user.strip(), hash_pass(login_pass)))
        user_row = c.fetchone()
        conn.close()

        if user_row:
            st.session_state["logged_in"] = True
            st.session_state["user"] = {
                "id": user_row[0], "username": user_row[1], "full_name": user_row[2],
                "email": user_row[3], "role": user_row[4], "tier": user_row[5],
                "logged_hours": user_row[6], "badges": user_row[7]
            }
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")
    st.sidebar.info("💡 Default: `admin` / `mom2026` or `volunteer1` / `mom2026`")
else:
    user = st.session_state["user"]
    st.sidebar.markdown(f"**{user['full_name']}** (`{user['role']}`)")
    st.sidebar.markdown(f"**Tier:** `{user['tier']}` | **Hours:** `{user['logged_hours']:.1f} hrs`")
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.rerun()

st.markdown(
    """
<div class="mom-header">
    <h1>Mending Our Mistakes, Inc.</h1>
    <p>Restoring Families. Rebuilding Stability. Renewing Communities.</p>
</div>
""",
    unsafe_allow_html=True,
)

if not st.session_state["logged_in"]:
    st.warning("👈 Please sign in via the sidebar.")
else:
    curr_user = st.session_state["user"]

    nav_options = [
        "📋 Task Marketplace",
        "⏱️ Task Time & Work Timer",
        "📅 Calendar & Daily Pulse",
        "🏠 Build-to-Own Housing",
        "📊 Impact & Grant Match",
        "💡 Support & Suggestions"
    ]
    if curr_user["role"] in ["Coordinator", "Admin"]:
        nav_options.extend(["👥 Onboarding", "🛠️ Coordinator Hub"])

    app_mode = st.radio("Navigation:", nav_options, horizontal=True)

    # 1. CLEAN TASK MARKETPLACE WITH SLIDE-DOWN ACCORDIONS & WORK TIMERS
    if app_mode == "📋 Task Marketplace":
        st.header("📋 Task Marketplace")
        st.caption("Click any task card below to view details, linked documents, and action controls.")

        conn = sqlite3.connect(DB_FILE)
        categories_df = pd.read_sql_query("SELECT DISTINCT category FROM tasks", conn)
        all_cats = ["All Categories"] + categories_df["category"].dropna().tolist()
        sel_cat = st.selectbox("Filter Category:", all_cats)

        cat_sql = "" if sel_cat == "All Categories" else f"AND category = '{sel_cat}'"
        tasks_df = pd.read_sql_query(f"SELECT * FROM tasks WHERE tier_required <= {curr_user['tier']} {cat_sql} AND (status='Open' OR assigned_volunteer='{curr_user['username']}') ORDER BY id DESC", conn)
        conn.close()

        if tasks_df.empty:
            st.info("No active tasks found for your clearance tier.")
        else:
            for _, row in tasks_df.iterrows():
                badge_txt = "🟢 Open Task" if row['status'] == 'Open' else f"🟡 Assigned to You ({row['status']})"
                
                conn = sqlite3.connect(DB_FILE)
                t_check = conn.execute("SELECT status FROM active_timers WHERE username=? AND task_code=?", (curr_user['username'], row['task_code'])).fetchone()
                conn.close()
                timer_state = t_check[0] if t_check else "Stopped"

                with st.expander(f"[{row['task_code']}] {row['title']} ({badge_txt} | {row['time_est']} hrs)"):
                    st.markdown(f"**Category:** {row['category']} | **Site Node:** {row['site_node']}")
                    st.markdown(f"**Why It Matters:** {row['why_it_matters']}")
                    
                    st.markdown("---")
                    st.markdown(f"**Instructions:**\n{row['instructions']}")
                    st.markdown(f"**Expected Deliverable:**\n{row['expected_deliverable']}")

                    if row['file_path'] and os.path.exists(row['file_path']):
                        with open(row['file_path'], "rb") as fp:
                            st.download_button(f"📥 Download Reference File ({row['file_name']})", data=fp.read(), file_name=row['file_name'], key=f"dl_{row['id']}")

                    st.markdown("---")
                    
                    c1, c2, c3 = st.columns(3)
                    
                    if row['status'] == 'Open':
                        if c1.button("🙋 Claim Task", key=f"claim_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            conn.execute("UPDATE tasks SET status='Claimed / In Progress', assigned_volunteer=? WHERE id=?", (curr_user['username'], row['id']))
                            conn.commit()
                            conn.close()
                            st.success("Task claimed!")
                            st.rerun()
                    elif row['assigned_volunteer'] == curr_user['username']:
                        if c1.button("↩️ Release Task", key=f"rel_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            conn.execute("UPDATE tasks SET status='Open', assigned_volunteer=NULL, submission_notes=NULL WHERE id=?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.warning("Task released.")
                            st.rerun()

                        st.markdown(f"**Work Timer Status:** `{timer_state}`")
                        tc1, tc2, tc3 = st.columns(3)
                        if timer_state != "Running":
                            if tc1.button("▶️ Start Work", key=f"start_{row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                conn.execute("INSERT OR REPLACE INTO active_timers (username, task_code, start_time, status) VALUES (?, ?, datetime('now'), 'Running')", (curr_user['username'], row['task_code']))
                                conn.commit()
                                conn.close()
                                st.rerun()
                        else:
                            if tc1.button("⏸️ Pause Work", key=f"pause_{row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                conn.execute("UPDATE active_timers SET status='Paused' WHERE username=? AND task_code=?", (curr_user['username'], row['task_code']))
                                conn.commit()
                                conn.close()
                                st.rerun()

                        if timer_state in ["Running", "Paused"]:
                            if tc2.button("⏹️ Stop & Log Hours", key=f"stop_{row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                conn.execute("DELETE FROM active_timers WHERE username=? AND task_code=?", (curr_user['username'], row['task_code']))
                                conn.commit()
                                conn.close()
                                st.success("Timer stopped. Hours ready for submission.")

                        with st.form(key=f"sub_{row['id']}"):
                            s_notes = st.text_area("Submission Notes / Deliverable Summary:", value=row['submission_notes'] if row['submission_notes'] else "")
                            if st.form_submit_button("🚀 Submit Task"):
                                conn = sqlite3.connect(DB_FILE)
                                conn.execute("UPDATE tasks SET status='Submitted / Under Review', submission_notes=? WHERE id=?", (s_notes, row['id']))
                                conn.commit()
                                conn.close()
                                st.success("Submitted for review!")
                                st.rerun()

    # 2. TASK TIME & WORK TIMER
    elif app_mode == "⏱️ Task Time & Work Timer":
        st.header("⏱️ Task Time Logging & Activity")
        conn = sqlite3.connect(DB_FILE)
        tasks_list = pd.read_sql_query("SELECT task_code, title FROM tasks", conn)
        conn.close()

        with st.form("time_log"):
            t_code = st.selectbox("Task Code:", tasks_list['task_code'].tolist() if not tasks_list.empty else ["GEN-001"])
            hrs = st.number_input("Hours Worked:", min_value=0.25, max_value=12.0, value=2.0, step=0.25)
            w_date = st.date_input("Date Performed:")
            notes = st.text_area("Work Performed Notes:")
            if st.form_submit_button("Log Time Entry"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO time_logs (username, task_code, task_title, hours_logged, work_date, notes) VALUES (?, ?, ?, ?, ?, ?)", 
                             (curr_user['username'], t_code, "Task Work", hrs, str(w_date), notes))
                conn.execute("UPDATE users SET logged_hours = logged_hours + ? WHERE username=?", (hrs, curr_user['username']))
                conn.execute("UPDATE tasks SET status='Approved & Completed', completed_date=? WHERE task_code=?", (str(w_date), t_code))
                conn.commit()
                conn.close()
                st.success("Time logged successfully!")
                st.rerun()

        st.subheader("Your Time Logs")
        conn = sqlite3.connect(DB_FILE)
        st.dataframe(pd.read_sql_query("SELECT task_code, hours_logged, work_date, notes FROM time_logs WHERE username=?", conn, params=(curr_user['username'],)), use_container_width=True)
        conn.close()

    # 3. CALENDAR & DAILY PULSE
    elif app_mode == "📅 Calendar & Daily Pulse":
        st.header("📅 Calendar & Daily Organization Pulse")
        t1, t2 = st.tabs(["🗓️ My Completed Tasks", "👥 Organization Daily Pulse"])
        
        with t1:
            conn = sqlite3.connect(DB_FILE)
            st.dataframe(pd.read_sql_query("SELECT task_code, title, time_est, completed_date FROM tasks WHERE assigned_volunteer=? AND status='Approved & Completed'", conn, params=(curr_user['username'],)), use_container_width=True)
            conn.close()
            
        with t2:
            conn = sqlite3.connect(DB_FILE)
            logs = pd.read_sql_query("SELECT username, task_code, hours_logged, work_date, notes FROM time_logs ORDER BY work_date DESC", conn)
            conn.close()
            if logs.empty:
                st.info("No logs found.")
            else:
                sel_date = st.selectbox("Select Date:", logs['work_date'].unique().tolist())
                day_logs = logs[logs['work_date'] == sel_date]
                st.metric("Total Hours on Date", f"{day_logs['hours_logged'].sum():.1f} hrs")
                for _, l in day_logs.iterrows():
                    st.info(f"👤 @{l['username']} completed [{l['task_code']}] ({l['hours_logged']} hrs)\n\n> {l['notes']}")

    # 4. BUILD-TO-OWN HOUSING PIPELINE
    elif app_mode == "🏠 Build-to-Own Housing":
        st.header("🏠 Build-to-Own Housing Pipeline")
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM housing_pipeline", conn)
        conn.close()
        for _, h in df.iterrows():
            st.markdown(f"""
            <div class="task-card">
                <span class="mom-badge-pill">{h['unit_code']} | {h['construction_status']}</span>
                <h3>Participant: {h['participant_name']}</h3>
                <p>📍 {h['site_location']} | 💰 Rent: ${h['monthly_rent']:,.2f} \vert{} Credited:${h['total_credited']:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)

    # 5. IMPACT & GRANT MATCH
    elif app_mode == "📊 Impact & Grant Match":
        st.header("📊 Federal Grant Match Calculator")
        conn = sqlite3.connect(DB_FILE)
        total_hrs = conn.execute("SELECT SUM(logged_hours) FROM users").fetchone()[0] or 0.0
        conn.close()
        rate = 33.49
        st.metric("Total Volunteer Hours", f"{total_hrs:.1f} hrs")
        st.metric("Independent Sector Match Value", f"${total_hrs * rate:,.2f} (@ $33.49/hr)")

    # 6. SUPPORT & SUGGESTIONS
    elif app_mode == "💡 Support & Suggestions":
        st.header("💡 Support Center")
        with st.form("supp"):
            subj = st.text_input("Subject / Task Code:")
            msg = st.text_area("Describe your question or issue:")
            if st.form_submit_button("Submit Ticket"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO support_tickets (volunteer, subject, message) VALUES (?, ?, ?)", (curr_user['username'], subj, msg))
                conn.commit()
                conn.close()
                st.success("Support ticket submitted!")
                st.rerun()

    # 7. ONBOARDING & COORDINATOR HUB
    elif app_mode == "👥 Onboarding" and curr_user['role'] in ["Coordinator", "Admin"]:
        st.header("👥 Volunteer Onboarding")
        with st.form("ob"):
            u = st.text_input("Username:")
            p = st.text_input("Password:", type="password", value="mom2026")
            fn = st.text_input("Full Name:")
            em = st.text_input("Email:")
            if st.form_submit_button("Create User"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours) VALUES (?, ?, ?, ?, 'Volunteer', 1, 0.0)", (u, hash_pass(p), fn, em))
                conn.commit()
                conn.close()
                st.success("User created!")

    elif app_mode == "🛠️ Coordinator Hub" and curr_user['role'] in ["Coordinator", "Admin"]:
        st.header("🛠️ Coordinator Command Center")
        with st.form("new_t"):
            tc = st.text_input("Task Code (e.g., FUND-102):")
            tt = st.text_input("Title:")
            tcateg = st.selectbox("Category:", ["Community Outreach & Fundraising", "Civil Legal Navigation", "Heritage Trade & Logistics"])
            t_hrs = st.number_input("Est Hours:", value=2.0)
            t_why = st.text_area("Why This Matters:")
            t_inst = st.text_area("Instructions:")
            t_del = st.text_area("Expected Deliverable:")
            if st.form_submit_button("Publish Task"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable) VALUES (?, ?, ?, 'Node 1 Plaza Hub', 'Admin', 1, ?, ?, ?, ?)", 
                             (tc, tt, tcateg, t_hrs, t_why, t_inst, t_del))
                conn.commit()
                conn.close()
                st.success("Task published to marketplace!")
                st.rerun()
