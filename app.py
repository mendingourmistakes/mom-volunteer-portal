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

    # Header Banner
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

@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
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
            proof_file_name TEXT DEFAULT ''
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

    # Messages table
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

    # Discussion topics
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

    # Discussion replies
    c.execute("""
        CREATE TABLE IF NOT EXISTS discussion_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discussion_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Support tickets
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

    # Suggestions
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

    # Announcements
    c.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            category TEXT DEFAULT 'General Announcement'
        )
    """)

    # Calendar Events
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

    # Poll votes
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

    # Seed Default Tasks
    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        sample_tasks = [
            (
                "FUND-101",
                "Community Outreach & Donation Requests (Batch of 5)",
                "Community Outreach & Fundraising",
                "Node 1: Dyer St Plaza Hub (Malvern)",
                "Grants & Master Administration",
                1,
                2.0,
                "",
                "",
                "Securing community sponsors and local donations funds emergency assistance for court-involved parents.",
                "1. Use the Outreach Email Templates provided in the hub.\n2. Send 5 outreach emails to local businesses or churches.\n3. Upload PDF or screenshot proof of sent emails.",
                "List of 5 organizations contacted + PDF/screenshot proof attached.",
                "Open",
                None,
                None,
                "",
                ""
            ),
            (
                "ANN-101",
                "Legal Readiness Binder Audit",
                "Civil Legal Navigation",
                "Node 1: Dyer St Plaza Hub (Malvern)",
                "Civil Legal Navigation (ANN)",
                1,
                2.0,
                "",
                "",
                "M.O.M. supports pro se parents by organizing Legal Readiness Binders to prevent bench warrants and preserve custody.",
                "1. Review uploaded binder checklist.\n2. Verify tabs 1-5 completeness.\n3. Format clean index.",
                "Completed 5-Tab Digital Index PDF ready for CALES review.",
                "Open",
                None,
                None,
                "",
                ""
            ),
            (
                "AHTA-201",
                "Salvage Materials Cataloging",
                "Heritage Trade & Logistics",
                "Node 3: Industrial Rd Trade Yard (Malvern)",
                "Heritage Trade & Salvage (AHTA)",
                2,
                1.5,
                "",
                "",
                "Reclaimed brick and timber sales generate revenue while training trade apprentices.",
                "1. Inspect incoming material photos.\n2. Log quantities, dimensions, and architectural era into catalog.",
                "10 cataloged inventory entries submitted to AHTA Salvage Depot.",
                "Open",
                None,
                None,
                "",
                ""
            ),
        ]
        c.executemany(
            """
            INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, file_path, file_name, why_it_matters, instructions, expected_deliverable, status, assigned_volunteer, submission_notes, proof_file_path, proof_file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            sample_tasks,
        )

    # Seed Announcements
    c.execute("SELECT COUNT(*) FROM announcements")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO announcements (title, content, date_posted, category) VALUES (?, ?, ?, ?)",
            ("🚀 Welcome to the M.O.M. Volunteer Portal!", "We are excited to launch our centralized task marketplace, resource center, and communication hub across our 7 regional site nodes. Thank you for standing with local families!", "2026-09-30", "Organization Update")
        )
        c.execute(
            "INSERT INTO announcements (title, content, date_posted, category) VALUES (?, ?, ?, ?)",
            ("⚖️ Family Court Docket Support Drive", "We are currently preparing 50 Legal Readiness Binders for Judge Burnett's upcoming docket in Malvern. Claim task ANN-101 to assist!", "2026-09-29", "Urgent Call to Action")
        )

    # Seed Calendar Events
    c.execute("SELECT COUNT(*) FROM calendar_events")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO calendar_events (title, event_date, time_str, location, description) VALUES (?, ?, ?, ?, ?)",
            ("Monthly Volunteer Orientation & Q&A", "2026-10-05", "6:00 PM - 7:00 PM", "Virtual (Zoom) / Node 1 Plaza Hub", "Join our team for a live walkthrough of upcoming CoC milestones, trade salvage projects, and tier 2 training.")
        )
        c.execute(
            "INSERT INTO calendar_events (title, event_date, time_str, location, description) VALUES (?, ?, ?, ?, ?)",
            ("Good360 Care Goods Intake & Staging Day", "2026-10-12", "10:00 AM - 2:00 PM", "Node 2: Chandler Rd Campus (Traskwood)", "Unboxing and sorting essential household goods, cribs, and care kits for reunifying kinship families.")
        )

    # Seed Sample Discussion
    c.execute("SELECT COUNT(*) FROM discussions")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO discussions (author, title, category, content) VALUES (?, ?, ?, ?)",
            ("Volunteer Coordinator", "Tips for Reaching Out to Local Businesses", "Fundraising & Outreach", "When contacting local business owners for sponsorships, emphasize how M.O.M. builds workforce trade skills and restores local families. Feel free to use Template 1 in the Task Marketplace!")
        )

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
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

    body, .stApp {
        background-color: #FAFAFC;
        font-family: 'Inter', sans-serif;
        color: #2D3748;
    }

    .mom-header {
        background: linear-gradient(135deg, #2E1A47 0%, #153D62 100%);
        padding: 2rem 2rem;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 20px rgba(46, 26, 71, 0.15);
        border-bottom: 4px solid #B47A19;
    }

    .mom-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0 0 0.3rem 0;
    }

    .mom-header p {
        font-family: 'Merriweather', serif;
        font-size: 1rem;
        color: #E0D7EA;
        margin: 0;
    }

    .mom-badge-pill {
        background-color: #F3EBF9;
        color: #5B2C6F;
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 3px 12px;
        border-radius: 50px;
        display: inline-block;
        margin-bottom: 0.6rem;
    }

    .mom-tag-pill {
        background-color: #E2E8F0;
        color: #2D3748;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-right: 6px;
    }

    h1, h2, h3, .stHeader {
        font-family: 'Playfair Display', serif !important;
        color: #2E1A47 !important;
    }

    .clean-summary-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2E1A47;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        transition: all 0.2s ease-in-out;
    }

    .clean-summary-card:hover {
        border-left-color: #B47A19;
        box-shadow: 0 4px 12px rgba(46, 26, 71, 0.08);
    }

    .clean-card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #2E1A47;
        margin: 0 0 0.3rem 0;
    }

    .clean-card-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #4A5568;
        margin: 0;
    }

    .stButton>button, div.stDownloadButton>button {
        background-color: #2E1A47 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        border: none !important;
    }

    .stButton>button:hover, div.stDownloadButton>button:hover {
        background-color: #B47A19 !important;
        box-shadow: 0 3px 10px rgba(180, 122, 25, 0.25) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E0D7EA !important;
    }

    .stExpander {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        margin-bottom: 0.8rem !important;
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
        "📊 Live Impact & News Dashboard",
        "💬 Direct Messaging",
        "🗣️ Community Discussion Board",
        "🎓 Training & Tier Upgrade",
        "🌟 Community Kudos & Leaderboard",
        "💡 Suggestion Box & Support Center",
    ]
    if curr_user["role"] in ["Coordinator", "Admin"]:
        nav_options.extend(["👥 Volunteer Onboarding", "🛠️ Coordinator Command Center"])

    app_mode = st.radio("Portal View:", nav_options, horizontal=True)

    # 1. VOLUNTEER TASK MARKETPLACE (CLEAN, ACCESSIBLE, EXPANDABLE)
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
        st.caption("Clean summary cards for fast scanning. Click '🔽 View Details & Action Controls' on any task to see instructions, attachments, and claim options!")

        conn = sqlite3.connect(DB_FILE)
        categories_df = pd.read_sql_query("SELECT DISTINCT category FROM tasks", conn)
        all_categories = ["All Categories"] + categories_df["category"].dropna().tolist()
        selected_cat = st.selectbox("🔍 Filter Tasks by Category:", all_categories)

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
                is_claimed_by_me = (row['assigned_volunteer'] == curr_user['username'])
                status_icon = "🟢 OPEN TASK" if row['status'] == 'Open' else f"🟡 YOUR TASK ({row['status']})"
                
                # CLEAN EASY-TO-READ SUMMARY CARD HEADER
                st.markdown(
                    f"""
                    <div class="clean-summary-card">
                        <div class="clean-card-title">[{row['task_code']}] {row['title']}</div>
                        <div class="clean-card-meta">
                            <span class="mom-badge-pill">{status_icon}</span>
                            <span class="mom-tag-pill">📂 {row['category']}</span>
                            <span class="mom-tag-pill">📍 {row['site_node']}</span>
                            <span class="mom-tag-pill">🔒 Tier {row['tier_required']}</span>
                            <span class="mom-tag-pill">⏱️ {row['time_est']} Hours Credit</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ALL HEAVY DETAILS & ACTIONS ARE NEATLY TUCKED INSIDE AN EXPANDER
                exp_label = "📌 Manage Your Claimed Task & Submissions" if is_claimed_by_me else "🔽 View Details, Instructions & Claim Task"
                with st.expander(exp_label, expanded=is_claimed_by_me):
                    st.markdown(f"#### 💡 Why This Matters\n{row['why_it_matters']}")
                    
                    if row["file_path"] and os.path.exists(row["file_path"]):
                        with open(row["file_path"], "rb") as f:
                            st.download_button(
                                label=f"📥 Download Reference Resource File ({row['file_name']})",
                                data=f.read(),
                                file_name=row["file_name"],
                                mime="application/octet-stream",
                                key=f"dl_{row['id']}_{row['task_code']}"
                            )

                    st.markdown(f"**Step-by-Step Instructions:**\n{row['instructions']}")
                    st.markdown(f"**Expected Deliverable:**\n{row['expected_deliverable']}")
                    st.write("---")

                    # Action Controls Inside Expander
                    if row['status'] == 'Open':
                        if st.button(f"🙋 Claim Task [{row['task_code']}]", key=f"claim_{row['id']}"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute(
                                "UPDATE tasks SET status='Claimed / In Progress', assigned_volunteer=? WHERE id=?",
                                (curr_user["username"], row["id"])
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Task {row['task_code']} claimed! You can now complete the work and submit your proof below.")
                            st.rerun()

                    elif is_claimed_by_me:
                        st.info(f"📌 Task Status: **{row['status']}**")
                        
                        col_rel1, _ = st.columns([1, 2])
                        with col_rel1:
                            if st.button(f"↩️ Release Task Back to Marketplace", key=f"rel_{row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE tasks SET status='Open', assigned_volunteer=NULL, submission_notes=NULL WHERE id=?",
                                    (row["id"],)
                                )
                                conn.commit()
                                conn.close()
                                st.warning(f"Task {row['task_code']} released back to the public marketplace.")
                                st.rerun()

                        with st.form(key=f"sub_form_{row['id']}"):
                            sub_notes = st.text_area(
                                "Edit / Submit Completed Work / Notes / Email List:",
                                value=row['submission_notes'] if row['submission_notes'] else "",
                                placeholder="List the 5 organizations contacted or paste your completion notes here...",
                            )
                            proof_file = st.file_uploader(
                                "📎 Upload PDF or Screenshot Proof of Sent Emails / Output (Optional):",
                                type=["pdf", "png", "jpg", "jpeg", "docx"]
                            )
                            
                            btn_label = "✏️ Update Submission" if row['status'] == 'Submitted / Under Review' else "🚀 Submit Work for Credit & Review"
                            if st.form_submit_button(btn_label):
                                if not sub_notes:
                                    st.error("Please enter completion notes before submitting!")
                                else:
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
                                    st.success(f"Submission updated for {row['task_code']}! Coordinator will review and award your hours.")
                                    st.rerun()

        st.write("---")
        st.subheader("📜 Your Submitted & Approved Task History")
        conn = sqlite3.connect(DB_FILE)
        df_my_history = pd.read_sql_query(
            "SELECT task_code, title, time_est, status, submission_notes FROM tasks WHERE assigned_volunteer = ?",
            conn,
            params=(curr_user['username'],)
        )
        conn.close()
        if df_my_history.empty:
            st.caption("You haven't submitted any tasks yet.")
        else:
            st.dataframe(df_my_history, use_container_width=True)

    # 2. LIVE IMPACT & NEWS DASHBOARD (CLEAN & FLOWY FORMATTING)
    elif app_mode == "📊 Live Impact & News Dashboard":
        st.header("📊 M.O.M. Community Impact & News Dashboard")
        st.caption("Stay Informed on Organization News, Upcoming Calendar Events & Strategic Milestones")

        # Top Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⚖️ Legal Binders Checked", "48 Binders", "+12 This Month")
        m2.metric("🧸 Good360 Care Packages", "185 Families", "+35 Distributed")
        m3.metric("🪵 AHTA Reclaimed Materials", "3,400 sq. ft.", "+800 sq. ft.")
        m4.metric("🚐 Micro-Transit Rides", "112 Trips", "Saline & Hot Spring")

        st.write("---")

        col_dash1, col_dash2 = st.columns(2)

        with col_dash1:
            st.subheader("📢 Official Announcements & Updates")
            conn = sqlite3.connect(DB_FILE)
            df_ann = pd.read_sql_query("SELECT title, content, date_posted, category FROM announcements ORDER BY id DESC LIMIT 5", conn)
            conn.close()

            if df_ann.empty:
                st.caption("No announcements posted yet.")
            else:
                for _, a_row in df_ann.iterrows():
                    with st.expander(f"📌 [{a_row['category']}] {a_row['title']} ({a_row['date_posted']})", expanded=False):
                        st.write(a_row['content'])

            st.write("---")
            st.subheader("🚀 Strategic Milestones & Roadmap")
            with st.expander("📍 View M.O.M. 3-Phase Expansion Roadmap"):
                st.markdown("""
                * **Phase 1: Pre-Launch Foundation (Current)**
                  * 5-Tab Legal Readiness Binder standardization.
                  * Google Ad Grant compliance repair for `mendingourmistakes.org`.
                  * Initial Good360 Requisition & Community Outreach Drive.
                * **Phase 2: Regional Site Node Activation (Upcoming)**
                  * Node 1 (Malvern Plaza Hub) & Node 2 (Traskwood Campus) staging.
                  * Heritage Trade & Salvage (AHTA) depot inventory cataloging.
                * **Phase 3: Full Continuum of Care (CoC) Launch**
                  * Court Appointed Lived-Experience Specialists (CALES) deployment.
                """)

        with col_dash2:
            st.subheader("📅 Upcoming Calendar & Schedule")
            conn = sqlite3.connect(DB_FILE)
            df_cal = pd.read_sql_query("SELECT title, event_date, time_str, location, description FROM calendar_events ORDER BY id ASC LIMIT 5", conn)
            conn.close()

            if df_cal.empty:
                st.caption("No calendar events scheduled yet.")
            else:
                for _, c_row in df_cal.iterrows():
                    with st.expander(f"🗓️ {c_row['event_date']} — {c_row['title']}"):
                        st.markdown(f"**Time:** {c_row['time_str']}")
                        st.markdown(f"**Location:** {c_row['location']}")
                        st.write(c_row['description'])

            st.write("---")
            st.subheader("🗳️ Volunteer Pulse Check")
            with st.expander("🗳️ Vote: Preferred Workday Schedule"):
                with st.form("pulse_poll_form"):
                    poll_opt = st.radio("Select your preferred time slot:", [
                        "Weekday Evenings (6:00 PM - 8:00 PM)",
                        "Saturday Mornings (9:00 AM - 12:00 PM)",
                        "Self-Paced / Flexible Remote Hours",
                    ])
                    if st.form_submit_button("Submit Vote"):
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("INSERT INTO poll_votes (username, option_chosen) VALUES (?, ?)", (curr_user['username'], poll_opt))
                        conn.commit()
                        conn.close()
                        st.success("Thank you for your feedback! Vote recorded.")

    # 3. DIRECT MESSAGING
    elif app_mode == "💬 Direct Messaging":
        st.header("💬 Internal Direct Messaging")
        st.caption("Send private messages to coordinators or fellow volunteers.")

        conn = sqlite3.connect(DB_FILE)
        all_users = pd.read_sql_query("SELECT username, full_name, role FROM users WHERE username != ?", conn, params=(curr_user['username'],))
        conn.close()

        if all_users.empty:
            st.info("No other registered users found.")
        else:
            selected_recipient = st.selectbox(
                "Select Recipient to Message:",
                all_users["username"].tolist(),
                format_func=lambda u: f"{all_users.loc[all_users['username']==u, 'full_name'].values[0]} (@{u} - {all_users.loc[all_users['username']==u, 'role'].values[0]})"
            )

            with st.form("send_msg_form"):
                msg_body = st.text_area("Write Your Message:")
                if st.form_submit_button("📨 Send Message"):
                    if msg_body:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)",
                            (curr_user['username'], selected_recipient, msg_body)
                        )
                        conn.commit()
                        conn.close()
                        st.success(f"Message sent to @{selected_recipient}!")
                        st.rerun()

            st.write("---")
            st.subheader("📬 Conversation History with @" + str(selected_recipient))
            conn = sqlite3.connect(DB_FILE)
            msgs = pd.read_sql_query(
                """
                SELECT sender, recipient, message, timestamp FROM messages 
                WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
                ORDER BY id ASC
                """,
                conn,
                params=(curr_user['username'], selected_recipient, selected_recipient, curr_user['username'])
            )
            conn.close()

            if msgs.empty:
                st.caption("No message history with this user yet.")
            else:
                for _, m in msgs.iterrows():
                    align = "👉 **You**" if m['sender'] == curr_user['username'] else f"👈 **@{m['sender']}**"
                    st.markdown(f"{align} *({m['timestamp']})*:\n>{m['message']}")

    # 4. COMMUNITY DISCUSSION BOARD
    elif app_mode == "🗣️ Community Discussion Board":
        st.header("🗣️ Community Discussion Board")
        st.caption("Public Forum for Team Ideas, Q&A, and Community Discussions")

        t_disc1, t_disc2 = st.tabs(["💬 Active Discussion Topics", "➕ Start New Topic"])

        with t_disc1:
            conn = sqlite3.connect(DB_FILE)
            discussions_df = pd.read_sql_query("SELECT id, author, title, category, content, timestamp FROM discussions ORDER BY id DESC", conn)
            conn.close()

            if discussions_df.empty:
                st.info("No discussion topics posted yet. Be the first to start a topic!")
            else:
                for _, d_row in discussions_df.iterrows():
                    with st.expander(f"💬 [{d_row['category']}] {d_row['title']} (by @{d_row['author']} on {d_row['timestamp']})"):
                        st.markdown(d_row['content'])
                        st.write("---")
                        
                        conn = sqlite3.connect(DB_FILE)
                        replies_df = pd.read_sql_query(
                            "SELECT author, content, timestamp FROM discussion_replies WHERE discussion_id = ? ORDER BY id ASC",
                            conn,
                            params=(d_row['id'],)
                        )
                        conn.close()

                        st.markdown("**Replies:**")
                        if replies_df.empty:
                            st.caption("No replies yet.")
                        else:
                            for _, r_row in replies_df.iterrows():
                                st.markdown(f"💬 **@{r_row['author']}** *({r_row['timestamp']})*:\n{r_row['content']}")

                        with st.form(key=f"reply_form_{d_row['id']}"):
                            reply_text = st.text_input("Post a reply:")
                            if st.form_submit_button("Post Reply"):
                                if reply_text:
                                    conn = sqlite3.connect(DB_FILE)
                                    c = conn.cursor()
                                    c.execute(
                                        "INSERT INTO discussion_replies (discussion_id, author, content) VALUES (?, ?, ?)",
                                        (d_row['id'], curr_user['username'], reply_text)
                                    )
                                    conn.commit()
                                    conn.close()
                                    st.success("Reply posted!")
                                    st.rerun()

        with t_disc2:
            with st.form("new_topic_form"):
                top_title = st.text_input("Topic Title:")
                top_cat = st.selectbox("Category:", ["General Discussion", "Fundraising & Outreach", "Civil Legal Navigation", "Heritage Trade & Salvage", "Ideas & Brainstorming"])
                top_content = st.text_area("Topic Description / Discussion Questions:")
                if st.form_submit_button("Publish Discussion Topic"):
                    if top_title and top_content:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO discussions (author, title, category, content) VALUES (?, ?, ?, ?)",
                            (curr_user['full_name'], top_title, top_cat, top_content)
                        )
                        conn.commit()
                        conn.close()
                        st.success("Discussion topic published!")
                        st.rerun()

    # 5. TRAINING & TIER UPGRADE
    elif app_mode == "🎓 Training & Tier Upgrade":
        st.header("🎓 Interactive Micro-Training & Auto-Tier Unlocking")
        st.caption("Complete a 3-Minute Orientation Quiz to Upgrade Your Volunteer Clearance Tier Automatically!")

        st.subheader("🔒 Tier 2 Clearance Quiz: Privacy & Logistics Etiquette")
        with st.form("quiz_tier2_form"):
            q1 = st.radio(
                "1. What is the primary purpose of M.O.M.'s 5-Tab Legal Readiness Binders?",
                [
                    "To store random documents",
                    "To provide standardized, court-admissible proof of compliance for pro se parents",
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
                "3. What is the proper procedure if a participant shares sensitive court or health data?",
                [
                    "Post it on social media",
                    "Maintain strict confidentiality under HIPAA and court navigation rules",
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
                    st.success("🎉 100% Score! You have successfully upgraded to Clearance Tier 2!")
                    st.session_state["user"]["tier"] = new_tier
                    st.rerun()
                else:
                    st.error("Some answers were incorrect. Please review the rules and try again!")

    # 6. KUDOS & LEADERBOARD
    elif app_mode == "🌟 Community Kudos & Leaderboard":
        st.header("🌟 Volunteer Kudos & Monthly Leaderboard")

        col_k1, col_k2 = st.columns(2)

        with col_k1:
            st.subheader("🏆 Monthly Hours Leaderboard")
            conn = sqlite3.connect(DB_FILE)
            df_lead = pd.read_sql_query(
                "SELECT full_name, logged_hours, badges FROM users ORDER BY logged_hours DESC LIMIT 5",
                conn,
            )
            conn.close()
            st.dataframe(df_lead, use_container_width=True)

        with col_k2:
            st.subheader("💬 Send Peer Kudos")
            with st.form("kudos_form"):
                conn = sqlite3.connect(DB_FILE)
                recip_df = pd.read_sql_query("SELECT username, full_name FROM users", conn)
                conn.close()

                k_recip = st.selectbox("Recipient:", recip_df["full_name"].tolist())
                k_msg = st.text_area("Your Appreciation Message:")

                if st.form_submit_button("Post Kudos"):
                    if k_msg:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO kudos (author, recipient, message) VALUES (?, ?, ?)",
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
            "SELECT author, recipient, message, timestamp FROM kudos ORDER BY id DESC LIMIT 5",
            conn,
        )
        conn.close()

        if df_kudos_list.empty:
            st.caption("No shout-outs posted yet. Be the first to appreciate a fellow volunteer!")
        else:
            for idx, k_row in df_kudos_list.iterrows():
                msg_text = k_row['message']
                time_text = k_row['timestamp']
                st.info(f"🌟 **{k_row['author']}** to **{k_row['recipient']}**: \"{msg_text}\" *({time_text})*")

    # 7. SUGGESTION BOX & SUPPORT CENTER
    elif app_mode == "💡 Suggestion Box & Support Center":
        st.header("💡 Suggestion Box & Support Center")

        t_sup1, t_sup2 = st.tabs(["🆘 Request Volunteer Support", "💡 Submit a Suggestion / Idea"])

        with t_sup1:
            st.subheader("🆘 Need Help or Have a Question?")
            st.caption("Submit a support ticket directly to our Coordinator team.")
            
            with st.form("support_ticket_form"):
                s_subj = st.text_input("Subject / Task Code:")
                s_cat = st.selectbox("Issue Category:", ["Task Help / Clarification", "Hours / Credit Inquiry", "Technical / Account Issue", "General Question"])
                s_msg = st.text_area("Describe what you need help with:")

                if st.form_submit_button("Submit Support Ticket"):
                    if s_subj and s_msg:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO support_tickets (volunteer, subject, category, message) VALUES (?, ?, ?, ?)",
                            (curr_user['username'], s_subj, s_cat, s_msg)
                        )
                        conn.commit()
                        conn.close()
                        st.success("Support ticket submitted! A coordinator will review it and reply.")
                        st.rerun()

            st.write("---")
            st.subheader("📋 Your Open & Past Support Tickets")
            conn = sqlite3.connect(DB_FILE)
            my_tickets = pd.read_sql_query("SELECT id, subject, category, status, message, response, timestamp FROM support_tickets WHERE volunteer = ? ORDER BY id DESC", conn, params=(curr_user['username'],))
            conn.close()

            if my_tickets.empty:
                st.caption("You have no support tickets.")
            else:
                for _, t_row in my_tickets.iterrows():
                    with st.expander(f"📌 [{t_row['category']}] {t_row['subject']} — Status: {t_row['status']}"):
                        st.write(f"**Your Request:** {t_row['message']}")
                        st.write(f"**Coordinator Response:** {t_row['response'] if t_row['response'] else 'Pending response...'}")

        with t_sup2:
            st.subheader("💡 Share Your Ideas with Leadership")
            st.caption("We value your input! Submit suggestions for portal features, community outreach, or operational improvements.")

            with st.form("suggestion_form"):
                sug_cat = st.selectbox("Suggestion Category:", ["Portal & Technology", "Outreach & Fundraising", "Volunteer Experience", "Site Operations", "Other Idea"])
                sug_text = st.text_area("Your Suggestion / Feature Idea:")

                if st.form_submit_button("Send Suggestion"):
                    if sug_text:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute(
                            "INSERT INTO suggestions (author, category, suggestion) VALUES (?, ?, ?)",
                            (curr_user['full_name'], sug_cat, sug_text)
                        )
                        conn.commit()
                        conn.close()
                        st.success("Thank you! Your suggestion has been sent to our leadership team.")
                        st.rerun()

    # 8. ONBOARDING (COORDINATORS)
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
                    "INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours, badges) VALUES (?, ?, ?, ?, ?, ?, 0.0, '🌱 Active Contributor')",
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

    # 9. COORDINATOR COMMAND CENTER
    elif app_mode == "🛠️ Coordinator Command Center":
        st.header("🛠️ Coordinator Command Center")

        t_cmd1, t_cmd2, t_cmd3, t_cmd4 = st.tabs(["📝 Intake & Review Hub", "📢 Publish News & Calendar", "🆘 Support Tickets", "💡 Volunteer Suggestions"])

        # TAB 1: INTAKE & REVIEW
        with t_cmd1:
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                st.subheader("➕ Intake & Task Creation")
                raw_text = st.text_area("📝 Paste Raw Request / Email Copy Here (Optional):", placeholder="Paste email or text request copy here...")

                with st.form("pub_form_col1"):
                    p_code = st.text_input("Task ID Code:", placeholder="e.g. FUND-102")
                    p_title = st.text_input("Task Title:")
                    p_cat = st.selectbox(
                        "Functional Category:",
                        [
                            "Community Outreach & Fundraising",
                            "Civil Legal Navigation",
                            "Heritage Trade & Logistics",
                            "Marketing & Web Copy",
                            "Grants & Administration",
                            "Site Operations & Facilities"
                        ]
                    )
                    p_site = st.selectbox(
                        "Site Node Location:",
                        [
                            "Node 1: Dyer St Plaza Hub (Malvern)",
                            "Node 2: Chandler Rd Campus (Traskwood)",
                            "Node 3: Industrial Rd Trade Yard (Malvern)",
                            "Node 4: Mountainaire Historic District (Hot Springs)",
                            "Node 5: Leola Satellite Division (Grant Co)",
                            "Node 6: Army-Navy Hospital Campus (Hot Springs)",
                            "Node 7: Former Majestic Hotel Site (Hot Springs)",
                        ],
                    )
                    p_mod = st.selectbox(
                        "Operational Module:",
                        [
                            "Civil Legal Navigation (ANN)",
                            "Safe Family Contact (PRISM)",
                            "Heritage Trade & Salvage (AHTA)",
                            "Micro-Transit & Fleet (ATMS)",
                            "Technology Lab & Services",
                            "Grants & Master Administration",
                        ],
                    )
                    p_tier = st.slider("Required Clearance Tier:", 1, 3, 1)
                    p_hrs = st.number_input("Service Hours Credit:", value=2.0, step=0.5)
                    p_why = st.text_area("Why This Matters (Context):", value=raw_text if raw_text else "")
                    p_inst = st.text_area("Step-by-Step Instructions:")
                    p_deliv = st.text_area("Expected Deliverable Description:")

                    p_file = st.file_uploader("Attach Reference Resource File (Optional):", type=["pdf", "docx", "xlsx", "csv", "png", "jpg", "zip", "txt"])

                    if st.form_submit_button("Publish Task to Marketplace"):
                        if not p_code or not p_title:
                            st.error("Task Code and Title are required!")
                        else:
                            saved_path, saved_name = "", ""
                            if p_file is not None:
                                saved_name = p_file.name
                                saved_path = os.path.join(UPLOAD_DIR, f"{p_code}_{saved_name}")
                                with open(saved_path, "wb") as f:
                                    f.write(p_file.getbuffer())

                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute(
                                """
                                INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, file_path, file_name, why_it_matters, instructions, expected_deliverable)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (p_code, p_title, p_cat, p_site, p_mod, p_tier, p_hrs, saved_path, saved_name, p_why, p_inst, p_deliv),
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Task {p_code} published!")
                            st.rerun()

            with col_c2:
                st.subheader("👥 Dynamic Task Assignment & Review")
                conn = sqlite3.connect(DB_FILE)
                active_tasks = pd.read_sql_query("SELECT id, task_code, title, category, status, assigned_volunteer FROM tasks WHERE status != 'Approved & Completed'", conn)
                volunteers_df = pd.read_sql_query("SELECT username, full_name, tier FROM users WHERE role = 'Volunteer'", conn)
                conn.close()

                st.markdown("#### ⚡ Manual Task Assignment Override")
                if not active_tasks.empty and not volunteers_df.empty:
                    with st.form("manual_assign_form"):
                        task_choice = st.selectbox(
                            "Select Active Task to Assign:",
                            active_tasks["id"].tolist(),
                            format_func=lambda tid: f"[{active_tasks.loc[active_tasks['id']==tid, 'task_code'].values[0]}] {active_tasks.loc[active_tasks['id']==tid, 'title'].values[0]} ({active_tasks.loc[active_tasks['id']==tid, 'status'].values[0]})"
                        )
                        vol_choice = st.selectbox(
                            "Select Volunteer to Assign:",
                            volunteers_df["username"].tolist(),
                            format_func=lambda uname: f"{volunteers_df.loc[volunteers_df['username']==uname, 'full_name'].values[0]} (@{uname})"
                        )
                        if st.form_submit_button("Assign Task Directly"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE tasks SET status='Claimed / In Progress', assigned_volunteer=? WHERE id=?", (vol_choice, task_choice))
                            conn.commit()
                            conn.close()
                            st.success(f"Task assigned directly to {vol_choice}!")
                            st.rerun()

                st.write("---")
                st.markdown("#### 📥 Review Submissions & Award Hours")
                conn = sqlite3.connect(DB_FILE)
                df_rev = pd.read_sql_query("SELECT * FROM tasks WHERE status = 'Submitted / Under Review'", conn)
                conn.close()

                if df_rev.empty:
                    st.info("No submissions currently pending review.")
                else:
                    for idx, r_row in df_rev.iterrows():
                        with st.expander(f"📥 [{r_row['task_code']}] {r_row['title']} — Submitted by @{r_row['assigned_volunteer']}"):
                            st.write(f"**Time Credit:** {r_row['time_est']} Hrs | **Category:** {r_row['category']}")
                            st.markdown(f"**Submitted Notes / Contact List:**\n```\n{r_row['submission_notes']}\n```")

                            if r_row["proof_file_path"] and os.path.exists(r_row["proof_file_path"]):
                                with open(r_row["proof_file_path"], "rb") as pf:
                                    st.download_button(
                                        label=f"📎 Download Proof File ({r_row['proof_file_name']})",
                                        data=pf.read(),
                                        file_name=r_row["proof_file_name"],
                                        mime="application/octet-stream",
                                        key=f"proof_dl_{r_row['id']}"
                                    )

                            col_rev1, col_rev2 = st.columns(2)
                            if col_rev1.button(f"✅ Approve & Award {r_row['time_est']} Hrs", key=f"app_{r_row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                if "FUND" in r_row["task_code"]:
                                    c.execute("UPDATE tasks SET status='Open', assigned_volunteer=NULL, submission_notes=NULL WHERE id=?", (r_row['id'],))
                                else:
                                    c.execute("UPDATE tasks SET status='Approved & Completed' WHERE id=?", (r_row['id'],))

                                c.execute("UPDATE users SET logged_hours = logged_hours + ? WHERE username=?", (r_row["time_est"], r_row["assigned_volunteer"]))
                                conn.commit()
                                conn.close()
                                st.success(f"Approved! {r_row['time_est']} hours credited to @{r_row['assigned_volunteer']}.")
                                st.rerun()

                            if col_rev2.button("🔄 Return to Open", key=f"reopen_{r_row['id']}"):
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute("UPDATE tasks SET status='Open', assigned_volunteer=NULL WHERE id=?", (r_row['id'],))
                                conn.commit()
                                conn.close()
                                st.warning("Task returned to Open status.")
                                st.rerun()

        # TAB 2: PUBLISH NEWS & CALENDAR
        with t_cmd2:
            col_nc1, col_nc2 = st.columns(2)

            with col_nc1:
                st.subheader("📢 Post Official Announcement")
                with st.form("post_announcement_form"):
                    ann_title = st.text_input("Announcement Title:")
                    ann_cat = st.selectbox("Category:", ["General Announcement", "Organization Update", "Urgent Call to Action", "Event Highlight"])
                    ann_body = st.text_area("Announcement Content:")
                    if st.form_submit_button("Publish Announcement"):
                        if ann_title and ann_body:
                            date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("INSERT INTO announcements (title, content, date_posted, category) VALUES (?, ?, ?, ?)", (ann_title, ann_body, date_str, ann_cat))
                            conn.commit()
                            conn.close()
                            st.success("Announcement published!")
                            st.rerun()

            with col_nc2:
                st.subheader("📅 Add Calendar Event")
                with st.form("add_event_form"):
                    evt_title = st.text_input("Event Title:")
                    evt_date = st.date_input("Event Date:")
                    evt_time = st.text_input("Time String:", value="6:00 PM - 7:30 PM")
                    evt_loc = st.text_input("Location:", value="Node 1: Plaza Hub / Virtual Zoom")
                    evt_desc = st.text_area("Description / Details:")
                    if st.form_submit_button("Add Event to Calendar"):
                        if evt_title:
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("INSERT INTO calendar_events (title, event_date, time_str, location, description) VALUES (?, ?, ?, ?, ?)", (evt_title, str(evt_date), evt_time, evt_loc, evt_desc))
                            conn.commit()
                            conn.close()
                            st.success("Event added to Calendar!")
                            st.rerun()

        # TAB 3: SUPPORT TICKETS
        with t_cmd3:
            st.subheader("🆘 Manage Volunteer Support Tickets")
            conn = sqlite3.connect(DB_FILE)
            tickets_df = pd.read_sql_query("SELECT id, volunteer, subject, category, message, status, response, timestamp FROM support_tickets ORDER BY id DESC", conn)
            conn.close()

            if tickets_df.empty:
                st.info("No support tickets submitted.")
            else:
                for _, tk in tickets_df.iterrows():
                    with st.expander(f"📌 Ticket #{tk['id']}: [{tk['category']}] {tk['subject']} (by @{tk['volunteer']}) — Status: {tk['status']}"):
                        st.write(f"**Volunteer Message:** {tk['message']}")
                        st.caption(f"Submitted on: {tk['timestamp']}")
                        
                        with st.form(key=f"resp_ticket_form_{tk['id']}"):
                            t_resp = st.text_area("Write Response to Volunteer:", value=tk['response'] if tk['response'] else "")
                            t_stat = st.selectbox("Update Status:", ["Open / Pending", "In Progress", "Resolved / Closed"], index=2 if tk['status']=="Resolved / Closed" else 0)
                            if st.form_submit_button("Send Response & Update Ticket"):
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute("UPDATE support_tickets SET response=?, status=? WHERE id=?", (t_resp, t_stat, tk['id']))
                                conn.commit()
                                conn.close()
                                st.success("Ticket updated!")
                                st.rerun()

        # TAB 4: SUGGESTIONS
        with t_cmd4:
            st.subheader("💡 Review Volunteer Suggestions & Ideas")
            conn = sqlite3.connect(DB_FILE)
            sug_df = pd.read_sql_query("SELECT id, author, category, suggestion, status, timestamp FROM suggestions ORDER BY id DESC", conn)
            conn.close()

            if sug_df.empty:
                st.info("No suggestions submitted yet.")
            else:
                st.dataframe(sug_df, use_container_width=True)
