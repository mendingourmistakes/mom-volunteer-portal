# Bolt's Journal - Performance Insights

## 2026-10-09 - Streamlit Database Initialization Caching & SQLite Indexing
**Learning:** In Streamlit applications, top-level database initialization functions like `init_db()` run on every single user interaction and script rerun. Decorating `init_db()` with `@st.cache_resource` prevents unnecessary database table checks and initial seed queries on every render. Additionally, creating compound and single-column indexes (`idx_tasks_tier_status`, `idx_tasks_assigned`, `idx_messages_sender_recipient`, `idx_discussion_replies_disc_id`) reduces SQLite query execution time from full table scans O(N) to index lookups O(log N).
**Action:** Always wrap top-level initialization routines in Streamlit with `@st.cache_resource` and add SQLite indexes for frequently queried columns in database tables.
