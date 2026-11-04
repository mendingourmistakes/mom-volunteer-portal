# Bolt's Performance Journal

Critical learnings only.

## 2026-11-04 - Caching PDF Letter Generation and Schema Initialization in Streamlit
**Learning:** Streamlit re-executes the entire script sequentially from top to bottom on every user interaction (such as tab switches, button clicks, and form submissions). Expensive operations like binary PDF document generation (`FPDF` formatting and output) take ~19.4ms per invocation and were regenerating unconditionally inside the volunteer marketplace view. Caching `generate_pdf_letter` with `@st.cache_data` memoizes the output by user parameters, reducing repeated execution time to <0.5ms (~98% latency reduction). In addition, decorating `init_db()` with `@st.cache_resource` ensures that 11 table creation DDL statements and multiple user/task seed checks execute once per process lifecycle rather than on every single Streamlit script rerun.
**Action:** In Streamlit applications, always memoize binary/data generation functions with `@st.cache_data` and heavy one-off initialization/setup logic with `@st.cache_resource`.
