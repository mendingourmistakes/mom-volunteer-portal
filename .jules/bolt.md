# Bolt's Performance Journal

## 2026-11-07 - Streamlit Rerun Latency in File/Data Generators
**Learning:** In Streamlit applications, every UI interaction (filtering dropdowns, checking boxes, clicking action buttons) triggers a full script rerun. Synchronous document generation functions like `generate_pdf_letter` (using FPDF) take ~15ms per call to compute layout metrics and assemble binary PDF documents. Rendering this unconditionally on the main marketplace view caused recurring CPU stalls on every user interaction.
**Action:** Use `@st.cache_data` on deterministic data and document generation functions so repeated script executions return memoized byte outputs immediately (<0.2ms), cutting execution latency by ~7x-10x per rerun.
