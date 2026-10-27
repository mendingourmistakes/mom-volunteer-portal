## 2026-10-27 - Cache SQLite Database Initialization in Streamlit Apps

**Learning:** Un-cached top-level SQLite database setup functions run on every Streamlit script execution during user interaction, opening connections and issuing redundant `CREATE TABLE IF NOT EXISTS` and `SELECT COUNT(*)` queries on every rerun. Using Streamlit's `@st.cache_resource` decorator on `init_db()` caches the initialization across user sessions and script reruns.
**Action:** Always decorate setup and database connection initialization logic with `@st.cache_resource` in Streamlit applications.
