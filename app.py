import hashlib
import os
import pandas as pd
import sqlalchemy
import streamlit as st
from fpdf import FPDF
from supabase import create_client, Client

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

@st.cache_resource
def get_supabase_client() -> Client:
    # Uses URL and Anon Key from Streamlit Secrets or Environment Variables
    url = st.secrets["postgres"]["url"].split("@")[1].split("/")[0] if "postgres" in st.secrets else ""
    # Fallback to direct supabase URL / key if stored in secrets
    supabase_url = st.secrets.get("SUPABASE_URL", f"https://{url}")
    supabase_key = st.secrets.get("SUPABASE_KEY", st.secrets.get("postgres", {}).get("password", ""))
    return create_client(supabase_url, supabase_key)

@st.cache_data
def generate_pdf_letter(full_name, username, total_hours, tier, badges):
    # Performance Optimization: Cache generated PDF bytes using Streamlit cache_data to prevent
    # re-executing expensive FPDF layout and string formatting on every Streamlit script rerun.
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    pdf.set_fill_color(46, 26, 71)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "MENDING OUR MISTAKES, INC.", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(
        0, 5, "Restoring Families. Rebuilding Stability. Renewing Communities.", ln=True, align="C"
    )
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(46, 26, 71)
    pdf.cell(0, 10, "OFFICIAL SERVICE VERIFICATION & IMPACT LETTER", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(45, 55, 72)
    date_str = pd.Timestamp.now().strftime("%B %d, %Y")
    pdf.cell(0, 8, clean_pdf_text(f"Date: {date_str}"), ln=True)
    record_id = hashlib.md5(username.encode()).hexdigest()[:8].upper()
    pdf.cell(0, 8, clean_pdf_text(f"Volunteer Record ID: MOM-VOL-{record_id}"), ln=True)
    pdf.ln(5)
    clean_name = clean_pdf_text(full_name)
    clean_user = clean_pdf_text(username)
    clean_badge = clean_pdf_text(badges) if badges else "Active Contributor"
    text_body = (
        f"This letter serves as official verification that {clean_name}"
        f" ({clean_user}) has actively contributed valuable volunteer service"
        " hours to Mending Our Mistakes, Inc. (M.O.M.) across our integrated"
        " Continuum of Care (CoC) and regional site network in Central Arkansas.\n\n"
        "Verified Service Credentials:\n"
        f" - Total Authenticated Service Hours: {total_hours:.1f} Hours\n"
        f" - Approved Security & Clearance Level: Tier {tier}\n"
        f" - Earned Badges & Distinctions: {clean_badge}\n\n"
        f"Through these dedicated service efforts, {clean_name} has directly supported our"
        " core mission of reunifying court-involved parents, delivering civil"
        " legal navigation, managing heritage trade salvage, and expanding"
        " family stabilization services.\n\n"
        "This service record is officially certified in the M.O.M. Master Operations Database"
        " and is valid for academic service credits, court compliance reporting,"
        " professional portfolios, and community honors."
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
    return pdf.output(dest="S").encode("latin-1")

@st.cache_resource
def get_db_engine():
    db_url = st.secrets["postgres"]["url"]
    return sqlalchemy.create_engine(db_url)

def run_query(query, params=None):
    engine = get_db_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(sqlalchemy.text(query), conn, params=params)

def execute_db(query, params=None):
    engine = get_db_engine()
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text(query), params or {})

st.set_page_config(
    page_title="Mending Our Mistakes, Inc. — Volunteer Portal",
    page_icon="💜",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');
    body, .stApp {background-color: #FAFAFC; font-family: 'Inter', sans-serif; color: #2D3748; }
    .mom-header {background: linear-gradient(135deg, #2E1A47 0%, #153D62 100%); padding: 2rem 2rem; border-radius: 12px; color: #FFFFFF; margin-bottom: 1.5rem; box-shadow: 0 6px 20px rgba(46, 26, 71, 0.15); border-bottom: 4px solid #B47A19; }
    .mom-header h1 {font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 700; color: #FFFFFF !important; margin: 0 0 0.3rem 0; }
    .mom-header p {font-family: 'Merriweather', serif; font-size: 1rem; color: #E0D7EA; margin: 0; }
    .mom-badge-pill {background-color: #F3EBF9; color: #5B2C6F; font-family: 'Inter', sans-serif; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 3px 12px; border-radius: 50px; display: inline-block; margin-bottom: 0.6rem; }
    .mom-tag-pill {background-color: #E2E8F0; color: #2D3748; font-family: 'Inter', sans-serif; font-size: 0.75rem; font-weight: 600; padding: 3px 10px; border-radius: 6px; display: inline-block; margin-right: 6px; }
    h1, h2, h3, .stHeader {font-family: 'Playfair Display', serif !important; color: #2E1A47 !important; }
    .clean-summary-card {background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #2E1A47; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03); transition: all 0.2s ease-in-out; }
    .clean-summary-card:hover {border-left-color: #B47A19; box-shadow: 0 4px 12px rgba(46, 26, 71, 0.08); }
    .clean-card-title {font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #2E1A47; margin: 0 0 0.3rem 0; }
    .clean-card-meta {font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #4A5568; margin: 0; }
    .stButton>button, div.stDownloadButton>button {background-color: #2E1A47 !important; color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; border-radius: 6px !important; border: none !important; }
    .stButton>button:hover, div.stDownloadButton>button:hover {background-color: #B47A19 !important; box-shadow: 0 3px 10px rgba(180, 122, 25, 0.25) !important; }
    section[data-testid="stSidebar"] {background-color: #F8FAFC !important; border-right: 1px solid #E0D7EA !important; }
    .stExpander {border: 1px solid #E2E8F0 !important; border-radius: 8px !important; background-color: #FFFFFF !important; margin-bottom: 0.8rem !important; }
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
        user_df = run_query(
            "SELECT id, username, full_name, email, role, tier, logged_hours, badges FROM users WHERE username = :u AND password_hash = :p",
            params={"u": login_user.strip(), "p": hash_pass(login_pass)},
        )
        if not user_df.empty:
            user_row = user_df.iloc[0]
            st.session_state["logged_in"] = True
            st.session_state["user"] = {
                "id": user_row["id"],
                "username": user_row["username"],
                "full_name": user_row["full_name"],
                "email": user_row["email"],
                "role": user_row["role"],
                "tier": user_row["tier"],
                "logged_hours": float(user_row["logged_hours"]),
                "badges": user_row["badges"],
            }
            st.sidebar.success(f"Welcome back, {user_row['full_name']}!")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")
    st.sidebar.info(
        "💡 Default Logins:\n- Coordinator: `admin` / `MendingOurMistakes25`\n- Volunteer: `volunteer1` / `MendingOurMistakes25`"
    )
else:
    user = st.session_state["user"]
    st.sidebar.markdown(f"### 👤 Logged in as:\n**{user['full_name']}**")
    st.sidebar.markdown(f"**Role:** `{user['role']}`")
    st.sidebar.markdown(f"**Approved Tier:** `Tier {user['tier']}`")
    st.sidebar.markdown(f"**Logged Hours:** `{user['logged_hours']:.1f} hrs`")
    st.sidebar.markdown(f"**Badges:** {user['badges'] or '🌱 Active Contributor'}")
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
    st.warning("👈 Please sign in using the sidebar to access your volunteer workspace.")
    st.markdown(
        """
        ### Welcome to the M.O.M. Volunteer Network!
        Our portal provides secure, tiered access to task cards, resource documents, micro-training, community discussions, and service hour certification.
        """
    )
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
                data=pdf_bytes,
                file_name=f"MOM_Service_Verification_{curr_user['username']}.pdf",
                mime="application/pdf",
            )
        st.write("---")
        st.subheader("📋 Volunteer Task Marketplace")
        st.caption(
            "Clean summary cards for fast scanning. Click '🔽 View Details & Action Controls' on any task to see instructions, attachments, and claim options!"
        )

        categories_df = run_query("SELECT DISTINCT category FROM tasks")
        all_categories = ["All Categories"] + [
            c for c in categories_df["category"].dropna().tolist() if c
        ]
        selected_cat = st.selectbox("🔍 Filter Tasks by Category:", all_categories)

        if selected_cat == "All Categories":
            df_tasks = run_query(
                "SELECT * FROM tasks WHERE tier_required <= :tier AND (status = 'Open' OR assigned_volunteer = :u) ORDER BY id DESC",
                params={"tier": curr_user["tier"], "u": curr_user["username"]},
            )
        else:
            df_tasks = run_query(
                "SELECT * FROM tasks WHERE tier_required <= :tier AND category = :cat AND (status = 'Open' OR assigned_volunteer = :u) ORDER BY id DESC",
                params={
                    "tier": curr_user["tier"],
                    "cat": selected_cat,
                    "u": curr_user["username"],
                },
            )

        if df_tasks.empty:
            st.info("No tasks currently available matching your selected filters.")
        else:
            for idx, row in df_tasks.iterrows():
                is_claimed_by_me = row["assigned_volunteer"] == curr_user["username"]
                status_icon = (
                    "🟢 OPEN TASK"
                    if row["status"] == "Open"
                    else f"🟡 YOUR TASK ({row['status']})"
                )

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

                exp_label = (
                    "📌 Manage Your Claimed Task & Submissions"
                    if is_claimed_by_me
                    else "🔽 View Details, Instructions & Claim Task"
                )
                with st.expander(exp_label, expanded=is_claimed_by_me):
                    st.markdown(f"#### 💡 Why This Matters\n{row['why_it_matters']}")
                    if row["file_path"] and str(row["file_path"]).startswith("http"):
                        st.markdown(f"[📥 Download Reference Resource File ({row['file_name']})]({row['file_path']})")
                    elif row["file_path"] and os.path.exists(row["file_path"]):
                        with open(row["file_path"], "rb") as f:
                            st.download_button(
                                label=f"📥 Download Reference Resource File ({row['file_name']})",
                                data=f.read(),
                                file_name=row["file_name"],
                                mime="application/octet-stream",
                                key=f"dl_{row['id']}_{row['task_code']}",
                            )
                    st.markdown(f"**Step-by-Step Instructions:**\n{row['instructions']}")
                    st.markdown(f"**Expected Deliverable:**\n{row['expected_deliverable']}")
                    st.write("---")

                    if row["status"] == "Open":
                        if st.button(
                            f"🙋 Claim Task [{row['task_code']}]", key=f"claim_{row['id']}"
                        ):
                            execute_db(
                                "UPDATE tasks SET status='Claimed / In Progress', assigned_volunteer=:u WHERE id=:id",
                                params={"u": curr_user["username"], "id": row["id"]},
                            )
                            st.success(
                                f"Task {row['task_code']} claimed! You can now complete the work and submit your proof below."
                            )
                            st.rerun()
                    elif is_claimed_by_me:
                        st.info(f"📌 Task Status: **{row['status']}**")
                        col_rel1, _ = st.columns([1, 2])
                        with col_rel1:
                            if st.button(
                                f"↩️️ Release Task Back to Marketplace",
                                key=f"rel_{row['id']}",
                            ):
                                execute_db(
                                    "UPDATE tasks SET status='Open', assigned_volunteer=NULL, submission_notes=NULL WHERE id=:id",
                                    params={"id": row["id"]},
                                )
                                st.warning(
                                    f"Task {row['task_code']} released back to the public marketplace."
                                )
                                st.rerun()
                        with st.form(key=f"sub_form_{row['id']}"):
                            sub_notes = st.text_area(
                                "Edit / Submit Completed Work / Notes / Email List:",
                                value=row["submission_notes"]
                                if row["submission_notes"]
                                else "",
                                placeholder="List the 5 organizations contacted or paste your completion notes here...",
                            )
                            proof_file = st.file_uploader(
                                "📎 Upload PDF or Screenshot Proof of Sent Emails / Output (Optional):",
                                type=["pdf", "png", "jpg", "jpeg", "docx"],
                            )
                            btn_label = (
                                "✏️ Update Submission"
                                if row["status"] == "Submitted / Under Review"
                                else "🚀 Submit Work for Credit & Review"
                            )
                            if st.form_submit_button(btn_label):
                                if not sub_notes:
                                    st.error("Please enter completion notes before submitting!")
                                else:
                                    p_path = row["proof_file_path"]
                                    p_name = row["proof_file_name"]
                                    if proof_file is not None:
                                        p_name = proof_file.name
                                        try:
                                            # Direct Cloud Upload to Supabase Storage Bucket
                                            file_bytes = proof_file.getvalue()
                                            storage_path = f"proofs/{curr_user['username']}_{p_name}"
                                            client = get_supabase_client()
                                            client.storage.from_("proof_files").upload(
                                                path=storage_path,
                                                file=file_bytes,
                                                file_options={"content-type": proof_file.type, "upsert": "true"}
                                            )
                                            p_path = client.storage.from_("proof_files").get_public_url(storage_path)
                                        except Exception as e:
                                            # Local fallback if bucket is offline
                                            p_path = os.path.join(
                                                UPLOAD_DIR,
                                                f"proof_{curr_user['username']}_{p_name}",
                                            )
                                            with open(p_path, "wb") as pf:
                                                pf.write(proof_file.getbuffer())

                                    execute_db(
                                        """
                                        UPDATE tasks 
                                        SET status='Submitted / Under Review', submission_notes=:notes, proof_file_path=:path, proof_file_name=:name 
                                        WHERE id=:id
                                        """,
                                        params={
                                            "notes": sub_notes,
                                            "path": p_path,
                                            "name": p_name,
                                            "id": row["id"],
                                        },
                                    )
                                    st.success(
                                        f"Submission updated for {row['task_code']}! Coordinator will review and award your hours."
                                    )
                                    st.rerun()

        st.write("---")
        st.subheader("📜 Your Submitted & Approved Task History")
        df_my_history = run_query(
            "SELECT task_code, title, time_est, status, submission_notes FROM tasks WHERE assigned_volunteer = :u",
            params={"u": curr_user["username"]},
        )
        if df_my_history.empty:
            st.caption("You haven't submitted any tasks yet.")
        else:
            st.dataframe(df_my_history, use_container_width=True)

    elif app_mode == "📊 Live Impact & News Dashboard":
        st.header("📊 M.O.M. Community Impact & News Dashboard")
        st.caption(
            "Stay Informed on Organization News, Upcoming Calendar Events & Strategic Milestones"
        )
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⚖️ Legal Binders Checked", "48 Binders", "+12 This Month")
        m2.metric("🧸 Good360 Care Packages", "185 Families", "+35 Distributed")
        m3.metric("🪵 AHTA Reclaimed Materials", "3,400 sq. ft.", "+800 sq. ft.")
        m4.metric("🚐 Micro-Transit Rides", "112 Trips", "Saline & Hot Spring")
        st.write("---")
        col_dash1, col_dash2 = st.columns(2)
        with col_dash1:
            st.subheader("📢 Official Announcements & Updates")
            df_ann = run_query(
                "SELECT title, content, date_posted, category FROM announcements ORDER BY id DESC LIMIT 5"
            )
            if df_ann.empty:
                st.caption("No announcements posted yet.")
            else:
                for _, a_row in df_ann.iterrows():
                    with st.expander(
                        f"📌 [{a_row['category']}] {a_row['title']} ({a_row['date_posted']})",
                        expanded=False,
                    ):
                        st.write(a_row["content"])
            st.write("---")
            st.subheader("🚀 Strategic Milestones & Roadmap")
            with st.expander("📍 View M.O.M. 3-Phase Expansion Roadmap"):
                st.markdown(
                    """
                    * **Phase 1: Pre-Launch Foundation (Current)**
                      * 5-Tab Legal Readiness Binder standardization.
                      * Google Ad Grant compliance repair for `mendingourmistakes.org`.
                      * Initial Good360 Requisition & Community Outreach Drive.
                    * **Phase 2: Regional Site Node Activation (Upcoming)**
                      * Node 1 (Malvern Plaza Hub) & Node 2 (Traskwood Campus) staging.
                      * Heritage Trade & Salvage (AHTA) depot inventory cataloging.
                    * **Phase 3: Full Continuum of Care (CoC) Launch**
                      * Court Appointed Lived-Experience Specialists (CALES) deployment.
                    """
                )
        with col_dash2:
            st.subheader("📅 Upcoming Calendar & Schedule")
            df_cal = run_query(
                "SELECT title, event_date, time_str, location, description FROM calendar_events ORDER BY id ASC LIMIT 5"
            )
            if df_cal.empty:
                st.caption("No calendar events scheduled yet.")
            else:
                for _, c_row in df_cal.iterrows():
                    with st.expander(f"🗓️ {c_row['event_date']} — {c_row['title']}"):
                        st.markdown(f"**Time:** {c_row['time_str']}")
                        st.markdown(f"**Location:** {c_row['location']}")
                        st.write(c_row["description"])
            st.write("---")
            st.subheader("🗳️ Volunteer Pulse Check")
            with st.expander("🗳️ Vote: Preferred Workday Schedule"):
                with st.form("pulse_poll_form"):
                    poll_opt = st.radio(
                        "Select your preferred time slot:",
                        [
                            "Weekday Evenings (6:00 PM - 8:00 PM)",
                            "Saturday Mornings (9:00 AM - 12:00 PM)",
                            "Self-Paced / Flexible Remote Hours",
                        ],
                    )
                    if st.form_submit_button("Submit Vote"):
                        execute_db(
                            "INSERT INTO poll_votes (username, option_chosen) VALUES (:u, :o)",
                            params={"u": curr_user["username"], "o": poll_opt},
                        )
                        st.success("Thank you for your feedback! Vote recorded.")

    elif app_mode == "💬 Direct Messaging":
        st.header("💬 Internal Direct Messaging")
        st.caption("Send private messages to coordinators or fellow volunteers.")
        all_users = run_query(
            "SELECT username, full_name, role FROM users WHERE username != :u",
            params={"u": curr_user["username"]},
        )
        if all_users.empty:
            st.info("No other registered users found.")
        else:
            selected_recipient = st.selectbox(
                "Select Recipient to Message:",
                all_users["username"].tolist(),
                format_func=lambda u: f"{all_users.loc[all_users['username']==u, 'full_name'].values[0]} (@{u} - {all_users.loc[all_users['username']==u, 'role'].values[0]})",
            )
            with st.form("send_msg_form"):
                msg_body = st.text_area("Write Your Message:")
                if st.form_submit_button("📨 Send Message"):
                    if msg_body:
                        execute_db(
                            "INSERT INTO messages (sender, recipient, message) VALUES (:s, :r, :m)",
                            params={
                                "s": curr_user["username"],
                                "r": selected_recipient,
                                "m": msg_body,
                            },
                        )
                        st.success(f"Message sent to @{selected_recipient}!")
                        st.rerun()
            st.write("---")
            st.subheader(f"📬 Conversation History with @{selected_recipient}")
            msgs = run_query(
                """
                SELECT sender, recipient, message, timestamp 
                FROM messages 
                WHERE (sender = :u AND recipient = :r) OR (sender = :r AND recipient = :u) 
                ORDER BY id ASC
                """,
                params={"u": curr_user["username"], "r": selected_recipient},
            )
            if msgs.empty:
                st.caption("No message history with this user yet.")
            else:
                for _, m in msgs.iterrows():
                    align = (
                        "👉 **You**"
                        if m["sender"] == curr_user["username"]
                        else f"👈 **@{m['sender']}**"
                    )
                    st.markdown(f"{align} *({m['timestamp']})*:\n>{m['message']}")

    elif app_mode == "🗣️ Community Discussion Board":
        st.header("🗣️ Community Discussion Board")
        st.caption("Public Forum for Team Ideas, Q&A, and Community Discussions")
        t_disc1, t_disc2 = st.tabs(["💬 Active Discussion Topics", "➕ Start New Topic"])
        with t_disc1:
            discussions_df = run_query(
                "SELECT id, author, title, category, content, timestamp FROM discussions ORDER BY id DESC"
            )
            if discussions_df.empty:
                st.caption("No discussions started yet. Be the first to start a topic!")
            else:
                # Performance Optimization: Batch fetch all discussion replies in a single query
                # to eliminate the N+1 database roundtrips per discussion render.
                all_replies_df = run_query(
                    "SELECT discussion_id, author, content, timestamp FROM discussion_replies ORDER BY id ASC"
                )
                for _, d_row in discussions_df.iterrows():
                    with st.expander(
                        f"📌 [{d_row['category']}] {d_row['title']} — by @{d_row['author']}"
                    ):
                        st.write(d_row["content"])
                        st.caption(f"Posted: {d_row['timestamp']}")
                        st.write("---")
                        replies_df = (
                            all_replies_df[all_replies_df["discussion_id"] == d_row["id"]]
                            if not all_replies_df.empty and "discussion_id" in all_replies_df.columns
                            else pd.DataFrame()
                        )
                        if not replies_df.empty:
                            st.markdown("**Replies:**")
                            for _, r_row in replies_df.iterrows():
                                st.markdown(
                                    f"💬 **@{r_row['author']}**: {r_row['content']} *({r_row['timestamp']})*"
                                )
                        with st.form(key=f"reply_form_{d_row['id']}"):
                            reply_text = st.text_input("Add a reply:")
                            if st.form_submit_button("Reply"):
                                if reply_text:
                                    execute_db(
                                        "INSERT INTO discussion_replies (discussion_id, author, content) VALUES (:d_id, :a, :c)",
                                        params={
                                            "d_id": d_row["id"],
                                            "a": curr_user["username"],
                                            "c": reply_text,
                                        },
                                    )
                                    st.success("Reply posted!")
                                    st.rerun()
        with t_disc2:
            with st.form("new_topic_form"):
                topic_title = st.text_input("Topic Title:")
                topic_cat = st.selectbox(
                    "Category:",
                    [
                        "General Discussion",
                        "Civil Legal Navigation",
                        "Heritage Salvage (AHTA)",
                        "Community Outreach",
                        "Technical Support",
                    ],
                )
                topic_content = st.text_area("Topic Content / Details:")
                if st.form_submit_button("Post New Discussion"):
                    if topic_title and topic_content:
                        execute_db(
                            "INSERT INTO discussions (author, title, category, content) VALUES (:a, :t, :c, :cnt)",
                            params={
                                "a": curr_user["username"],
                                "t": topic_title,
                                "c": topic_cat,
                                "cnt": topic_content,
                            },
                        )
                        st.success("Discussion topic posted!")
                        st.rerun()

    elif app_mode == "🎓 Training & Tier Upgrade":
        st.header("🎓 Micro-Training & Security Tier Clearance")
        st.caption("Complete modules to unlock higher security clearance and advanced operational tasks.")
        st.subheader(f"Current Clearance Level: Tier {curr_user['tier']}")
        t_tr1, t_tr2 = st.tabs(["📚 Tier 2 Upgrade Course", "🔐 Tier 3 Coordinator Orientation"])
        with t_tr1:
            st.markdown(
                """
                ### 📖 Module 1: Continuum of Care (CoC) & Confidentiality Protocols
                Learn essential procedures for handing Sensitive Legal Records, Parent Case Notes, and Restorative Care Plans.
                """
            )
            with st.form("tier2_exam"):
                q1 = st.radio(
                    "1. How should volunteer legal notes be stored?",
                    [
                        "On personal phone memory",
                        "In the M.O.M. Master Operations Database",
                        "Emailed to personal accounts",
                    ],
                )
                if st.form_submit_button("Submit Tier 2 Clearance Exam"):
                    if q1 == "In the M.O.M. Master Operations Database":
                        new_tier = max(curr_user["tier"], 2)
                        execute_db(
                            "UPDATE users SET tier = :t WHERE username = :u",
                            params={"t": new_tier, "u": curr_user["username"]},
                        )
                        st.session_state["user"]["tier"] = new_tier
                        st.success("Congratulations! You have been upgraded to Tier 2 Clearance.")
                        st.rerun()
                    else:
                        st.error("Incorrect answer. Please review the material and try again.")
        with t_tr2:
            st.markdown(
                """
                ### 📖 Module 2: Site Node Coordination & Operational Leadership
                Covers logistics, Good360 requisition management, and volunteer supervision across Malvern & Traskwood site nodes.
                """
            )

    elif app_mode == "🌟 Community Kudos & Leaderboard":
        st.header("🌟 Community Kudos & Volunteer Recognition")
        st.caption("Celebrate achievements, send appreciation, and track community impact!")
        col_kd1, col_kd2 = st.columns([1, 1])
        with col_kd1:
            st.subheader("👏 Send Kudos")
            all_users = run_query(
                "SELECT username, full_name FROM users WHERE username != :u",
                params={"u": curr_user["username"]},
            )
            if not all_users.empty:
                kudo_recipient = st.selectbox(
                    "Recipient:",
                    all_users["username"].tolist(),
                    format_func=lambda u: f"{all_users.loc[all_users['username']==u, 'full_name'].values[0]} (@{u})",
                )
                kudo_msg = st.text_area("Recognition Message:")
                if st.button("🌟 Award Kudos"):
                    if kudo_msg:
                        execute_db(
                            "INSERT INTO kudos (author, recipient, message) VALUES (:a, :r, :m)",
                            params={
                                "a": curr_user["username"],
                                "r": kudo_recipient,
                                "m": kudo_msg,
                            },
                        )
                        st.success("Kudos awarded successfully!")
                        st.rerun()
        with col_kd2:
            st.subheader("🏆 Volunteer Leaderboard")
            leaderboard_df = run_query(
                "SELECT full_name, role, logged_hours, badges FROM users ORDER BY logged_hours DESC LIMIT 10"
            )
            st.dataframe(leaderboard_df, use_container_width=True)

    elif app_mode == "💡 Suggestion Box & Support Center":
        st.header("💡 Suggestion Box & Technical Support")
        st.caption("Submit ideas for improving portal features or open support tickets for technical assistance.")
        t_sup1, t_sup2 = st.tabs(["💡 Submit Suggestion", "🆘 Open Support Ticket"])
        with t_sup1:
            with st.form("sug_form"):
                sug_cat = st.selectbox(
                    "Suggestion Category:",
                    [
                        "General Suggestion",
                        "Portal Feature Request",
                        "Site Node Logistics",
                        "Training Content",
                    ],
                )
                sug_text = st.text_area("Your Ideas & Feedback:")
                if st.form_submit_button("Submit Feedback"):
                    if sug_text:
                        execute_db(
                            "INSERT INTO suggestions (author, category, suggestion) VALUES (:a, :c, :s)",
                            params={
                                "a": curr_user["username"],
                                "c": sug_cat,
                                "s": sug_text,
                            },
                        )
                        st.success("Thank you! Your feedback has been submitted to portal coordinators.")
        with t_sup2:
            with st.form("supp_form"):
                supp_subj = st.text_input("Issue Subject:")
                supp_cat = st.selectbox(
                    "Issue Category:",
                    [
                        "General Inquiry",
                        "Account / Password Help",
                        "Bug Report",
                        "Task Submission Issue",
                    ],
                )
                supp_msg = st.text_area("Describe the issue in detail:")
                if st.form_submit_button("Submit Support Ticket"):
                    if supp_subj and supp_msg:
                        execute_db(
                            "INSERT INTO support_tickets (volunteer, subject, category, message) VALUES (:v, :s, :c, :m)",
                            params={
                                "v": curr_user["username"],
                                "s": supp_subj,
                                "c": supp_cat,
                                "m": supp_msg,
                            },
                        )
                        st.success("Support ticket created. A coordinator will follow up with you.")

    elif app_mode == "👥 Volunteer Onboarding" and curr_user["role"] in ["Coordinator", "Admin"]:
        st.header("👥 Volunteer Onboarding & Account Management")
        st.caption("Create new volunteer accounts and set initial clearance tiers.")
        with st.form("create_user_form"):
            new_u = st.text_input("New Username:")
            new_p = st.text_input("Default Password:", value="MendingOurMistakes25", type="password")
            new_fn = st.text_input("Full Name:")
            new_em = st.text_input("Email Address:")
            new_role = st.selectbox("Assigned Role:", ["Volunteer", "Coordinator", "Admin"])
            new_tier = st.slider("Approved Clearance Tier:", 1, 3, 1)
            if st.form_submit_button("Register Account"):
                if new_u and new_p and new_fn and new_em:
                    try:
                        execute_db(
                            """
                            INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours, badges)
                            VALUES (:u, :p, :fn, :em, :r, :t, 0.0, '🌱 Active Contributor')
                            """,
                            params={
                                "u": new_u.strip(),
                                "p": hash_pass(new_p),
                                "fn": new_fn.strip(),
                                "em": new_em.strip(),
                                "r": new_role,
                                "t": new_tier,
                            },
                        )
                        st.success(f"Account for @{new_u} created successfully!")
                    except Exception as e:
                        st.error(f"Error creating account: {e}")

    elif app_mode == "🛠️ Coordinator Command Center" and curr_user["role"] in ["Coordinator", "Admin"]:
        st.header("🛠 Coordinator Command Center")
        st.caption("Review submissions, award hours, and manage marketplace tasks.")
        t_cmd1, t_cmd2, t_cmd3 = st.tabs(
            ["📥 Review Work Submissions", "➕ Post New Task Card", "📊 Master Volunteer Directory"]
        )
        with t_cmd1:
            pending_df = run_query(
                "SELECT * FROM tasks WHERE status = 'Submitted / Under Review' ORDER BY id ASC"
            )
            if pending_df.empty:
                st.info("No task submissions currently pending review.")
            else:
                for _, p_row in pending_df.iterrows():
                    with st.expander(
                        f"📌 Task [{p_row['task_code']}] {p_row['title']} — Submitted by @{p_row['assigned_volunteer']}"
                    ):
                        st.markdown(f"**Submitted Notes / Output:**\n{p_row['submission_notes']}")
                        if p_row["proof_file_path"] and str(p_row["proof_file_path"]).startswith("http"):
                            st.markdown(f"[📥 View / Download Proof Attachment ({p_row['proof_file_name']})]({p_row['proof_file_path']})")
                        elif p_row["proof_file_path"] and os.path.exists(p_row["proof_file_path"]):
                            with open(p_row["proof_file_path"], "rb") as pf:
                                st.download_button(
                                    label=f"📥 Download Proof Attachment ({p_row['proof_file_name']})",
                                    data=pf.read(),
                                    file_name=p_row["proof_file_name"],
                                    key=f"cmd_dl_{p_row['id']}",
                                )
                        col_ap1, col_ap2 = st.columns(2)
                        with col_ap1:
                            if st.button(
                                f"✅ Approve & Award {p_row['time_est']} Hours",
                                key=f"app_{p_row['id']}",
                            ):
                                execute_db(
                                    "UPDATE tasks SET status = 'Completed & Approved' WHERE id = :id",
                                    params={"id": p_row["id"]},
                                )
                                execute_db(
                                    "UPDATE users SET logged_hours = logged_hours + :h WHERE username = :u",
                                    params={
                                        "h": p_row["time_est"],
                                        "u": p_row["assigned_volunteer"],
                                    },
                                )
                                st.success(f"Approved {p_row['task_code']} and awarded hours!")
                                st.rerun()
                        with col_ap2:
                            if st.button(
                                f"🔴 Reject / Request Revision", key=f"rej_{p_row['id']}"
                            ):
                                execute_db(
                                    "UPDATE tasks SET status = 'Revision Requested' WHERE id = :id",
                                    params={"id": p_row["id"]},
                                )
                                st.warning("Submission returned for revision.")
                                st.rerun()
        with t_cmd2:
            with st.form("new_task_form"):
                tc = st.text_input("Task Code (e.g. COC-301):")
                tt = st.text_input("Task Title:")
                tcat = st.selectbox(
                    "Category:",
                    [
                        "Community Outreach & Fundraising",
                        "Civil Legal Navigation",
                        "Heritage Salvage (AHTA)",
                        "Administrative & IT",
                    ],
                )
                tsite = st.selectbox(
                    "Site Node:",
                    [
                        "Malvern Plaza Hub",
                        "Traskwood Campus",
                        "Remote / Virtual",
                        "Central Arkansas Regional",
                    ],
                )
                tmod = st.text_input("Module Name (e.g., Continuum of Care):")
                tier_req = st.slider("Required Clearance Tier:", 1, 3, 1)
                time_e = st.number_input("Estimated Hours Credit:", min_value=0.5, value=2.0, step=0.5)
                why_m = st.text_area("Why It Matters:")
                inst = st.text_area("Step-by-Step Instructions:")
                exp_del = st.text_area("Expected Deliverable:")
                if st.form_submit_button("Post Task Card to Marketplace"):
                    if tc and tt and why_m and inst and exp_del:
                        execute_db(
                            """
                            INSERT INTO tasks (task_code, title, category, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable, status)
                            VALUES (:tc, :tt, :cat, :site, :mod, :tier, :time_e, :why, :inst, :exp, 'Open')
                            """,
                            params={
                                "tc": tc,
                                "tt": tt,
                                "cat": tcat,
                                "site": tsite,
                                "mod": tmod,
                                "tier": tier_req,
                                "time_e": time_e,
                                "why": why_m,
                                "inst": inst,
                                "exp": exp_del,
                            },
                        )
                        st.success(f"Task Card {tc} successfully posted!")
                        st.rerun()
        with t_cmd3:
            st.subheader("📊 Master Volunteer Directory")
            v_df = run_query("SELECT id, username, full_name, email, role, tier, logged_hours, badges FROM users ORDER BY id ASC")
            st.dataframe(v_df, use_container_width=True)
