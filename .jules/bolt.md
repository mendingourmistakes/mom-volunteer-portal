# Bolt's Journal - Critical Learnings

## 2026-10-12 - Streamlit PDF Generation Caching & SQLite Indexes
**Learning:** Generating dynamic PDFs with FPDF on every Streamlit page rerun introduces ~16ms overhead per UI interaction even when user credentials haven't changed. Caching `generate_pdf_letter` using `@st.cache_data` eliminates redundant FPDF operations across script reruns. Additionally, adding targeted SQLite indexes on filtered columns (`tasks`, `discussion_replies`, `messages`, `support_tickets`) prevents full table scans on query execution.
**Action:** Always memoize pure binary output functions (like PDF/chart generation) using `@st.cache_data` in Streamlit apps and verify SQLite schema indexes on filtered fields.
