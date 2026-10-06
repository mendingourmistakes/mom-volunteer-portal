# 🤝 Mending Our Mistakes, Inc. — Volunteer Portal

Welcome to the official **Mending Our Mistakes (M.O.M.) Volunteer Portal**. This application provides a lightweight, zero-dependency dashboard for remote and local volunteers to log tasks, track service hours, and download verified PDF impact letters.

---

## 🚀 Quick Setup & Local Run

### Prerequisites
- Python 3.9+ installed

### 1. Clone the Repository
```bash
git clone https://github.com/mendingourmistakes/mom-volunteer-portal.git
cd mom-volunteer-portal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```
The portal will open automatically at `http://localhost:8501`.

---

## ☁️ Free 1-Click Cloud Deployment (Streamlit Community Cloud)

This app is designed to run **100% free with zero external databases (No Supabase required)** using built-in SQLite:

1. Push this clean codebase to your GitHub repo (`mendingourmistakes/mom-volunteer-portal`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **New app** -> Select your repository (`mom-volunteer-portal`) -> Main file path: `app.py`.
4. Click **Deploy!** Your live portal URL will be active in under 60 seconds.

---

## 🏛️ Features Included

- 🔐 **Secure Role-Based Login:** Admin, Volunteer, and Staff access tiers.
- 📋 **Task Assignment Board:** Web Specialist, Video Editor, Admin/Intake, and Outreach Liaisons.
- ⏱️ **Service Hour Logging:** Auto-calculates non-federal grant match value at **$33.49/hr** (Independent Sector rate).
- 📜 **Instant PDF Verification:** Generates official signed Service Verification Letters on M.O.M. letterhead.
- 💾 **Local & Portable:** Built-in SQLite database requiring zero cloud database maintenance or paid tiers.

---
*© Mending Our Mistakes, Inc. | Restoring Families • Rebuilding Stability • Renewing Communities*
