# Bolt's Performance Journal

## 2026-10-31 - Streamlit Rerun Caching for Expensive Operations
**Learning:** In Streamlit applications, every user interaction triggers a full rerun of the script top-to-bottom. Uncached operations like PDF document building (`fpdf2`) and database schema/seed checks (`sqlite3`) block rendering on every interaction. Using `@st.cache_data` for document generation reduces rerun latency from ~16ms to ~0.3ms (~50x speedup), and `@st.cache_resource` for `init_db()` ensures table setup runs once per session.
**Action:** When working with Streamlit apps, profile reruns and ensure that document generators, data exports, and database initialization are decorated with appropriate `@st.cache_data` or `@st.cache_resource` hooks.
