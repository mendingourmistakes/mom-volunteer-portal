# Bolt's Journal - Critical Learnings Only

## 2026-11-06 - Streamlit Script Execution Model and Expensive Render Caching
**Learning:** Streamlit executes the entire script top-to-bottom on every user interaction (clicks, filters, typing). Operations like PDF generation (`fpdf2`) and SQLite DDL checks (`init_db()`) block the main script thread on every rerun (~15-20ms per user click) unless explicitly cached.
**Action:** Use `@st.cache_data` for pure generation functions producing serialized data (PDFs, reports, dataframes) and `@st.cache_resource` for global database schema initializations.
