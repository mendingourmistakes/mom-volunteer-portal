import hashlib
import os
import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "mom_volunteers.db"
UPLOAD_DIR = "uploaded_resources"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def hash_pass(password):
  return hashlib.sha256(password.encode()).hexdigest()


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
            0.0,
            "🌱 Active Contributor",
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
            "M.O.M. supports pro se parents by organizing Legal Readiness Binders"
            " to prevent bench warrants and preserve custody.",
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

# Custom Styling to match mendingourmistakes.org branding & typography
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Colors & Fonts */
    :root {
        --primary-purple: #2E1A47;
        --royal-purple: #301934;
        --light-purple: #F3EBF9;
        --accent-purple: #7E57C2;
        --gold-amber: #B47A19;
        --charcoal: #2D3748;
        --soft-bg: #F8FAFC;
    }

    body, .stApp {
        background-color: #FFFFFF;
        font-family: 'Merriweather', serif;
        color: #2D3748;
    }

    /* Top Brand Header Banner */
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
        letter-spacing: 0.02em;
    }

    .mom-header p {
        font-family: 'Merriweather', serif;
        font-size: 1.05rem;
        color: #E0D7EA;
        margin: 0;
        font-weight: 300;
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

    /* Headings */
    h1, h2, h3, .stHeader {
        font-family: 'Playfair Display', serif !important;
        color: #2E1A47 !important;
    }

    /* Card Containers */
    .task-card {
        background-color: #FFFFFF;
        border: 1px solid #E0D7EA;
        border-left: 6px solid #2E1A47;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(46, 26, 71, 0.05);
        transition: all 0.2s ease-in-out;
    }

    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(46, 26, 71, 0.12);
        border-left-color: #B47A19;
    }

    /* Primary Buttons */
    .stButton>button, div.stDownloadButton>button {
        background-color: #2E1A47 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover, div.stDownloadButton>button:hover {
        background-color: #B47A19 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(180, 122, 25, 0.3) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E0D7EA !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #2E1A47;
        border-radius: 6px;
        padding: 8px 16px;
        background-color: #F3EBF9;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2E1A47 !important;
        color: #FFFFFF !important;
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
          "id": user_row,
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
    Our portal provides secure, tiered access to task cards, resource documents, and personalized hour tracking across our 7 regional site nodes.
    
    * **Tier 1 (Community & Remote)**: Public research, material cataloging, copyediting, and web copy.
    * **Tier 2 (Specialized Operations)**: Logistics, care warehouse inventory, fleet scheduling, and legal binder formatting.
    * **Tier 3 (Confidential / Client-Facing)**: Supervised visitation support, court compliance records, and pro se mentoring.
    """)

else:
  curr_user = st.session_state["user"]

  # Navigation Tabs depending on Role
  if curr_user["role"] in ["Coordinator", "Admin"]:
    app_mode = st.radio(
        "Portal Navigation:",
        [
            "📋 My Volunteer Workspace",
            "👥 Volunteer Onboarding & User Accounts",
            "⚙️ Task Management & Review Hub",
        ],
        horizontal=True,
    )
  else:
    app_mode = "📋 My Volunteer Workspace"

  # WORKSPACE VIEW FOR ALL VOLUNTEERS
  if app_mode == "📋 My Volunteer Workspace":
    st.header(f"👋 Welcome, {curr_user['full_name']}!")

    # Profile Summary Card
    c_p1, c_p2, c_p3 = st.columns(3)
    c_p1.metric("Approved Clearance Level", f"Tier {curr_user['tier']}")
    c_p2.metric(
        "Total Service Hours Logged", f"{curr_user['logged_hours']:.1f} Hours"
    )
    c_p3.metric(
        "Badges & Credentials", curr_user["badges"] or "🌱 Active Volunteer"
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

          # File Download Button
          if row["file_path"] and os.path.exists(row["file_path"]):
            with open(row["file_path"], "rb") as f:
              file_bytes = f.read()
            st.download_button(
                label=f"📥 Download Task Resource File ({row['file_name']})",
                data=file_bytes,
                file_name=row["file_name"],
                mime="application/octet-stream",
                type="primary",
            )

          with st.expander("📌 View Instructions & Deliverable Standards"):
            st.markdown(
                f"**Step-by-Step Instructions:**\n{row['instructions']}"
            )
            st.markdown(
                f"**Expected Deliverable:**\n{row['expected_deliverable']}"
            )

          # Submission Form
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

  # ONBOARDING & USER MANAGEMENT (COORDINATORS ONLY)
  elif app_mode == "👥 Volunteer Onboarding & User Accounts":
    st.header("👥 Volunteer Onboarding & User Management")
    st.caption(
        "Onboard new volunteers, set account passwords, and assign clearance"
        " tiers as directed by the Coordinator."
    )

    t_on1, t_on2 = st.tabs(
        ["➕ Create New User Account", "📜 Master Volunteer Roster"]
    )

    with t_on1:
      with st.form("create_user_form"):
        u_col1, u_col2 = st.columns(2)
        with u_col1:
          new_user = st.text_input("New Username (e.g. jsmith):")
          new_pass = st.text_input(
              "Set Initial Password:", type="password", value="mom2026"
          )
          new_name = st.text_input("Full Name:")
        with u_col2:
          new_email = st.text_input("Email Address:")
          new_role = st.selectbox(
              "Account Role:", ["Volunteer", "Coordinator"]
          )
          new_tier = st.slider(
              "Approved Clearance Tier:",
              1,
              3,
              1,
              help="1=Public, 2=Logistics, 3=Confidential",
          )

        if st.form_submit_button("Create & Activate Account"):
          if not new_user or not new_name:
            st.error("Username and Full Name are required!")
          else:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
              c.execute(
                  """
                                INSERT INTO users (username, password_hash, full_name, email, role, tier, logged_hours, badges)
                                VALUES (?, ?, ?, ?, ?, ?, 0.0, '🌱 Active Contributor')
                            """,
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
              st.success(
                  f"Account for **{new_name}** ({new_user}) activated at Tier"
                  f" {new_tier}!"
              )
            except Exception as e:
              st.error(f"Error creating user: {e}")
            finally:
              conn.close()

    with t_on2:
      st.subheader("Active Volunteer Roster & Hours Ledger")
      conn = sqlite3.connect(DB_FILE)
      df_users = pd.read_sql_query(
          "SELECT id, username, full_name, email, role, tier, logged_hours,"
          " badges FROM users",
          conn,
      )
      conn.close()
      st.dataframe(df_users, use_container_width=True)

  # TASK MANAGEMENT & REVIEW HUB (COORDINATORS ONLY)
  elif app_mode == "⚙️ Task Management & Review Hub":
    st.header("⚙️ Task Management & Review Hub")

    t_m1, t_m2, t_m3 = st.tabs([
        "📥 Review Submissions & Award Hours",
        "➕ Publish New Task Card",
        "📊 Master Task Ledger",
    ])

    with t_m1:
      st.subheader("Review Submissions & Credit Volunteer Hours")
      conn = sqlite3.connect(DB_FILE)
      df_rev = pd.read_sql_query(
          "SELECT * FROM tasks WHERE status = 'Submitted / Under Review'", conn
      )
      conn.close()

      if df_rev.empty:
        st.info("No submissions currently pending review.")
      else:
        for idx, row in df_rev.iterrows():
          with st.container():
            st.markdown(
                f"### 📥 [{row['task_code']}] {row['title']} — Submitted by"
                f" **{row['assigned_volunteer']}**"
            )
            st.write(
                f"**Estimated Hours:** {row['time_est']} hrs | **Site:**"
                f" {row['site_node']}"
            )
            st.markdown(
                f"**Submitted Deliverable / Notes:**\n```\n{row['submission_notes']}\n```"
            )

            col_a1, col_a2 = st.columns(2)
            if col_a1.button(
                f"✅ Approve & Credit {row['time_est']} Hours ({row['task_code']})",
                key=f"app_{row['task_code']}",
            ):
              conn = sqlite3.connect(DB_FILE)
              c = conn.cursor()
              c.execute(
                  "UPDATE tasks SET status='Approved & Completed' WHERE"
                  " task_code=?",
                  (row["task_code"],),
              )
              c.execute(
                  "UPDATE users SET logged_hours = logged_hours + ? WHERE"
                  " username=?",
                  (row["time_est"], row["assigned_volunteer"]),
              )

              c.execute(
                  "SELECT logged_hours, badges FROM users WHERE username=?",
                  (row["assigned_volunteer"],),
              )
              u_data = c.fetchone()
              if u_data:
                total_h, curr_b = u_data, u_data[1]
                new_b = curr_b
                if total_h >= 10 and "🏅 10+ Hour Bronze" not in curr_b:
                  new_b += " | 🏅 10+ Hour Bronze"
                if total_h >= 25 and "🥈 25+ Hour Silver" not in curr_b:
                  new_b += " | 🥈 25+ Hour Silver"
                if total_h >= 50 and "🥇 50+ Hour Gold Hero" not in curr_b:
                  new_b += " | 🥇 50+ Hour Gold Hero"
                c.execute(
                    "UPDATE users SET badges=? WHERE username=?",
                    (new_b, row["assigned_volunteer"]),
                )

              conn.commit()
              conn.close()
              st.success(
                  f"Task {row['task_code']} approved and {row['time_est']}"
                  " service hours credited!"
              )
              st.rerun()

            if col_a2.button(
                f"🔄 Request Revisions ({row['task_code']})",
                key=f"rev_{row['task_code']}",
            ):
              conn = sqlite3.connect(DB_FILE)
              c = conn.cursor()
              c.execute(
                  "UPDATE tasks SET status='Open' WHERE task_code=?",
                  (row["task_code"],),
              )
              conn.commit()
              conn.close()
              st.warning(f"Task {row['task_code']} returned to Open status.")
              st.rerun()

    with t_m2:
      st.subheader("Publish a New Task Card")
      with st.form("pub_task_form"):
        col_pt1, col_pt2 = st.columns(2)
        with col_pt1:
          pt_code = st.text_input("Task ID Code:", placeholder="e.g. ANN-102")
          pt_title = st.text_input("Task Title:")
          pt_site = st.selectbox(
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
          pt_module = st.selectbox(
              "Operational Module:",
              [
                  "Civil Legal Navigation (ANN)",
                  "Safe Family Contact (PRISM)",
                  "Heritage Trade & Salvage (AHTA)",
                  "Micro-Transit & Fleet (ATMS)",
                  "Technology Lab & Services (Tech Center)",
                  "Grants & Master Administration",
              ],
          )
        with col_pt2:
          pt_tier = st.slider("Required Clearance Tier:", 1, 3, 1)
          pt_time = st.number_input(
              "Estimated Service Hours Credit:",
              min_value=0.5,
              max_value=20.0,
              value=2.0,
              step=0.5,
          )
          pt_file = st.file_uploader(
              "Attach Reference Resource Document:",
              type=["pdf", "docx", "xlsx", "csv", "png", "jpg", "zip", "txt"],
          )

        pt_why = st.text_area("Why This Matters (Context):")
        pt_inst = st.text_area("Step-by-Step Instructions:")
        pt_deliv = st.text_area("Expected Deliverable Description:")

        if st.form_submit_button("Publish Task Card"):
          if not pt_code or not pt_title:
            st.error("Task ID Code and Title are required!")
          else:
            saved_path, saved_name = "", ""
            if pt_file is not None:
              saved_name = pt_file.name
              saved_path = os.path.join(
                  UPLOAD_DIR, f"{pt_code}_{saved_name}"
              )
              with open(saved_path, "wb") as f:
                f.write(pt_file.getbuffer())

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
              c.execute(
                  """
                                INSERT INTO tasks (task_code, title, site_node, module, tier_required, time_est, file_path, file_name, why_it_matters, instructions, expected_deliverable)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                  (
                      pt_code,
                      pt_title,
                      pt_site,
                      pt_module,
                      pt_tier,
                      pt_time,
                      saved_path,
                      saved_name,
                      pt_why,
                      pt_inst,
                      pt_deliv,
                  ),
              )
              conn.commit()
              st.success(f"Task {pt_code} published successfully!")
            except Exception as e:
              st.error(f"Error publishing task: {e}")
            finally:
              conn.close()

    with t_m3:
      st.subheader("Master Task Status Ledger")
      conn = sqlite3.connect(DB_FILE)
      df_all = pd.read_sql_query("SELECT * FROM tasks", conn)
      conn.close()
      st.dataframe(df_all, use_container_width=True)
