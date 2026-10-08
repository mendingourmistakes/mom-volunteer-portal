## 2026-10-08 - Streamlit PDF Generation Caching
**Learning:** Streamlit re-executes the entire script on every user interaction/rerun. Uncached PDF rendering with `FPDF` in render loops creates a ~15ms CPU block on every click/filter change.
**Action:** Always wrap non-mutating expensive data formatting/generation functions like `generate_pdf_letter` with `@st.cache_data`.
