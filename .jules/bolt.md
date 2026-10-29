# Bolt's Journal - Critical Learnings

## 2026-10-29 - Cache Streamlit PDF Letter Generation
**Learning:** Generating dynamic PDF letters with FPDF on every Streamlit script rerun introduces redundant CPU work (~0.017s per render vs ~0.0005s cached).
**Action:** Use `@st.cache_data` for pure byte/file generation functions in Streamlit applications.
