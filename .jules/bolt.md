# Bolt's Journal - Critical Performance Learnings

## 2026-10-20 - Streamlit Function Caching with @st.cache_data and @st.cache_resource

**Learning:** In Streamlit applications, top-level function calls like database initialization (`init_db`) and PDF document generation (`generate_pdf_letter`) execute on every user interaction or UI rerun. Decorating non-mutating DB init functions with `@st.cache_resource` skips repetitive schema verification and table seeding queries. Decorating PDF generation with `@st.cache_data` caches PDF output bytes based on function parameters, avoiding costly FPDF rendering on subsequent reruns.

**Action:** Always check Streamlit top-level utility functions and data/file processing functions for missing `@st.cache_resource` (for global setup/connections) or `@st.cache_data` (for deterministic computations/file generation).
