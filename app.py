import streamlit as st
import pandas as pd
from fpdf import FPDF
import sqlite3
import hashlib
from datetime import datetime
import json

# Page Configuration
st.set_page_config(
    page_title="M.O.M. Volunteer Portal",
    page_icon="🤝",
    layout="wide"
)

DB_FILE = "volunteer_portal.db"

# Password Hashing Helper
def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Database Initialization
@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        role TEXT,
        full_name TEXT,
        total_hours REAL,
        tier TEXT,
        badges TEXT
    )
    """)
    
    # Insert Default Users (Password: MendingOurMistakes25)
    c.execute("""
    INSERT OR IGNORE INTO users (username, password_hash, role, full_name, total_hours, tier, badges)
    VALUES ('admin', '490ebf932ec7349d4becc9eecbe9b1a5bd8b248eb3a696fa8d5e8211b81cd7e1', 'admin', 'Program Coordinator', 0.0, 'Bronze', '')
    """)
    
    c.execute("""
    INSERT OR IGNORE INTO users (username, password_hash, role, full_name, total_hours, tier, badges)
    VALUES ('volunteer1', '490ebf932ec7349d4becc9eecbe9b1a5bd8b248eb3a696fa8d5e8211b81cd7e1', 'volunteer', 'Jane Doe', 12.5, 'Silver', 'Orientation Complete')
    """)
    
    # Submissions / Task Logs Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS task_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        task_name TEXT,
        hours_logged REAL,
        date_submitted TEXT,
        status TEXT
    )
    """)
    
    conn.commit()
    return conn

conn = init_db()

# PDF Generator Function
def generate_pdf_letter(full_name, username, total_hours, tier, badges):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Mending Our Mistakes, Inc.", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Official Volunteer Service Certification", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, txt=f"Volunteer Name: {full_name} (@{username})", ln=True)
    pdf.cell(200, 10, txt=f"Total Certified Hours: {total_hours} hrs", ln=True)
    pdf.cell(200, 10, txt=f"Tier Status: {tier}", ln=True)
    pdf.cell(200, 10, txt=f"Badges Earned: {badges}", ln=True)
    pdf.ln(15)
    pdf.multi_cell(0, 10, txt="This letter confirms the official service hours completed by the volunteer named above for Mending Our Mistakes, Inc. We deeply appreciate their commitment to restoring families and renewing communities.")
    pdf.ln(20)
    pdf.cell(200, 10, txt="________________________________________", ln=True)
    pdf.cell(200, 10, txt="Authorized Program Coordinator Signature", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# Session State Initialization
if "user" not in st.session_state:
    st.session_state["user"] = None

# Sidebar Authentication
st.sidebar.markdown("### Mending Our Mistakes\n*A Parental Restoration Continuum*")
st.sidebar.divider()

if st.session_state["user"] is None:
    st.sidebar.subheader("🔒 Account Sign In")
    login_user = st.sidebar.text_input("Username").strip()
    login_pass = st.sidebar.text_input("Password", type="password").strip()
    
    if st.sidebar.button("Sign In"):
        c = conn.cursor()
        c.execute("SELECT username, password_hash, role, full_name, total_hours, tier, badges FROM users WHERE username = ?", (login_user,))
        user_row = c.fetchone()
        
        if user_row and user_row[1] == hash_pass(login_pass):
            st.session_state["user"] = {
                "username": user_row[0],
                "role": user_row[2],
                "full_name": user_row[3],
                "total_hours": user_row[4],
                "tier": user_row[5],
                "badges": user_row[6]
            }
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")
            
    st.sidebar.info("💡 **Default Logins:**\n- Coordinator: `admin` / `MendingOurMistakes25`\n- Volunteer: `volunteer1` / `MendingOurMistakes25`")

else:
    st.sidebar.success(f"Signed in as **{st.session_state['user']['full_name']}** ({st.session_state['user']['role'].title()})")
    if st.sidebar.button("Sign Out"):
        st.session_state["user"] = None
        st.rerun()

# Main Application Dashboard
st.title("Mending Our Mistakes, Inc. — Volunteer Portal")
st.caption("Restoring Families. Rebuilding Stability. Renewing Communities.")

if st.session_state["user"] is None:
    st.warning("👈 Please sign in using the sidebar to access your volunteer workspace.")
    st.markdown("## Welcome to the M.O.M. Volunteer Network!")
    st.write("Our portal provides secure, tiered access to task cards, resource documents, micro-training, community discussions, and service hour certification.")

else:
    user = st.session_state["user"]
    
    # Navigation Tabs
    if user["role"] == "admin":
        tab1, tab2, tab3 = st.tabs(["📊 Coordinator Dashboard", "📝 Task Management", "📜 Certifications"])
    else:
        tab1, tab2, tab3 = st.tabs(["👤 My Profile", "📝 Log Hours", "📜 Request Certificate"])

    # Volunteer Profile / Overview
    with tab1:
        st.header(f"Welcome back, {user['full_name']}!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Hours Logged", f"{user['total_hours']} hrs")
        col2.metric("Current Tier", user['tier'])
        col3.metric("Role", user['role'].title())
        
        st.divider()
        st.subheader("Recent Activity & Service History")
        df_logs = pd.read_sql_query("SELECT task_name, hours_logged, date_submitted, status FROM task_logs WHERE username = ?", conn, params=(user['username'],))
        if not df_logs.empty:
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("No service tasks logged yet.")

    # Hours Logging Tab
    with tab2:
        st.header("Log Service Hours")
        with st.form("log_hours_form"):
            task_name = st.text_input("Task / Activity Description")
            hours = st.number_input("Hours Spent", min_value=0.5, max_value=24.0, step=0.5)
            submitted = st.form_submit_button("Submit Hours")
            
            if submitted and task_name:
                c = conn.cursor()
                c.execute("INSERT INTO task_logs (username, task_name, hours_logged, date_submitted, status) VALUES (?, ?, ?, ?, ?)",
                          (user['username'], task_name, hours, datetime.now().strftime('%Y-%m-%d %H:%M'), "Pending Review"))
                
                # Update user total hours
                new_total = user['total_hours'] + hours
                c.execute("UPDATE users SET total_hours = ? WHERE username = ?", (new_total, user['username']))
                conn.commit()
                
                st.session_state["user"]["total_hours"] = new_total
                st.success("Hours submitted successfully!")
                st.rerun()

    # Certificate Generation Tab
    with tab3:
        st.header("Service Verification Letter")
        st.write("Generate an official PDF certifying your volunteer hours with Mending Our Mistakes, Inc.")
        
        pdf_bytes = generate_pdf_letter(
            user['full_name'],
            user['username'],
            user['total_hours'],
            user['tier'],
            user['badges']
        )
        
        st.download_button(
            label="📄 Download Official Verification PDF",
            data=pdf_bytes,
            file_name=f"MOM_Volunteer_Certificate_{user['username']}.pdf",
            mime="application/pdf"
        )
