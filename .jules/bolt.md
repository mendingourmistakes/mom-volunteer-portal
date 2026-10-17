## 2026-10-17 - Batch Discussion Replies Retrieval
**Learning:** Rendering discussion threads created an N+1 SQLite connection and query overhead by querying `discussion_replies` inside an iteration loop over `discussions`. Batching reply retrieval into a single `WHERE discussion_id IN (...)` query reduces database overhead from O(N) queries/connections to O(1).
**Action:** When iterating over parent database entities in Streamlit/SQLite applications, collect parent IDs and perform a single batch `IN` query to map child items in memory.
