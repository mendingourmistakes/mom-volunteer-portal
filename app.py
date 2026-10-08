import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF


# --- GOOGLE SHEETS SYNC MODULE ---
def get_gsheets_conn():
    """Attempt to get Streamlit Google Sheets Connection if secrets are configured."""
    try:
        from streamlit_gsheets import GSheetsConnection
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        pass
    return None

def sync_to_gsheets(sheet_name, df_data):
    """Sync a pandas DataFrame to a named worksheet in Google Sheets if connected."""
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

    # Header Banner (Dark Royal Purple #2E1A47)
    pdf.set_fill_color(46, 26, 71)
    pdf.rect(0, 0, 210, 35, "F")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "MENDING OUR MISTAKES, INC.", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(
        0,
        5,
        "Restoring Families. Rebuilding Stability. Renewing Communities.",
        ln=True,
        align="C",
    )
    pdf.ln(15)

    # Title
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(46, 26, 71)
    pdf.cell(
        0, 10, "OFFICIAL SERVICE VERIFICATION & IMPACT LETTER", ln=True, align="C"
    )
    pdf.ln(5)

    # Body
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(44, 44, 44)

    date_str = pd.Timestamp.now().strftime("%B %d, %Y")
    pdf.cell(0, 8, clean_pdf_text(f"Date: {date_str}"), ln=True)
    record_id = hashlib.md5(username.encode()).hexdigest()[:8].upper()
    pdf.cell(
        0,
        8,
        clean_pdf_text(f"Volunteer Record ID: MOM-VOL-{record_id}"),
        ln=True,
    )
    pdf.ln(5)

    clean_name = clean_pdf_text(full_name)
    clean_user = clean_pdf_text(username)
    clean_badge = clean_pdf_text(badges) if badges else "Active Contributor"

    text_body = (
        f"This letter serves as official verification that {clean_name}"
        f" ({clean_user}) has actively contributed valuable volunteer service"
        " hours to Mending Our Mistakes, Inc. (M.O.M.) across our integrated"
        " Continuum of Care (CoC) and regional site network in Central"
        " Arkansas.\n\nVerified Service Credentials:\n -"
        f" Total Authenticated Service Hours: {total_hours:.1f} Hours\n -"
        f" Approved Security & Clearance Level: Tier {tier}\n -"
        f" Earned Badges & Distinctions: {clean_badge}\n\nThrough these"
        f" dedicated service efforts, {clean_name} has directly supported our"
        " core mission of reunifying court-involved parents, delivering civil"
        " legal navigation, managing heritage trade salvage, and expanding"
        " family stabilization services.\n\nThis service record is officially"
        " certified in the M.O.M. Master Operations Database and is valid for"
        " academic service credits, court compliance reporting, professional"
        " portfolios, and community honors."
    )

    pdf.multi_cell(0, 7, clean_pdf_text(text_body))
    pdf.ln(15)

    # Signature Block
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Certified by:", ln=True)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 6, "Executive Director & Board of Directors", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0, 6, "Mending Our Mistakes, Inc. (d.b.a. The M.O.M. Project)", ln=True
    )
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

    c.execute("""
        CREATE TABLE IF NOT EXISTS kudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General Discussion',
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS discussion_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer TEXT NOT NULL,
            subject TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General Inquiry',
            message TEXT NOT NULL,
            status TEXT DEFAULT 'Open / Pending',
            response TEXT DEFAULT '',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General Suggestion',
            suggestion TEXT NOT NULL,
            status TEXT DEFAULT 'Under Review',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            category TEXT DEFAULT 'General Announcement'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            time_str TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            option_chosen TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed Default Users
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        default_users = [
            (
                "admin",
                hash_pass("mom2026"),
                "Volunteer Coordinator",
                "admin@mendingourmistakes.org",
                "Coordinator",
                3,
                0.0,
                "🌟 Master Coordinator",
            ),
            (
                "onboarder",
                hash_pass("mom2026"),
                "Onboarding Specialist",
                "onboarder@mendingourmistakes.org",
                "Coordinator",
                3,
                0.0,
                "📋 Onboarding Lead",
            ),
            (
                "volunteer1",
                hash_pass("mom2026"),
                "Jane Doe",
                "jane@example.com",
                "Volunteer",
                1,
                12.5,
                "🌱 Active Contributor | 🏅 10+ Hour Bronze",
            ),
        ]
        c.executemany(
            """
            INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours, badges)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            default_users,
        )

    # Seed Housing Pipeline
    c.execute("SELECT COUNT(*) FROM housing_pipeline")
    if c.fetchone()[0] == 0:
        sample_housing = [
            ("SABS-UNIT-01", "Node 1: Dyer St Plaza Hub (Malvern)", "Family Integration Test Case A", "Completed / Occupied", 750.0, 9000.0, 145000.0, "Lease-to-Own Active"),
            ("SABS-UNIT-02", "Node 2: Chandler Rd Campus (Traskwood)", "Pending Apprentice Assignment", "Under Construction", 0.0, 0.0, 150000.0, "Pre-Lease Phase"),
        ]
        c.executemany("""
            INSERT INTO housing_pipeline (unit_code, site_location, participant_name, construction_status, monthly_rent, total_credited, purchase_price, deed_transfer_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_housing)

    conn.commit()
    conn.close()


init_db()

st.set_page_config(
    page_title="Mending Our Mistakes, Inc. — Volunteer Portal",
    page_icon="💜",
    layout="wide",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    body, .stApp {
        background: linear-gradient(90deg, rgb(245, 239, 230), rgb(232, 221, 208)) !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #1a1a1a !important;
    }

    .font-display {
        font-family: 'Playfair Display', serif !important;
    }

    .mom-header {
        background: #2E1A47;
        padding: 2.5rem 2.5rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px rgba(46, 26, 71, 0.2);
    }

    .mom-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff !important;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
    }

    .mom-header p {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.05rem;
        color: #d1c4e9;
        margin: 0;
    }

    .mom-badge-pill {
        background-color: #7e57c2;
        color: #ffffff;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 9999px;
        display: inline-block;
        margin-bottom: 0.8rem;
    }

    h1, h2, h3, .stHeader {
        font-family: 'Playfair Display', serif !important;
        color: #2E1A47 !important;
    }

    .task-card {
        background-color: #fffdf1;
        border: 1px solid #e9e5e1;
        border-left: 6px solid #2E1A47;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        transition: all 0.2s ease-in-out;
    }

    .stButton>button, div.stDownloadButton>button {
        background-color: #2E1A47 !important;
        color: #ffffff !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.5rem 1.25rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .stButton>button:hover, div.stDownloadButton>button:hover {
        background-color: #7e57c2 !important;
        transform: translateY(-2px);
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
    <h2 style="font-family: 'Playfair Display', serif; color: #2E1A47; margin: 0; font-size: 1.4rem;">Mending Our Mistakes</h2>
    <p style="font-size: 0.8rem; color: #7e57c2; font-style: italic;">A Parental Restoration Continuum</p>
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
        c.execute(
            "SELECT id, username, full_name, email, role, tier, logged_hours,"
            " badges FROM users WHERE username=? AND password_hash=?",
            (login_user.strip(), hash_pass(login_pass)),
        )
        user_row = c.fetchone()
        conn.close()

        if user_row:
            st.session_state["logged_in"] = True
            st.session_state["user"] = {
                "id": user_row[0],
                "username": user_row[1],
                "full_name": user_row[2],
                "email": user_row[3],
                "role": user_row[4],
                "tier": user_row[5],
                "logged_hours": user_row[6],
                "badges": user_row[7],
            }
            st.sidebar.success(f"Welcome back, {user_row[2]}!")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")

    st.sidebar.info(
        "💡 Default Logins:\n- Coordinator: `admin` / `mom2026`\n- Volunteer:"
        " `volunteer1` / `mom2026`"
    )

else:
    user = st.session_state["user"]
    st.sidebar.markdown(f"### 👤 Logged in as:\n**{user['full_name']}**")
    st.sidebar.markdown(f"**Role:** `{user['role']}`")
    st.sidebar.markdown(f"**Approved Tier:** `Tier {user['tier']}`")
    st.sidebar.markdown(f"**Logged Hours:** `{user['logged_hours']:.1f} hrs`")
    st.sidebar.markdown(
        f"**Badges:** {user['badges'] or '🌱 Active Contributor'}"
    )

    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.rerun()

st.markdown(
    """
<div class="mom-header">
    <span class="mom-badge-pill">Official Operations & Volunteer Portal</span>
    <h1>Mending Our Mistakes, Inc.</h1>
    <p>Restoring Families. Rebuilding Stability. Renewing Communities.</p>
</div>
""",
    unsafe_allow_html=True,
)

if not st.session_state["logged_in"]:
    st.warning(
        "👈 Please sign in using the sidebar to access your volunteer workspace."
    )
    st.markdown("""
    ### Welcome to the M.O.M. Volunteer Network!
    Our portal provides secure, tiered access to task cards, resource documents, micro-training, community discussions, and service hour certification.
    """)

else:
    curr_user = st.session_state["user"]

    nav_options = [
        "📋 Volunteer Task Marketplace",
        "⏱️ Task Time Logging & Activity",
        "📅 Calendar & Completion Views",
        "🏠 Build-to-Own Housing Pipeline",
        "📊 Live Impact & Grant Match",
        "💬 Direct Messaging",
        "🗣️ Community Discussion Board",
        "🎓 Training & Tier Upgrade",
        "🌟 Community Kudos & Leaderboard",
        "💡 Suggestion Box & Support Center",
    ]
    if curr_user["role"] in ["Coordinator", "Admin"]:
        nav_options.extend(["👥 Volunteer Onboarding", "🛠️ Coordinator Command Center"])

    app_mode = st.radio("Portal View:", nav_options, horizontal=True)

    # 1. VOLUNTEER TASK MARKETPLACE
    if app_mode == "📋 Volunteer Task Marketplace":
        st.header(f"👋 Welcome, {curr_user['full_name']}!")

        col_prof1, col_prof2 = st.columns(2)
        with col_prof1:
            c_p1, c_p2, c_p3 = st.columns(3)
            c_p1.metric("Clearance Tier", f"Tier {curr_user['tier']}")
            c_p2.metric("Service Hours", f"{curr_user['logged_hours']:.1f} Hours")
            badge_display = curr_user["badges"] if curr_user["badges"] else "🌱 Active"
            c_p3.metric("Badges Earned", badge_display)
        with col_prof2:
            pdf_bytes = generate_pdf_letter(
                curr_user["full_name"],
                curr_user["username"],
                curr_user["logged_hours"],
                curr_user["tier"],
                curr_user["badges"],
            )
            st.download_button(
                label="📄 Download Official Service Letter (PDF)",
                data=bytes(pdf_bytes),
                file_name=f"MOM_Service_Verification_{curr_user['username']}.pdf",
                mime="application/pdf",
            )

        st.write("---")
        st.subheader("📋 Volunteer Task Marketplace")
        st.caption("Browse tasks approved for your clearance tier. Claim tasks, manage active commitments, or log your hours.")

        conn = sqlite3.connect(DB_FILE)
        categories_df = pd.read_sql_query("SELECT DISTINCT category FROM tasks", conn)
        all_categories = ["All Categories"] + categories_df["category"].dropna().tolist()
        selected_cat = st.selectbox("🔍 Filter Tasks by Functional Category:", all_categories)

        cat_filter_sql = "" if selected_cat == "All Categories" else f"AND category = '{selected_cat}'"
        
        query = f"""
            SELECT * FROM tasks 
            WHERE tier_required <= {curr_user['tier']} 
            {cat_filter_sql}
            AND (status = 'Open' OR assigned_volunteer = '{curr_user['username']}')
            ORDER BY id DESC
        """
        df_tasks = pd.read_sql_query(query, conn)
        conn.close()

        if df_tasks.empty:
            st.info("No tasks currently available matching your selected filters.")
        else:
            for idx, row in df_tasks.iterrows():
                with st.container():
                    status_badge = "🟢 OPEN TASK" if row['status'] == 'Open' else f"🟡 YOUR TASK ({row['status']})"
                    st.markdown(
                        f"""
                        <div class="task-card">
                            <span class="mom-badge-pill">{status_badge} | Tier {row['tier_required']} | {row['time_est']} Hours</span>
                            <h3 style="margin-top: 0.4rem; color: #2E1A47; font-family: 'Playfair Display', serif;">[{row['task_code']}] {row['title']}</h3>
                            <p><strong>📂 Category:</strong> {row['category']} | <strong>📍 Site Node:</strong> {row['site_node']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"#### 💡 Why This Matters\n{row['why_it_matters']}")

                    with st.expander("📌 View Instructions & Deliverables"):
                        st.markdown(f"**Step-by-Step Instructions:**\n{row['instructions']}")
                        st.markdown(f"**Expected Deliverable:**\n{row['expected_deliverable']}")

                    if row['status'] == 'Open':
                        if st.button(f"🙋 Claim This Task ({row['task_code']})", key=f"claim_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute(
                                "UPDATE tasks SET status='Claimed / In Progress', assigned_volunteer=? WHERE id=?",
                                (curr_user["username"], row["id"])
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Task {row['task_code']} claimed!")
                            st.rerun()

                    elif row['assigned_volunteer'] == curr_user['username']:
                        st.info(f"📌 Status: **{row['status']}**")
                        
                        col_rel1, col_rel2 = st.columns([1, 2])
                        with col_rel1:
                            if st.button(f"↩️ Release Task", key=f"rel_{row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE tasks SET status='Open', assigned_volunteer=NULL, submission_notes=NULL WHERE id=?",
                                    (row["id"],)
                                )
                                conn.commit()
                                conn.close()
                                st.warning(f"Task {row['task_code']} released back to the marketplace.")
                                st.rerun()

                        with st.form(key=f"sub_form_{row['id']}"):
                            sub_notes = st.text_area(
                                "Completion Notes / Summary:",
                                value=row['submission_notes'] if row['submission_notes'] else "",
                                placeholder="Describe completed work...",
                            )
                            proof_file = st.file_uploader(
                                "📎 Attach Proof (PDF/Image):",
                                type=["pdf", "png", "jpg", "jpeg", "docx"]
                            )
                            
                            if st.form_submit_button("🚀 Submit Work for Review"):
                                p_path = row['proof_file_path']
                                p_name = row['proof_file_name']
                                if proof_file is not None:
                                    p_name = proof_file.name
                                    p_path = os.path.join(UPLOAD_DIR, f"proof_{curr_user['username']}_{p_name}")
                                    with open(p_path, "wb") as pf:
                                        pf.write(proof_file.getbuffer())

                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute(
                                    """
                                    UPDATE tasks 
                                    SET status='Submitted / Under Review', submission_notes=?, proof_file_path=?, proof_file_name=? 
                                    WHERE id=?
                                    """,
                                    (sub_notes, p_path, p_name, row["id"])
                                )
                                conn.commit()
                                conn.close()
                                st.success("Task submitted for coordinator review!")
                                st.rerun()

    # 2. TASK TIME LOGGING & ACTIVITY
    elif app_mode == "⏱️ Task Time Logging & Activity":
        st.header("⏱️ Task Time Logging & Activity Tracker")
        st.caption("Log precise time spent working on tasks, projects, or meetings to accumulate certified service hours.")

        conn = sqlite3.connect(DB_FILE)
        my_tasks = pd.read_sql_query("SELECT task_code, title FROM tasks WHERE assigned_volunteer = ? OR status='Open'", conn, params=(curr_user['username'],))
        conn.close()

        with st.form("log_time_form"):
            st.subheader("📝 Record Time Entry")
            t_choice = st.selectbox(
                "Select Associated Task:",
                my_tasks["task_code"].tolist() if not my_tasks.empty else ["GENERAL-001"],
                format_func=lambda code: f"[{code}] {my_tasks.loc[my_tasks['task_code']==code, 'title'].values[0]}" if not my_tasks.empty and code in my_tasks['task_code'].values else "General Volunteer Service"
            )
            
            task_title_match = my_tasks.loc[my_tasks['task_code']==t_choice, 'title'].values[0] if not my_tasks.empty and t_choice in my_tasks['task_code'].values else "General Service"
            
            col_t1, col_t2 = st.columns(2)
            logged_hrs = col_t1.number_input("Hours Spent:", min_value=0.25, max_value=12.0, value=2.0, step=0.25)
            work_date = col_t2.date_input("Date Performed:", value=pd.Timestamp.now())
            
            time_notes = st.text_area("Detailed Work Performed / Notes:")

            if st.form_submit_button("✅ Submit Time Log"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO time_logs (username, task_code, task_title, hours_logged, work_date, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (curr_user['username'], t_choice, task_title_match, logged_hrs, str(work_date), time_notes)
                )
                c.execute(
                    "UPDATE users SET logged_hours = logged_hours + ? WHERE username = ?",
                    (logged_hrs, curr_user['username'])
                )
                c.execute("UPDATE tasks SET status='Approved & Completed', completed_date=? WHERE task_code=? AND (assigned_volunteer=? OR assigned_volunteer IS NULL)", (str(work_date), t_choice, curr_user['username']))
                conn.commit()
                conn.close()
                st.success(f"Successfully logged {logged_hrs} hours for [{t_choice}]!")
                st.session_state["user"]["logged_hours"] += logged_hrs
                st.rerun()

        st.write("---")
        st.subheader("📜 Your Detailed Time Logs")
        conn = sqlite3.connect(DB_FILE)
        df_logs = pd.read_sql_query("SELECT task_code, task_title, hours_logged, work_date, notes, timestamp FROM time_logs WHERE username = ? ORDER BY id DESC", conn, params=(curr_user['username'],))
        conn.close()

        if df_logs.empty:
            st.caption("No time logs recorded yet.")
        else:
            st.dataframe(df_logs, use_container_width=True)

    # 3. CALENDAR & COMPLETION VIEWS
    elif app_mode == "📅 Calendar & Completion Views":
        st.header("📅 Calendar & Task Completion Views")
        st.caption("Inspect completed tasks and organizational activities across multiple calendar and daily breakdown views.")

        t_cal1, t_cal2, t_cal3 = st.tabs(["🗓️ My Completed Tasks Calendar", "📋 Daily Organization Pulse", "📅 Event Schedule"])

        with t_cal1:
            st.subheader(f"🗓️ @{curr_user['username']}'s Completed Tasks by Date")
            conn = sqlite3.connect(DB_FILE)
            df_my_comp = pd.read_sql_query(
                "SELECT task_code, title, category, time_est, completed_date FROM tasks WHERE assigned_volunteer = ? AND status = 'Approved & Completed' ORDER BY completed_date DESC",
                conn,
                params=(curr_user['username'],)
            )
            conn.close()

            if df_my_comp.empty:
                st.info("You have no completed tasks recorded with completion dates yet.")
            else:
                st.dataframe(df_my_comp, use_container_width=True)
                for date_val, group in df_my_comp.groupby('completed_date'):
                    display_date = date_val if date_val else "Unscheduled Date"
                    with st.expander(f"📁 Date: {display_date} ({len(group)} tasks completed)"):
                        for _, r in group.iterrows():
                            st.markdown(f"- **[{r['task_code']}] {r['title']}** (`{r['category']}`) — {r['time_est']} hrs")

        with t_cal2:
            st.subheader("👥 Organization-Wide Daily Completion Pulse")
            conn = sqlite3.connect(DB_FILE)
            all_time_logs = pd.read_sql_query("SELECT username, task_code, task_title, hours_logged, work_date, notes FROM time_logs ORDER BY work_date DESC", conn)
            conn.close()

            if all_time_logs.empty:
                st.info("No time logs recorded across the organization yet.")
            else:
                unique_dates = all_time_logs['work_date'].unique().tolist()
                selected_date = st.selectbox("📅 Select Date to Inspect Organization Activity:", unique_dates)
                filtered_logs = all_time_logs[all_time_logs['work_date'] == selected_date]
                st.metric("Total Hours Logged on this Date", f"{filtered_logs['hours_logged'].sum():.1f} Hours")
                for _, log in filtered_logs.iterrows():
                    st.info(f"👤 **@{log['username']}** completed **[{log['task_code']}] {log['task_title']}** ({log['hours_logged']} hrs)\n\n> *Notes:* {log['notes']}")

        with t_cal3:
            st.subheader("📅 Official M.O.M. Calendar Events")
            conn = sqlite3.connect(DB_FILE)
            df_evts = pd.read_sql_query("SELECT title, event_date, time_str, location, description FROM calendar_events ORDER BY event_date ASC", conn)
            conn.close()

            if df_evts.empty:
                st.caption("No upcoming calendar events.")
            else:
                for _, e in df_evts.iterrows():
                    st.markdown(f"""
                    <div class="task-card">
                        <span class="mom-badge-pill">🗓️ {e['event_date']} | {e['time_str']}</span>
                        <h3 style="margin-top: 0.4rem; color: #2E1A47;">{e['title']}</h3>
                        <p><strong>📍 Location:</strong> {e['location']}</p>
                        <p>{e['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # 4. BUILD-TO-OWN HOUSING PIPELINE
    elif app_mode == "🏠 Build-to-Own Housing Pipeline":
        st.header("🏠 The 'Build-to-Own' Housing Pipeline")
        st.caption("Tracking SABS technology composite housing units, apprentice construction progress, monthly rental payment credits, and deed transfers.")

        conn = sqlite3.connect(DB_FILE)
        housing_df = pd.read_sql_query("SELECT * FROM housing_pipeline", conn)
        conn.close()

        if housing_df.empty:
            st.info("No housing units currently in the pipeline.")
        else:
            for _, h in housing_df.iterrows():
                st.markdown(f"""
                <div class="task-card">
                    <span class="mom-badge-pill">🏠 Unit Code: {h['unit_code']} | Status: {h['construction_status']}</span>
                    <h3 style="margin-top: 0.4rem; color: #2E1A47;">Participant: {h['participant_name']}</h3>
                    <p><strong>📍 Location:</strong> {h['site_location']}</p>
                    <p><strong>💰 Monthly Rent:</strong> ${h['monthly_rent']:,.2f} | <strong>Credited Toward Purchase:</strong> ${h['total_credited']:,.2f} /${h['purchase_price']:,.2f}</p>
                    <p><strong>📜 Deed Transfer Stage:</strong> `{h['deed_transfer_status']}`</p>
                </div>
                """, unsafe_allow_html=True)

        if curr_user["role"] in ["Coordinator", "Admin"]:
            st.write("---")
            st.subheader("➕ Add / Update Housing Unit")
            with st.form("housing_form"):
                u_code = st.text_input("Unit Code (e.g. SABS-UNIT-03):")
                u_loc = st.text_input("Site Location:", value="Node 2: Chandler Rd Campus (Traskwood)")
                u_part = st.text_input("Participant Family Name:")
                u_stat = st.selectbox("Construction Status:", ["Under Construction", "Completed / Occupied"])
                u_rent = st.number_input("Monthly Rent Amount ($):", value=750.0)
                u_cred = st.number_input("Total Credited Toward Purchase ($):", value=0.0)
                u_price = st.number_input("Total Purchase Price ($):", value=150000.0)
                u_deed = st.text_input("Deed Transfer Status:", value="Lease-to-Own Active")

                if st.form_submit_button("Save Housing Unit Record"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO housing_pipeline (unit_code, site_location, participant_name, construction_status, monthly_rent, total_credited, purchase_price, deed_transfer_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (u_code, u_loc, u_part, u_stat, u_rent, u_cred, u_price, u_deed))
                    conn.commit()
                    conn.close()
                    st.success("Housing unit saved!")
                    st.rerun()

    # 5. LIVE IMPACT & GRANT MATCH
    elif app_mode == "📊 Live Impact & Grant Match":
        st.header("📊 Community Impact & Federal Grant Match Calculator")
        st.caption("Calculate non-federal volunteer match value at the Independent Sector rate ($33.49/hr) for CDBG and grant applications.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(logged_hours) FROM users")
        total_all_hours = cursor.fetchone()[0] or 0.0
        conn.close()

        INDEPENDENT_SECTOR_RATE = 33.49
        total_match_value = total_all_hours * INDEPENDENT_SECTOR_RATE

        m1, m2, m3 = st.columns(3)
        m1.metric("👥 Total Cumulative Volunteer Hours", f"{total_all_hours:.1f} Hours")
        m2.metric("💵 Independent Sector Rate", f"${INDEPENDENT_SECTOR_RATE:.2f} / hr")
        m3.metric("🤝 Total Non-Federal Match Value", f"${total_match_value:,.2f}")

        st.write("---")
        st.subheader("📢 Official Announcements")
        conn = sqlite3.connect(DB_FILE)
        df_ann = pd.read_sql_query("SELECT title, content, date_posted, category FROM announcements ORDER BY id DESC LIMIT 5", conn)
        conn.close()
        for _, a_row in df_ann.iterrows():
            st.info(f"📌 **[{a_row['category']}] {a_row['title']}** ({a_row['date_posted']})\n\n{a_row['content']}")

    # 6. DIRECT MESSAGING
    elif app_mode == "💬 Direct Messaging":
        st.header("💬 Internal Direct Messaging")
        conn = sqlite3.connect(DB_FILE)
        all_users = pd.read_sql_query("SELECT username, full_name, role FROM users WHERE username != ?", conn, params=(curr_user['username'],))
        conn.close()

        if all_users.empty:
            st.info("No other registered users found.")
        else:
            selected_recipient = st.selectbox(
                "Select Recipient:",
                all_users["username"].tolist(),
                format_func=lambda u: f"{all_users.loc[all_users['username']==u, 'full_name'].values[0]} (@{u})"
            )

            with st.form("send_msg_form"):
                msg_body = st.text_area("Write Your Message:")
                if st.form_submit_button("📨 Send Message"):
                    if msg_body:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)", (curr_user['username'], selected_recipient, msg_body))
                        conn.commit()
                        conn.close()
                        st.success("Message sent!")
                        st.rerun()

            st.write("---")
            conn = sqlite3.connect(DB_FILE)
            msgs = pd.read_sql_query("SELECT sender, message, timestamp FROM messages WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?) ORDER BY id ASC", conn, params=(curr_user['username'], selected_recipient, selected_recipient, curr_user['username']))
            conn.close()
            for _, m in msgs.iterrows():
                align = "👉 **You**" if m['sender'] == curr_user['username'] else f"👈 **@{m['sender']}**"
                st.markdown(f"{align} *({m['timestamp']})*:\n>{m['message']}")

    # 7. COMMUNITY DISCUSSION BOARD
    elif app_mode == "🗣️ Community Discussion Board":
        st.header("🗣️ Community Discussion Board")
        t_d1, t_d2 = st.tabs(["💬 Active Topics", "➕ Start Topic"])
        with t_d1:
            conn = sqlite3.connect(DB_FILE)
            disc = pd.read_sql_query("SELECT id, author, title, category, content, timestamp FROM discussions ORDER BY id DESC", conn)
            conn.close()
            for _, d in disc.iterrows():
                with st.expander(f"📌 [{d['category']}] {d['title']} (by @{d['author']})"):
                    st.markdown(d['content'])
        with t_d2:
            with st.form("new_disc"):
                t_title = st.text_input("Title:")
                t_cat = st.selectbox("Category:", ["General", "Fundraising", "Legal Navigation", "Trade & Salvage"])
                t_cont = st.text_area("Content:")
                if st.form_submit_button("Publish"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO discussions (author, title, category, content) VALUES (?, ?, ?, ?)", (curr_user['full_name'], t_title, t_cat, t_cont))
                    conn.commit()
                    conn.close()
                    st.success("Published!")
                    st.rerun()

    # 8. TRAINING & TIER UPGRADE
    elif app_mode == "🎓 Training & Tier Upgrade":
        st.header("🎓 Interactive Micro-Training & Auto-Tier Unlocking")
        with st.form("quiz_form"):
            q1 = st.radio("1. Purpose of 5-Tab Legal Readiness Binders?", ["Random storage", "Standardized proof of compliance for pro se parents", "Lawsuits"])
            q2 = st.radio("2. Can Good360 items be resold?", ["Yes", "No, strictly prohibited", "Maybe"])
            if st.form_submit_button("Submit Quiz"):
                if q1.startswith("Standardized") and q2.startswith("No"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("UPDATE users SET tier=2 WHERE username=?", (curr_user['username'],))
                    conn.commit()
                    conn.close()
                    st.success("🎉 Upgraded to Tier 2!")
                    st.rerun()
                else:
                    st.error("Incorrect answers. Try again!")

    # 9. KUDOS & LEADERBOARD
    elif app_mode == "🌟 Community Kudos & Leaderboard":
        st.header("🌟 Leaderboard & Kudos")
        c1, c2 = st.columns(2)
        with c1:
            conn = sqlite3.connect(DB_FILE)
            st.dataframe(pd.read_sql_query("SELECT full_name, logged_hours, badges FROM users ORDER BY logged_hours DESC", conn), use_container_width=True)
            conn.close()
        with c2:
            with st.form("kudos"):
                k_msg = st.text_area("Appreciation Message:")
                if st.form_submit_button("Send"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO kudos (author, recipient, message) VALUES (?, ?, ?)", (curr_user['full_name'], "Team", k_msg))
                    conn.commit()
                    conn.close()
                    st.success("Kudos sent!")
                    st.rerun()

    # 10. SUGGESTION BOX & SUPPORT CENTER
    elif app_mode == "💡 Suggestion Box & Support Center":
        st.header("💡 Support & Suggestions")
        with st.form("ticket"):
            s_sub = st.text_input("Subject:")
            s_msg = st.text_area("Message:")
            if st.form_submit_button("Send Ticket"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO support_tickets (volunteer, subject, message) VALUES (?, ?, ?)", (curr_user['username'], s_sub, s_msg))
                conn.commit()
                conn.close()
                st.success("Ticket submitted!")
                st.rerun()

    # 11. ONBOARDING (COORDINATORS)
    elif app_mode == "👥 Volunteer Onboarding" and curr_user["role"] in ["Coordinator", "Admin"]:
        st.header("👥 Volunteer Onboarding")
        with st.form("onboard"):
            un = st.text_input("Username:")
            pw = st.text_input("Password:", type="password", value="mom2026")
            fn = st.text_input("Full Name:")
            em = st.text_input("Email:")
            if st.form_submit_button("Create"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours) VALUES (?, ?, ?, ?, 'Volunteer', 1, 0.0)", (un, hash_pass(pw), fn, em))
                conn.commit()
                conn.close()
                st.success("Account created!")

    # 12. COORDINATOR COMMAND CENTER
    elif app_mode == "🛠️ Coordinator Command Center" and curr_user["role"] in ["Coordinator", "Admin"]:
        st.header("🛠️ Coordinator Command Center")
        t_c1, t_c2, t_c3 = st.tabs(["📝 Task Management", "📊 Google Sheets Sync", "📅 Event Manager"])
        with t_c1:
            with st.form("new_task"):
                tc = st.text_input("Task Code (e.g. FUND-103):")
                tt = st.text_input("Title:")
                t_cat = st.selectbox("Category:", ["Community Outreach & Fundraising", "Civil Legal Navigation", "Heritage Trade & Logistics"])
                t_hrs = st.number_input("Hours Estimate:", value=2.0)
                t_why = st.text_area("Why This Matters:")
                t_ins = st.text_area("Instructions:")
                t_del = st.text_area("Expected Deliverable:")
                if st.form_submit_button("Publish Task"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable) VALUES (?, ?, ?, 'Node 1', 'Admin', 1, ?, ?, ?, ?)", (tc, tt, t_cat, t_hrs, t_why, t_ins, t_del))
                    conn.commit()
                    conn.close()
                    st.success("Task published!")
                    st.rerun()
        with t_c2:
            if st.button("Sync Users to Google Sheets"):
                conn = sqlite3.connect(DB_FILE)
                df_u = pd.read_sql_query("SELECT username, full_name, email, role, tier, logged_hours FROM users", conn)
                conn.close()
                succ, msg = sync_to_gsheets("Users", df_u)
                if succ: st.success(msg)
                else: st.error(msg)
        with t_c3:
            with st.form("add_event"):
                e_title = st.text_input("Event Title:")
                e_date = st.date_input("Event Date:")
                e_time = st.text_input("Time:", value="6:00 PM")
                e_loc = st.text_input("Location:")
                e_desc = st.text_area("Description:")
                if st.form_submit_button("Add Event"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO calendar_events (title, event_date, time_str, location, description) VALUES (?, ?, ?, ?, ?)", (e_title, str(e_date), e_time, e_loc, e_desc))
                    conn.commit()
                    conn.close()
                    st.success("Event added!")
                    st.rerun()
