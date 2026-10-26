# Bolt's Journal - Critical Learnings

## 2026-10-26 - Streamlit Decorator Caching for Database Init & PDF Generation
**Learning:** Streamlit re-executes the entire script from top to bottom on every user interaction or widget state change. Top-level database schema initializations (`init_db`) and PDF letter generations (`generate_pdf_letter`) rerun synchronously on every render unless explicitly cached. Decorating `generate_pdf_letter` with `@st.cache_data` provides a ~45x speedup per render (from ~16ms down to ~0.3ms), while decorating `init_db` with `@st.cache_resource` eliminates redundant SQLite schema checks on every rerun.
**Action:** Always check Streamlit app entry points for uncached setup functions and document/file generator helper functions, decorating them with `@st.cache_resource` (for database connections/initializations) or `@st.cache_data` (for computed data/file outputs).
