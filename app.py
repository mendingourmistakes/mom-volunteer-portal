Complete Upgraded app.py Code
import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF

DB_FILE = "mom_volunteers.db"
UPLOAD_DIR = "uploaded_resources"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()


def clean_pdf_text(text):
    if not text:
        return ""
    # Replace common unicode dashes and quotes with standard ASCII
    text = (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    # Strip emojis and non-latin1 characters for standard Helvetica PDF fonts
    return text.encode("latin-1", "ignore").decode("latin-1").strip()


def generate_pdf_letter(full_name, username, total_hours, tier, badges):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header Banner
    pdf.set_fill_color(46, 26, 71)  # Primary Dark Purple
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
    pdf.set_text_color(45, 55, 72)

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

    # Users table
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

    # Tasks table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
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
            submission_notes TEXT DEFAULT NULL
        )
    """)

    # Kudos table
    c.execute("""
        CREATE TABLE IF NOT EXISTS kudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed default Admin and Onboarder accounts if missing
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone() == 0:
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

    # Seed default sample tasks if empty
    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone() == 0:
        sample_tasks = [
            (
                "ANN-101",
                "Legal Readiness Binder Audit",
                "Node 1: Dyer St Plaza Hub (Malvern)",
                "Civil Legal Navigation (ANN)",
                1,
                2.0,
                "",
                "",
                "M.O.M. supports pro se parents by organizing Legal Readiness"
                " Binders to prevent bench warrants and preserve custody.",
                "1. Review uploaded binder checklist.\n2. Verify tabs 1-5"
                " completeness (Court Orders, Income Proof, Visitation Logs, Drug"
                " Tests, Certificates).\n3. Format clean index.",
                "Completed 5-Tab Digital Index PDF ready for CALES review.",
                "Open",
                None,
                None,
            ),
            (
                "AHTA-201",
                "Salvage Materials Cataloging",
                "Node 3: Industrial Rd Trade Yard (Malvern)",
                "Heritage Trade & Salvage (AHTA)",
                2,
                1.5,
                "",
                "",
                "Reclaimed brick and timber sales generate tax-free enterprise"
                " revenue while training trade apprentices in historic"
                " preservation.",
                "1. Inspect incoming material photos.\n2. Log quantities,"
                " dimensions, and architectural era into catalog.",
                "10 cataloged inventory entries submitted to AHTA Salvage Depot.",
                "Open",
                None,
                None,
            ),
        ]
        c.executemany(
            """
            INSERT INTO tasks (task_code, title, site_node, module, tier_required, time_est, file_path, file_name, why_it_matters, instructions, expected_deliverable, status, assigned_volunteer, submission_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_tasks,
        )

    conn.commit()
    conn.close()


init_db()

# Page config
st.set_page_config(
    page_title="Mending Our Mistakes, Inc. — Volunteer Portal",
    page_icon="💜",
    layout="wide",
)

# Custom Styling
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

    body, .stApp {
        background-color: #FFFFFF;
        font-family: 'Merriweather', serif;
        color: #2D3748;
    }

    .mom-header {
        background: linear-gradient(135deg, #2E1A47 0%, #153D62 100%);
        padding: 2.2rem 2rem;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(46, 26, 71, 0.18);
        border-bottom: 4px solid #B47A19;
    }

    .mom-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0 0 0.4rem 0;
    }

    .mom-header p {
        font-family: 'Merriweather', serif;
        font-size: 1.05rem;
        color: #E0D7EA;
        margin: 0;
    }

    .mom-badge-pill {
        background-color: #F3EBF9;
        color: #5B2C6F;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 14px;
        border-radius: 50px;
        display: inline-block;
        margin-bottom: 0.8rem;
    }

    h1, h2, h3, .stHeader {
        font-family: 'Playfair Display', serif !important;
        color: #2E1A47 !important;
    }

    .task-card {
        background-color: #FFFFFF;
        border: 1px solid #E0D7EA;
        border-left: 6px solid #2E1A47;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(46, 26, 71, 0.05);
    }

    .stButton>button, div.stDownloadButton>button {
        background-color: #2E1A47 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
    }

    .stButton>button:hover, div.stDownloadButton>button:hover {
        background-color: #B47A19 !important;
        box-shadow: 0 4px 12px rgba(180, 122, 25, 0.3) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E0D7EA !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar Authentication Box
st.sidebar.markdown(
    """
<div style="text-align: center; padding-bottom: 1rem;">
    <h2 style="font-family: 'Playfair Display', serif; color: #2E1A47; margin: 0;">Mending Our Mistakes</h2>
    <p style="font-size: 0.8rem; color: #5B2C6F; font-style: italic;">A Parental Restoration Continuum</p>
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

# MAIN BRAND HEADER BANNER
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
    Our portal provides secure, tiered access to task cards, resource documents, micro-training, and service hour certification.
    """)

else:
    curr_user = st.session_state["user"]

    # Navigation Bar
    nav_options = [
        "📋 My Task Workspace",
        "📊 Live Impact Dashboard",
        "🎓 Training & Tier Upgrade",
        "🌟 Community Kudos & Leaderboard",
    ]
    if curr_user["role"] in ["Coordinator", "Admin"]:
        nav_options.extend(["👥 Volunteer Onboarding", "⚙️ Coordinator Admin Hub"])

    app_mode = st.radio("Portal View:", nav_options, horizontal=True)

    # 1. MY TASK WORKSPACE
    if app_mode == "📋 My Task Workspace":
        st.header(f"👋 Welcome, {curr_user['full_name']}!")

        # Profile Summary & PDF Certificate Generator
        col_prof1, col_prof2 = st.columns(2)
        with col_prof1:
            c_p1, c_p2, c_p3 = st.columns(3)
            c_p1.metric("Clearance Tier", f"Tier {curr_user['tier']}")
            c_p2.metric("Service Hours", f"{curr_user['logged_hours']:.1f} Hours")
            badge_display = curr_user["badges"] if curr_user["badges"] else "🌱 Active"
            c_p3.metric("Badges Earned", badge_display)
        with col_prof2:
            # Generate PDF Service Letter
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
        st.subheader("📋 Tasks Available for Your Clearance Level")

        conn = sqlite3.connect(DB_FILE)
        df_tasks = pd.read_sql_query(
            f"SELECT * FROM tasks WHERE tier_required <= {curr_user['tier']} AND"
            " status IN ('Open', 'In Progress')",
            conn,
        )
        conn.close()

        if df_tasks.empty:
            st.info("No open tasks currently available at your approved tier level.")
        else:
            for idx, row in df_tasks.iterrows():
                with st.container():
                    st.markdown(
                        f"""
                        <div class="task-card">
                            <span class="mom-badge-pill">Tier {row['tier_required']} | {row['time_est']} Hours</span>
                            <h3 style="margin-top: 0.4rem; color: #2E1A47;">🟢 [{row['task_code']}] {row['title']}</h3>
                            <p><strong>📍 Site Node:</strong> {row['site_node']} | <strong>⚙️ Module:</strong> {row['module']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"#### 💡 Why This Matters\n{row['why_it_matters']}")

                    if row["file_path"] and os.path.exists(row["file_path"]):
                        with open(row["file_path"], "rb") as f:
                            st.download_button(
                                label=f"📥 Download Task Resource File ({row['file_name']})",
                                data=f.read(),
                                file_name=row["file_name"],
                                mime="application/octet-stream",
                                key=f"dl_{row['task_code']}"
                            )

                    with st.expander("📌 View Instructions & Deliverable Standards"):
                        st.markdown(
                            f"**Step-by-Step Instructions:**\n{row['instructions']}"
                        )
                        st.markdown(
                            f"**Expected Deliverable:**\n{row['expected_deliverable']}"
                        )

                    with st.form(key=f"sub_form_{row['task_code']}"):
                        sub_notes = st.text_area(
                            "Submit Completed Work / Completion Notes:",
                            placeholder=(
                                "Paste your output link, text, or summary notes here..."
                            ),
                        )
                        if st.form_submit_button("Submit Work for Credit & Review"):
                            if not sub_notes:
                                st.error("Please enter completion notes before submitting!")
                            else:
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE tasks SET status='Submitted / Under Review',"
                                    " assigned_volunteer=?, submission_notes=? WHERE task_code=?",
                                    (curr_user["username"], sub_notes, row["task_code"]),
                                )
                                conn.commit()
                                conn.close()
                                st.success(
                                    f"Task {row['task_code']} submitted! Your coordinator will"
                                    " review it and credit your service hours."
                                )
                                st.rerun()

        # Personal History
        st.write("---")
        st.subheader("📜 Your Submitted & Approved Task History")
        conn = sqlite3.connect(DB_FILE)
        df_my_history = pd.read_sql_query(
            "SELECT task_code, title, time_est, status, submission_notes FROM"
            f" tasks WHERE assigned_volunteer = '{curr_user['username']}'",
            conn,
        )
        conn.close()
        if df_my_history.empty:
            st.caption("You haven't submitted any tasks yet.")
        else:
            st.dataframe(df_my_history, use_container_width=True)

    # 2. LIVE IMPACT DASHBOARD
    elif app_mode == "📊 Live Impact Dashboard":
        st.header("📊 M.O.M. Community Impact Dashboard")
        st.caption(
            "Real-Time Community Impact Metrics Across Our 7 Regional Site Nodes"
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⚖️ Legal Binders Checked", "48 Binders", "+12 This Month")
        m2.metric("🧸 Good360 Care Packages", "185 Families", "+35 Distributed")
        m3.metric("🪵 AHTA Reclaimed Materials", "3,400 sq. ft.", "+800 sq. ft.")
        m4.metric("🚐 Micro-Transit Rides", "112 Trips", "Saline & Hot Spring")

        st.write("---")
        st.subheader("🎯 Active Community Stabilization Goals")
        st.markdown(
            "**1. Legal Readiness Binders for Upcoming Family Court Docket (Goal:"
            " 50)**"
        )
        st.progress(0.96)
        st.caption(
            "96% Complete — 48 of 50 Binders Verified for Judge Burnett's Docket!"
        )

        st.markdown(
            "**2. Good360 Household Care Kits for Reunifying Kinship Families"
            " (Goal: 200)**"
        )
        st.progress(0.85)
        st.caption(
            "85% Complete — 185 Care Packages Delivered to Chandler Road Campus!"
        )

    # 3. TRAINING & TIER UPGRADE
    elif app_mode == "🎓 Training & Tier Upgrade":
        st.header("🎓 Interactive Micro-Training & Auto-Tier Unlocking")
        st.caption(
            "Complete a 3-Minute Orientation Quiz to Upgrade Your Volunteer"
            " Clearance Tier Automatically!"
        )

        st.subheader("🔒 Tier 2 Clearance Quiz: Privacy & Logistics Etiquette")
        with st.form("quiz_tier2_form"):
            q1 = st.radio(
                "1. What is the primary purpose of M.O.M.'s 5-Tab Legal Readiness"
                " Binders?",
                [
                    "To store random documents",
                    (
                        "To provide standardized, court-admissible proof of"
                        " compliance for pro se parents"
                    ),
                    "To file lawsuit appeals",
                ],
            )
            q2 = st.radio(
                "2. Can Good360 donated care goods be resold or auctioned?",
                [
                    "Yes, to raise funds",
                    "No, Good360 rules strictly prohibit resale or bartering",
                    "Only with manager approval",
                ],
            )
            q3 = st.radio(
                "3. What is the proper procedure if a participant shares sensitive"
                " court or health data?",
                [
                    "Post it on social media",
                    (
                        "Maintain strict confidentiality under HIPAA and court"
                        " navigation rules"
                    ),
                    "Ignore it",
                ],
            )

            if st.form_submit_button("Submit Quiz for Tier Upgrade"):
                if (
                    q1.startswith("To provide")
                    and q2.startswith("No, Good360")
                    and q3.startswith("Maintain")
                ):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    new_tier = max(curr_user["tier"], 2)
                    c.execute(
                        "UPDATE users SET tier=? WHERE username=?",
                        (new_tier, curr_user["username"]),
                    )
                    conn.commit()
                    conn.close()
                    st.success(
                        "🎉 100% Score! You have successfully upgraded to Clearance"
                        " Tier 2!"
                    )
                    st.session_state["user"]["tier"] = new_tier
                    st.rerun()
                else:
                    st.error(
                        "Some answers were incorrect. Please review the rules and try"
                        " again!"
                    )

    # 4. KUDOS & LEADERBOARD
    elif app_mode == "🌟 Community Kudos & Leaderboard":
        st.header("🌟 Volunteer Kudos & Monthly Leaderboard")

        col_k1, col_k2 = st.columns(2)

        with col_k1:
            st.subheader("🏆 Monthly Hours Leaderboard")
            conn = sqlite3.connect(DB_FILE)
            df_lead = pd.read_sql_query(
                "SELECT full_name, logged_hours, badges FROM users ORDER BY"
                " logged_hours DESC LIMIT 5",
                conn,
            )
            conn.close()
            st.dataframe(df_lead, use_container_width=True)

        with col_k2:
            st.subheader("💬 Send Peer Kudos")
            with st.form("kudos_form"):
                conn = sqlite3.connect(DB_FILE)
                recip_df = pd.read_sql_query(
                    "SELECT username, full_name FROM users", conn
                )
                conn.close()

                k_recip = st.selectbox("Recipient:", recip_df["full_name"].tolist())
                k_msg = st.text_area("Your Appreciation Message:")

                if st.form_submit_button("Post Kudos"):
                    if k_msg:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO kudos (author, recipient, message) VALUES (?, ?,"
                            " ?)",
                            (curr_user["full_name"], k_recip, k_msg),
                        )
                        conn.commit()
                        conn.close()
                        st.success("Kudos message posted!")
                        st.rerun()

        st.write("---")
        st.subheader("📣 Recent Community Shout-Outs")
        conn = sqlite3.connect(DB_FILE)
        df_kudos_list = pd.read_sql_query(
            "SELECT author, recipient, message, timestamp FROM kudos ORDER BY id"
            " DESC LIMIT 5",
            conn,
        )
        conn.close()

        if df_kudos_list.empty:
            st.caption(
                "No shout-outs posted yet. Be the first to appreciate a fellow"
                " volunteer!"
            )
        else:
            for idx, k_row in df_kudos_list.iterrows():
                msg_text = k_row['message']
                time_text = k_row['timestamp']
                st.info(
                    f"🌟 **{k_row['author']}** to **{k_row['recipient']}**: "
                    f'"{msg_text}" *({time_text})*'
                )

    # 5. ONBOARDING (COORDINATORS)
    elif app_mode == "👥 Volunteer Onboarding":
        st.header("👥 Volunteer Onboarding & User Management")
        with st.form("create_user_form"):
            u1, u2 = st.columns(2)
            new_user = u1.text_input("New Username:")
            new_pass = u1.text_input("Set Password:", type="password", value="mom2026")
            new_name = u1.text_input("Full Name:")
            new_email = u2.text_input("Email:")
            new_role = u2.selectbox("Role:", ["Volunteer", "Coordinator"])
            new_tier = u2.slider("Clearance Tier:", 1, 3, 1)

            if st.form_submit_button("Create Account"):
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (username, password_hash, full_name, email,"
                    " role, tier, logged_hours, badges) VALUES (?, ?, ?, ?, ?, ?, 0.0,"
                    " '🌱 Active Contributor')",
                    (
                        new_user.strip(),
                        hash_pass(new_pass),
                        new_name,
                        new_email,
                        new_role,
                        new_tier,
                    ),
                )
                conn.commit()
                conn.close()
                st.success(f"Account for {new_name} created!")

    # 6. COORDINATOR ADMIN HUB
    elif app_mode == "⚙️ Coordinator Admin Hub":
        st.header("⚙️ Coordinator Admin Hub")
        t_rev, t_pub = st.tabs(["📥 Review Submissions", "➕ Publish Task"])

        with t_rev:
            conn = sqlite3.connect(DB_FILE)
            df_rev = pd.read_sql_query(
                "SELECT * FROM tasks WHERE status = 'Submitted / Under Review'", conn
            )
            conn.close()

            if df_rev.empty:
                st.info("No submissions pending review.")
            else:
                for idx, r_row in df_rev.iterrows():
                    st.write(
                        f"**[{r_row['task_code']}] {r_row['title']}** by"
                        f" {r_row['assigned_volunteer']}"
                    )
                    st.code(r_row["submission_notes"])
                    if st.button(
                        f"Approve & Credit {r_row['time_est']} Hrs ({r_row['task_code']})"
                    ):
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "UPDATE tasks SET status='Approved & Completed' WHERE"
                            " task_code=?",
                            (r_row["task_code"],),
                        )
                        c.execute(
                            "UPDATE users SET logged_hours = logged_hours + ? WHERE"
                            " username=?",
                            (r_row["time_est"], r_row["assigned_volunteer"]),
                        )
                        conn.commit()
                        conn.close()
                        st.success("Approved and hours credited!")
                        st.rerun()

        with t_pub:
            with st.form("pub_form"):
                p_code = st.text_input("Task Code:")
                p_title = st.text_input("Task Title:")
                p_site = st.selectbox(
                    "Site Node:",
                    [
                        "Node 1: Dyer St Plaza Hub (Malvern)",
                        "Node 2: Chandler Rd Campus (Traskwood)",
                        "Node 3: Industrial Rd Trade Yard (Malvern)",
                    ],
                )
                p_mod = st.selectbox(
                    "Module:",
                    [
                        "Civil Legal Navigation (ANN)",
                        "Safe Family Contact (PRISM)",
                        "Heritage Trade & Salvage (AHTA)",
                    ],
                )
                p_tier = st.slider("Required Tier:", 1, 3, 1)
                p_hrs = st.number_input("Service Hours Credit:", value=2.0, step=0.5)
                p_why = st.text_area("Why This Matters:")
                p_inst = st.text_area("Instructions:")
                p_deliv = st.text_area("Expected Deliverable:")

                if st.form_submit_button("Publish Task Card"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO tasks (task_code, title, site_node, module,"
                        " tier_required, time_est, why_it_matters, instructions,"
                        " expected_deliverable) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            p_code,
                            p_title,
                            p_site,
                            p_mod,
                            p_tier,
                            p_hrs,
                            p_why,
                            p_inst,
                            p_deliv,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("Task Published!")
