# Bolt's Journal - Critical Learnings

## 2026-10-28 - Caching Streamlit Data Generation Functions
**Learning:** In Streamlit applications, functions that build in-memory objects like PDFs using FPDF or DataFrames on every script rerun create noticeable latency (~15ms per call). Adding `@st.cache_data` and returning immutable primitives (such as `bytes`) allows Streamlit to cache output across reruns and reduces execution time to ~0.1ms per call.
**Action:** Always decorate deterministic data generation functions in Streamlit apps with `@st.cache_data` and return primitive binary or text representations (e.g. `bytes`).
