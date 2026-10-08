# 🤝 Mending Our Mistakes, Inc. (M.O.M.) — Volunteer Portal

Welcome to the official **M.O.M. Volunteer Portal**, an integrated Web Application designed for remote and local volunteers, skilled advisors, and program coordinators supporting court-involved families across Central Arkansas.

---

## 🌟 Key Features

* **Role-Based Access Control:** Volunteer and Coordinator Command Center modes.
* **Task Time Logging & Multi-View Calendars:** Track hours precisely per task and view completion logs chronologically or via organization-wide daily pulses.
* **Build-to-Own Housing Pipeline:** Monitor composite housing construction, monthly rental credits, and eventual deed transfers.
* **Automated Grant Match Calculations:** Logs service hours and calculates financial match values at the Independent Sector rate (**$33.49/hr**).
* **Official Service Verification Letters:** Generates branded PDF letters on M.O.M. letterhead with unique verification IDs (`MOM-VOL-XXXX`).
* **Google Sheets Sync & SQLite Backend:** Live dual-sync with Google Workspace spreadsheets.

---

## 🚀 Quickstart Guide

### Local Setup
```bash
git clone [https://github.com/mendingourmistakes/mom-volunteer-portal.git](https://github.com/mendingourmistakes/mom-volunteer-portal.git)
cd mom-volunteer-portal
pip install -r requirements.txt
streamlit run app.py
