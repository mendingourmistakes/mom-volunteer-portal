import os
import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "mom_volunteers.db"
UPLOAD_DIR = "uploaded_resources"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


def init_db():
  conn = sqlite3.connect(DB_FILE)
  c = conn.cursor()

  c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            site_node TEXT NOT NULL,
            module TEXT NOT NULL,
            tier_required INTEGER NOT NULL,
            time_est TEXT NOT NULL,
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

  # Migration check for file columns
  c.execute("PRAGMA table_info(tasks)")
  columns = [col[1] for col in c.fetchall()]
  if "file_path" not in columns:
    c.execute("ALTER TABLE tasks ADD COLUMN file_path TEXT DEFAULT ''")
  if "file_name" not in columns:
    c.execute("ALTER TABLE tasks ADD COLUMN file_name TEXT DEFAULT ''")

  conn.commit()
  conn.close()


init_db()

st.set_page_config(
    page_title="M.O.M. Volunteer & Task Portal", page_icon="🏛️", layout="wide"
)

st.title("🏛️ Mending Our Mistakes, Inc. — Operations & Volunteer Portal")
st.caption("Tiered Task Delegation & Resource File Distribution System")

# Sidebar Navigation
sidebar_mode = st.sidebar.radio(
    "Select Portal View:", ["Volunteer Task Center", "Coordinator Admin Hub"]
)

if sidebar_mode == "Volunteer Task Center":
  st.header("📋 Available Volunteer Tasks")

  col_v1, col_v2 = st.columns(2)
  with col_v1:
    volunteer_name = st.text_input(
        "Your Name / Email:", placeholder="e.g. Jane Doe (jane@example.com)"
    )
  with col_v2:
    assigned_tier = st.selectbox(
        "Select Your Approved Clearance Tier:",
        [1, 2, 3],
        format_func=lambda x: f"Tier {x}: "
        + (
            "Community & Remote (Public Tasks)"
            if x == 1
            else "Specialized Ops (Logistics / Non-PII)"
            if x == 2
            else "Client-Facing / Confidential (HIPAA & Court Clearance)"
        ),
    )

  conn = sqlite3.connect(DB_FILE)
  df_tasks = pd.read_sql_query(
      f"SELECT * FROM tasks WHERE tier_required <= {assigned_tier} AND status"
      " IN ('Open', 'In Progress')",
      conn,
  )
  conn.close()

  st.write("---")

  if df_tasks.empty:
    st.info("No active tasks currently available at your clearance level.")
  else:
    for idx, row in df_tasks.iterrows():
      with st.container(border=True):
        status_color = "🟢" if row["status"] == "Open" else "🟡"
        st.subheader(
            f"{status_color} [{row['task_code']}] {row['title']} ({row['status']})"
        )

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.markdown(f"**📍 Site Node:**\n{row['site_node']}")
        col_m2.markdown(f"**⚙️ Module:**\n{row['module']}")
        col_m3.markdown(
            f"**🔒 Tier & Time:**\nTier {row['tier_required']} |"
            f" {row['time_est']}"
        )

        st.markdown(f"#### 💡 Why This Matters\n{row['why_it_matters']}")

        # File Download Section
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
        else:
          st.caption("ℹ️ No attached document file for this task.")

        with st.expander("📌 View Detailed Instructions & Deliverable Rules"):
          st.markdown(
              f"**Step-by-Step Instructions:**\n{row['instructions']}"
          )
          st.markdown(
              f"**Expected Deliverable:**\n{row['expected_deliverable']}"
          )

        # Submission Form
        with st.form(key=f"claim_form_{row['task_code']}"):
          sub_notes = st.text_area(
              "Submit Completed Work / Completion Notes:",
              placeholder=(
                  "Enter completion details, notes, or paste links to your"
                  " finished work..."
              ),
          )
          submit_button = st.form_submit_button("Submit Work for Review")

          if submit_button:
            if not volunteer_name:
              st.error("Please enter your Name or Email at the top first!")
            elif not sub_notes:
              st.error("Please enter completion notes before submitting!")
            else:
              conn = sqlite3.connect(DB_FILE)
              c = conn.cursor()
              c.execute(
                  "UPDATE tasks SET status='Submitted / Under Review',"
                  " assigned_volunteer=?, submission_notes=? WHERE task_code=?",
                  (volunteer_name, sub_notes, row["task_code"]),
              )
              conn.commit()
              conn.close()
              st.success(
                  f"Task {row['task_code']} submitted for coordinator review!"
                  " Thank you!"
              )
              st.rerun()

