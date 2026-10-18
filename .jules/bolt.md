## 2026-10-18 - SQLite Table Scan Bottlenecks in Streamlit Applications

**Learning:** In Streamlit applications backed by SQLite (`app.py`), database queries run on every user interaction and page render. Without explicit indexes, queries like `WHERE status = ?`, `WHERE assigned_volunteer = ?`, `WHERE discussion_id = ?`, and `ORDER BY logged_hours DESC` perform full table scans (`SCAN TABLE`) and create temporary B-trees for sorting.
**Action:** Always create `CREATE INDEX IF NOT EXISTS` inside database initialization (`init_db()`) on columns used in `WHERE` clauses and `ORDER BY` fields.
