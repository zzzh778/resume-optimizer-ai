"""
管理员账号初始化脚本。

用法：
    python create_admin.py              # 首次创建
    python create_admin.py --reset       # 重置密码（仅管理员）
    python create_admin.py --force       # 强制重置密码
"""

import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import init_db, get_user_by_email
from auth import hash_password

ADMIN_EMAIL = "admin@resume-ai.com"


def generate_password(length=16) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def main():
    init_db()

    existing = get_user_by_email(ADMIN_EMAIL)
    force_reset = "--force" in sys.argv or "--reset" in sys.argv

    if existing and not force_reset:
        print(f"[SKIP] 管理员账号已存在: {ADMIN_EMAIL}")
        print(f"       如需重置密码: python create_admin.py --reset")
        return

    password = generate_password()
    password_hash = hash_password(password)
    admin_plan = "pro"

    from database import _get_conn
    conn = _get_conn()

    if existing and force_reset:
        conn.execute(
            "UPDATE users SET password_hash = ?, plan = ?, role = 'admin' WHERE email = ?",
            (password_hash, admin_plan, ADMIN_EMAIL),
        )
        action = "密码已重置"
    else:
        conn.execute(
            "INSERT INTO users (email, password_hash, plan, role) VALUES (?, ?, ?, 'admin')",
            (ADMIN_EMAIL, password_hash, admin_plan),
        )
        action = "账号创建成功"
        from datetime import datetime
        uid = conn.execute("SELECT id FROM users WHERE email = ?", (ADMIN_EMAIL,)).fetchone()
        if uid:
            conn.execute(
                "INSERT INTO usage (user_id, limit_count, used_count, reset_date) VALUES (?, 999, 0, ?)",
                (uid[0], datetime.now().isoformat()),
            )
    conn.commit()
    conn.close()

    print("=" * 50)
    print(f"  管理员{action}")
    print("=" * 50)
    print(f"  登录邮箱: {ADMIN_EMAIL}")
    print(f"  登录密码: {password}")
    print("=" * 50)
    print("  请立即登录并修改密码。")
    print("=" * 50)


if __name__ == "__main__":
    main()
