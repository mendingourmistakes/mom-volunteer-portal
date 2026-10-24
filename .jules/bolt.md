# Bolt's Journal - Critical Learnings

## 2026-10-24 - Streamlit Database Initialization Caching
**Learning:** In Streamlit apps, top-level execution of database schema initialization (`init_db()`) runs on every user interaction and page rerun. Decorating `init_db()` with `@st.cache_resource` ensures table checks and seeding run only once per app resource lifecycle, eliminating unnecessary SQL queries and disk I/O on every UI event.
**Action:** Always wrap top-level database schema setup functions with `@st.cache_resource` in Streamlit applications.
