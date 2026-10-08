# 🤝 Mending Our Mistakes, Inc. (M.O.M.) — Volunteer Portal

Welcome to the official **M.O.M. Volunteer Portal**, an integrated Web Application designed for remote and local volunteers, skilled advisors, and program coordinators supporting court-involved families across Central Arkansas.

---

## 🌟 Key Features

* **Role-Based Access Control:** Volunteer and Coordinator Command Center modes.
* **4 Functional Task Boards:** Community Outreach, Civil Legal Navigation, Heritage Trade & Salvage, and Web/Marketing.
* **Automated Grant Match Calculations:** Logs service hours and calculates financial match values at the Independent Sector rate (**$33.49/hr**).
* **Official Service Verification Letters:** Generates branded PDF letters on M.O.M. letterhead with unique verification IDs (`MOM-VOL-XXXX`).
* **Google Sheets Sync & CSV Export:** Live dual-sync with Google Workspace spreadsheets and 1-click CSV/SQLite backups.

---

## 🚀 Quickstart Guide

### 1. Local Setup
```bash
git clone https://github.com/mendingourmistakes/mom-volunteer-portal.git
cd mom-volunteer-portal
pip install -r requirements.txt
streamlit run app.py
```

### 2. Streamlit Cloud Deployment (Free)
1. Push this repository to GitHub (`github.com/mendingourmistakes/mom-volunteer-portal`).
2. Log into [share.streamlit.io](https://share.streamlit.io) with GitHub.
3. Select repo: `mom-volunteer-portal`, main file: `app.py`.
4. Click **Deploy**!

---

## 📊 Google Sheets Integration
To link a live Google Sheet, follow the instructions in [`GOOGLE_SHEETS_SETUP.md`](./GOOGLE_SHEETS_SETUP.md).

---

© Mending Our Mistakes, Inc. (d.b.a. The M.O.M. Project) | Malvern & Traskwood, AR
