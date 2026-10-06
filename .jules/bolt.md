## 2026-10-06 - Cache PDF Generation in Streamlit App
**Learning:** Generating dynamic PDFs with FPDF on every Streamlit script re-render introduces significant latency (~15ms per call). Using `@st.cache_data` on PDF generation functions prevents unnecessary re-computations when parameters (e.g. user info, hours) remain constant.
**Action:** Always wrap expensive asset or report generation functions in Streamlit apps with `@st.cache_data`.