elif sidebar_mode == "Coordinator Admin Hub":
  st.header("⚙️ Volunteer Coordinator Command Center")

  tab1, tab2, tab3 = st.tabs(
      ["➕ Add New Task", "📥 Review Submissions", "📊 Master Task Ledger"]
  )

  # Tab 1: Create New Task with File Upload
  with tab1:
    st.subheader("Create a Task Card & Upload Reference Documents")
    with st.form("create_task_form"):
      c_col1, c_col2 = st.columns(2)
      with c_col1:
        t_code = st.text_input(
            "Task ID Code:", placeholder="e.g. ANN-102, AHTA-202"
        )
        t_title = st.text_input("Task Title:")
        t_site = st.selectbox(
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
        t_module = st.selectbox(
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
      with c_col2:
        t_tier = st.slider(
            "Required Clearance Tier:",
            1,
            3,
            1,
            help="1=Public, 2=Logistics, 3=Confidential",
        )
        t_time = st.text_input("Estimated Time Commitment:", "2 Hours")

        # File Upload Field
        uploaded_file = st.file_uploader(
            "Upload Reference Document (PDF, Word, Excel, Image):",
            type=["pdf", "docx", "xlsx", "csv", "png", "jpg", "zip", "txt"],
        )

      t_why = st.text_area("Why This Matters (Background Context):")
      t_inst = st.text_area("Step-by-Step Instructions:")
      t_deliv = st.text_area("Expected Deliverable Description:")

      if st.form_submit_button("Publish Task Card"):
        if not t_code or not t_title:
          st.error("Task ID Code and Title are required!")
        else:
          saved_file_path = ""
          saved_file_name = ""

          if uploaded_file is not None:
            saved_file_name = uploaded_file.name
            saved_file_path = os.path.join(UPLOAD_DIR, f"{t_code}_{saved_file_name}")
            with open(saved_file_path, "wb") as f:
              f.write(uploaded_file.getbuffer())

          conn = sqlite3.connect(DB_FILE)
          c = conn.cursor()
          try:
            c.execute(
                """
                            INSERT INTO tasks (task_code, title, site_node, module, tier_required, time_est, file_path, file_name, why_it_matters, instructions, expected_deliverable)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                (
                    t_code,
                    t_title,
                    t_site,
                    t_module,
                    t_tier,
                    t_time,
                    saved_file_path,
                    saved_file_name,
                    t_why,
                    t_inst,
                    t_deliv,
                ),
            )
            conn.commit()
            st.success(f"Task {t_code} published with document attachment!")
          except Exception as e:
            st.error(f"Error creating task: {e}")
          finally:
            conn.close()

  # Tab 2: Review Submissions
  with tab2:
    st.subheader("Review & Approve Submitted Volunteer Work")
    conn = sqlite3.connect(DB_FILE)
    df_review = pd.read_sql_query(
        "SELECT * FROM tasks WHERE status = 'Submitted / Under Review'", conn
    )
    conn.close()

    if df_review.empty:
      st.info("No submissions currently pending review.")
    else:
      for idx, row in df_review.iterrows():
        with st.container(border=True):
          st.markdown(
              f"### 📥 [{row['task_code']}] {row['title']} — Submitted by"
              f" **{row['assigned_volunteer']}**"
          )
          st.write(
              f"**Site:** {row['site_node']} | **Module:** {row['module']}"
          )
          st.markdown(
              f"**Submitted Deliverable / Notes:**\n```\n{row['submission_notes']}\n```"
          )

          r_col1, r_col2 = st.columns(2)
          if r_col1.button(
              f"✅ Approve & Mark Complete ({row['task_code']})",
              key=f"app_{row['task_code']}",
          ):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "UPDATE tasks SET status='Approved & Completed' WHERE"
                " task_code=?",
                (row["task_code"],),
            )
            conn.commit()
            conn.close()
            st.success(f"Task {row['task_code']} approved!")
            st.rerun()

          if r_col2.button(
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

  # Tab 3: Master Ledger
  with tab3:
    st.subheader("Master Task & Status Ledger")
    conn = sqlite3.connect(DB_FILE)
    df_all = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    st.dataframe(df_all, use_container_width=True)
