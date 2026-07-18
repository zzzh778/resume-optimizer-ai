import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "resume_optimizer.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            limit_count INTEGER NOT NULL DEFAULT 3,
            used_count INTEGER NOT NULL DEFAULT 0,
            reset_date TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_name TEXT NOT NULL DEFAULT '',
            target_position TEXT NOT NULL DEFAULT '',
            match_score INTEGER NOT NULL DEFAULT 0,
            analysis_summary TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            model_name TEXT NOT NULL DEFAULT '',
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            total_tokens INTEGER NOT NULL DEFAULT 0,
            estimated_cost REAL NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


def create_user(email: str, password_hash: str) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash),
    )
    user_id = cur.lastrowid
    conn.execute(
        "INSERT INTO usage (user_id, limit_count, used_count, reset_date) VALUES (?, 3, 0, ?)",
        (user_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email: str):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def get_usage(user_id: int):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM usage WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def deduct_usage(user_id: int) -> bool:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM usage WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return False
    if row["used_count"] >= row["limit_count"]:
        conn.close()
        return False
    conn.execute(
        "UPDATE usage SET used_count = used_count + 1, updated_at = ? WHERE user_id = ?",
        (datetime.now().isoformat(), user_id),
    )
    conn.commit()
    conn.close()
    return True


def get_remaining_count(user_id: int) -> int:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM usage WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return 0
    return max(0, row["limit_count"] - row["used_count"])


# ---- Analysis History CRUD ----


def create_analysis_record(
    user_id: int,
    resume_name: str = "",
    target_position: str = "",
    match_score: int = 0,
    analysis_summary: str = "",
) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO analysis_history (user_id, resume_name, target_position, match_score, analysis_summary) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, resume_name, target_position, match_score, analysis_summary),
    )
    record_id = cur.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_user_history(user_id: int, limit: int = 50):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM analysis_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_history_record(record_id: int, user_id: int) -> bool:
    conn = _get_conn()
    cur = conn.execute(
        "DELETE FROM analysis_history WHERE id = ? AND user_id = ?",
        (record_id, user_id),
    )
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ---- Admin CRUD ----


def get_user_count() -> dict:
    conn = _get_conn()
    total = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    today = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE date(created_at) = date('now')"
    ).fetchone()["c"]
    free = conn.execute("SELECT COUNT(*) as c FROM users WHERE plan='free'").fetchone()["c"]
    pro = conn.execute("SELECT COUNT(*) as c FROM users WHERE plan!='free'").fetchone()["c"]
    conn.close()
    return {"total": total, "today": today, "free": free, "pro": pro}


def get_analysis_stats() -> dict:
    conn = _get_conn()
    total = conn.execute("SELECT COUNT(*) as c FROM analysis_history").fetchone()["c"]
    today = conn.execute(
        "SELECT COUNT(*) as c FROM analysis_history WHERE date(created_at) = date('now')"
    ).fetchone()["c"]
    rows = conn.execute(
        "SELECT date(created_at) as d, COUNT(*) as c FROM analysis_history "
        "WHERE created_at >= datetime('now', '-7 days') GROUP BY d ORDER BY d"
    ).fetchall()
    trend = {r["d"]: r["c"] for r in rows}
    conn.close()
    return {"total": total, "today": today, "trend": trend}


def get_all_users():
    conn = _get_conn()
    rows = conn.execute(
        "SELECT u.*, COALESCE(g.limit_count, 3) as limit_count, "
        "COALESCE(g.used_count, 0) as used_count "
        "FROM users u LEFT JOIN usage g ON u.id = g.user_id "
        "ORDER BY u.id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_analysis_records(limit: int = 100):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT h.*, u.email "
        "FROM analysis_history h JOIN users u ON h.user_id = u.id "
        "ORDER BY h.id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_plan(user_id: int, new_plan: str) -> bool:
    conn = _get_conn()
    cur = conn.execute("UPDATE users SET plan = ? WHERE id = ?", (new_plan, user_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def update_user_role(user_id: int, new_role: str) -> bool:
    conn = _get_conn()
    cur = conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    ok = cur.rowcount > 0
    conn.commit()
    conn.close()
    return ok


def update_user_usage_limit(user_id: int, new_limit: int) -> bool:
    conn = _get_conn()
    row = conn.execute("SELECT id FROM usage WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        conn.execute("UPDATE usage SET limit_count = ? WHERE user_id = ?", (new_limit, user_id))
    else:
        conn.execute(
            "INSERT INTO usage (user_id, limit_count, used_count) VALUES (?, ?, 0)",
            (user_id, new_limit),
        )
    conn.commit()
    conn.close()
    return True
