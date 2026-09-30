import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "mom_volunteers.db"


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
            why_it_matters TEXT NOT NULL,
            instructions TEXT NOT NULL,
            expected_deliverable TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            assigned_volunteer TEXT DEFAULT NULL,
            submission_notes TEXT DEFAULT NULL
        )
    """)
  c.execute("SELECT COUNT(*) FROM tasks")
  if c.fetchone()[0] == 0:
    sample_tasks = [
        (
            "ANN-101",
            "Legal Readiness Binder Pre-Check",
            "Node 1: Dyer St Plaza Hub (Malvern)",
            "Civil Legal Navigation",
            2,
            "2 Hours",
            "M.O.M. supports pro se parents in private civil court by"
            " organizing 5-tab Legal Readiness Binders to prevent bench"
            " warrants and custody loss.",
            "1. Download the 5-Tab Checklist template.\n2. Review uploaded"
            " client documents for completeness (Court Orders, Income Proof,"
            " Visitation Logs).\n3. Compile into a formatted PDF index.",
            "Completed 5-Tab Digital PDF Binder Index ready for CALES/Legal Aid"
            " review.",
            "Open",
            None,
            None,
        ),
        (
            "AHTA-201",
            "Salvage Depot Materials Cataloging",
            "Node 3: Industrial Rd Trade Yard (Malvern)",
            "Heritage Trade & Salvage",
            1,
            "1.5 Hours",
            "Reclaimed architectural materials generate earned revenue for"
            " M.O.M. while teaching trade apprentices preservation skills.",
            "1. Review photos of incoming reclaimed timber and historic"
            " brick.\n2. Log dimensions, condition, and quantities into the"
            " catalog.\n3. Tag by architectural era.",
            "10 cataloged inventory entries uploaded to the digital AHTA"
            " Salvage Depot database.",
            "Open",
            None,
            None,
        ),
        (
            "PRISM-301",
            "Safe Exchange & Visitation Preparation",
            "Node 2: Chandler Rd Campus (Traskwood)",
            "Safe Family Contact (PRISM)",
            3,
            "3 Hours",
            "PRISM suites provide neutral, trauma-informed visitation for"
            " parents restoring court-sanctioned custody rights.",
            "1. Review session schedule and observation protocol.\n2."
            " Inspect suite safety equipment and dual-entrance access"
            " points.\n3. Log pre-session compliance verification.",
            "Signed PRISM Suite Verification Log submitted to Clinical"
            " Director.",
            "Open",
            None,
            None,
        ),
    ]
    c.executemany(
        """
            INSERT INTO tasks (task_code, title, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable, status, assigned_volunteer, submission_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_tasks,
    )
  conn.commit()
  conn.close()


init_db()

st.set_page_config(
    page_title="M.O.M. Volunteer Portal", page_icon="🤝", layout="wide"
)

st.title("🤝 Mending Our Mistakes, Inc. — Volunteer Task Portal")
st.caption("Tiered Task Delegation & Operational Management System")

sidebar_mode = st.sidebar.radio(
    "Select Your Portal View:", ["Volunteer Portal", "Coordinator Admin Center"]
)

if sidebar_mode == "Volunteer Portal":
  st.header("📋 Available Volunteer Tasks")

  col1, col2 = st.columns(2)
  with col1:
    volunteer_name = st.text_input("Your Name / Email:", "volunteer@mom.org")
  with col2:
    assigned_tier = st.selectbox(
        "Select Your Approved Clearance Tier:",
        [
            1,
            2,
            3,
        ],
        format_func=lambda x: f"Tier {x}: "
        + (
            "Community & Remote (Public Data)"
            if x == 1
            else "Specialized Ops (Non-PII Logistics)"
            if x == 2
            else "Client-Facing / Confidential (HIPAA/Court Cleaned)"
        ),
    )

  conn = sqlite3.connect(DB_FILE)
  df_tasks = pd.read_sql_query(
      f"SELECT * FROM tasks WHERE tier_required <= {assigned_tier} AND status"
      " = 'Open'",
      conn,
  )
  conn.close()

  st.subheader(
      f"Tasks Available for Clearance Level Tier {assigned_tier} and Below:"
  )

  if df_tasks.empty:
    st.info("No open tasks currently available at this tier level.")
  else:
    for idx, row in df_tasks.iterrows():
      with st.expander(
          f"[{row['task_code']}] {row['title']} — {row['site_node']} (Est. Time:"
          f" {row['time_est']})"
      ):
        st.write(f"**Module:** {row['module']} | **Required Tier:** Tier"
                 f" {row['tier_required']}")
        st.markdown(f"### 💡 Why This Matters\n{row['why_it_matters']}")
        st.markdown(f"### 📝 Step-by-Step Instructions\n{row['instructions']}")
        st.markdown(
            f"### 🎯 Expected Deliverable\n{row['expected_deliverable']}"
        )

        with st.form(key=f"claim_form_{row['task_code']}"):
          sub_notes = st.text_area("Paste Completed Work / Deliverable Link:")
          submit_button = st.form_submit_button("Submit Completed Task")

          if submit_button:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "UPDATE tasks SET status='Completed', assigned_volunteer=?,"
                " submission_notes=? WHERE task_code=?",
                (volunteer_name, sub_notes, row["task_code"]),
            )
            conn.commit()
            conn.close()
            st.success(
                f"Task {row['task_code']} successfully submitted! Thank you"
                " for supporting M.O.M.!"
            )
            st.rerun()

elif sidebar_mode == "Coordinator Admin Center":
  st.header("⚙️ Volunteer Coordinator Command Center")

  tab1, tab2 = st.tabs(["Add New Task", "View Task Ledger"])

  with tab1:
    st.subheader("Create a New Self-Contained Task Card")
    with st.form("create_task_form"):
      t_code = st.text_input("Task ID Code (e.g., ANN-102, AHTA-202):")
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
      t_tier = st.slider(
          "Required Clearance Tier:", 1, 3, 1, help="1=Public, 2=Logistics, 3=Confidential"
      )
      t_time = st.text_input("Estimated Time Commitment:", "2 Hours")
      t_why = st.text_area("Why This Matters (Background Context):")
      t_inst = st.text_area("Step-by-Step Instructions:")
      t_deliv = st.text_area("Expected Deliverable Description:")

      if st.form_submit_button("Publish Task to Portal"):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
          c.execute(
              """
                        INSERT INTO tasks (task_code, title, site_node, module, tier_required, time_est, why_it_matters, instructions, expected_deliverable)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  t_code,
                  t_title,
                  t_site,
                  t_module,
                  t_tier,
                  t_time,
                  t_why,
                  t_inst,
                  t_deliv,
              ),
          )
          conn.commit()
          st.success(f"Task {t_code} published successfully!")
        except Exception as e:
          st.error(f"Error creating task: {e}")
        finally:
          conn.close()

  with tab2:
    st.subheader("Master Task Status Ledger")
    conn = sqlite3.connect(DB_FILE)
    df_all = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    st.dataframe(df_all, use_container_width=True)
