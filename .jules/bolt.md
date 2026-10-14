# Bolt's Performance Journal

## 2026-03-31 - Batch Querying Discussion Replies & SQLite Foreign Key Indexing
**Learning:** In Streamlit applications rendering relational lists (like discussion threads and replies), executing database queries inside an `iterrows()` loop creates an N+1 query problem that opens/closes SQLite connection overhead per item. Batch querying all child records in a single SELECT and grouping by foreign key reduces database roundtrips and significantly speeds up page render times.
**Action:** Always fetch child records in batch prior to iterating over parent records, and ensure indexes exist on frequently queried foreign key fields (`discussion_id`, `assigned_volunteer`, etc.).
