# Bolt's Performance Journal

This journal records critical performance learnings, architectural bottlenecks, and codebase-specific patterns discovered during optimizations.

## 2026-11-01 - Caching In-Memory Artifacts and Setup in Streamlit
**Learning:** Streamlit re-executes the entire script on every user interaction (e.g., clicking a button or changing tabs). Synchronous file generation (like FPDF document compilation taking ~15ms) and repeated database setup routines (`init_db` running SQLite DDL queries taking ~0.6ms) add unnecessary latency to every user interaction. Wrapping idempotent setup routines with `@st.cache_resource` and deterministic byte generators with `@st.cache_data` eliminates redundant re-computation (~30-50x speedup on reruns) without breaking application state.
**Action:** When working on Streamlit apps, profile module-level initialization code and synchronous document/data generation for `@st.cache_resource` and `@st.cache_data` applicability.
