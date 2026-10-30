## 2026-10-30 - Streamlit PDF Generation Caching
**Learning:** Functions that generate PDF documents using FPDF in Streamlit applications create significant execution overhead (~15ms per call) during script reruns. Wrapping them with `@st.cache_data` caches the output byte stream and speeds up execution to ~0.4ms when arguments remain unchanged.
**Action:** Always check expensive document generation or data export functions in Streamlit apps and decorate pure input-output generation methods with `@st.cache_data`.
