# Bolt's Journal - Performance Learnings

## 2026-10-05 - Streamlit N+1 Database Queries & Redundant PDF Generation
**Learning:** In Streamlit applications, every user interaction triggers a complete rerun of the script from top to bottom. DB queries inside UI loops (like fetching discussion replies per topic card) create severe N+1 database roundtrips, and un-cached helper calls (like PDF letter generation) run repeatedly on every interaction.
**Action:** Batch database queries before rendering loops and wrap expensive computation/generation functions in `@st.cache_data`.
