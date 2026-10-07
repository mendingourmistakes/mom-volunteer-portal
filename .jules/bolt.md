## 2026-10-07 - Streamlit Database Initialization Caching & SQLite Indexes

**Learning:** In Streamlit applications, top-level database initialization functions like `init_db()` execute DDL (`CREATE TABLE IF NOT EXISTS`) and seeding queries (`SELECT COUNT(*)`) on every user interaction/rerun if uncached. Decorating initialization with `@st.cache_resource` caches the initialization execution across script reruns while retaining database integrity. Additionally, adding SQLite indexes on foreign keys and filtering columns (`assigned_volunteer`, `status`, `sender`/`recipient`, `discussion_id`, `volunteer`) significantly reduces query execution times as data grows.

**Action:** Always wrap top-level startup/DDL database functions with `@st.cache_resource` in Streamlit apps, and ensure all queried columns in `WHERE` and `ORDER BY` clauses have corresponding SQLite indexes.
