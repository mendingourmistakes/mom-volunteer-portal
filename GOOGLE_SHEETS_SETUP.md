# 📊 3-Step Guide to Linking Google Sheets to M.O.M. Volunteer Portal

This guide shows you how to connect your Streamlit Volunteer Portal directly to a **Google Sheet** so every volunteer signup, logged hour, and task card is saved live in your Google Workspace.

---

### Step 1: Create Your Google Sheet
1. Go to [Google Sheets](https://sheets.new) and create a new blank spreadsheet.
2. Title it: **`MOM_Volunteer_Portal_Database`**.
3. Create two tabs at the bottom:
   - **`Users`**
   - **`Tasks`**
4. Set Share Permissions:
   - Click **Share** (top right) -> Change under General Access to **"Anyone with the link" -> "Editor"**.
   - Copy the Sheet URL (e.g., `https://docs.google.com/spreadsheets/d/1ABC.../edit`).

---

### Step 2: Add Sheet URL to Streamlit Cloud Secrets
1. Go to your app dashboard at [share.streamlit.io](https://share.streamlit.io).
2. Click **Settings** (gear icon) next to your `mom-volunteer-portal` app -> **Secrets**.
3. Paste the following snippet, replacing the URL with your Google Sheet URL:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit"
```

4. Click **Save**.

---

### Step 3: Verify Connection
1. Log into your M.O.M. Volunteer Portal as Coordinator.
2. Navigate to **🛠️ Coordinator Command Center -> 📊 Google Sheets & Export**.
3. You will see a green **"✅ Google Sheets Connection Active!"** badge.
4. Click **"🔄 Force Sync Roster to Google Sheets"** or **"🔄 Force Sync Tasks to Google Sheets"** to push all current data directly into your Google Sheet!

---

### 💡 Benefits of This Setup
- **100% Free & Automatic:** No database servers or monthly hosting costs.
- **Grant-Ready CSV Exports:** Calculate non-federal volunteer match value (**$33.49/hr**) with one click.
- **Never Lost:** Even if Streamlit Cloud reboots or updates, all data remains permanently saved in your Google Sheet.
