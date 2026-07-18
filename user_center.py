import streamlit as st

from database import get_user_by_id, get_usage
from usage_tracker import get_remaining


def render_user_center():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return
    user = get_user_by_id(user_id)
    if not user:
        return
    usage = get_usage(user_id)
    remaining = get_remaining(user_id)

    st.divider()
    st.markdown(
        "<h3 style='margin-bottom:16px;'>用户中心</h3>",
        unsafe_allow_html=True,
    )

    info_rows = [
        ("邮箱", user["email"]),
        ("用户ID", str(user["id"])),
        ("套餐", {"free": "免费版", "pro": "专业版", "enterprise": "企业版"}.get(user["plan"], user["plan"])),
        ("角色", {"user": "普通用户", "admin": "管理员"}.get(user["role"], user["role"])),
        ("注册时间", user["created_at"]),
    ]
    for label, value in info_rows:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
            f'border-bottom:1px solid #334155;font-size:14px;">'
            f'<span style="color:#94a3b8;">{label}</span>'
            f'<span style="color:#f8fafc;">{value}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;padding:12px 0;font-size:14px;">'
        f'<span style="color:#94a3b8;">剩余分析次数</span>'
        f'<span style="color:#6ee7b7;font-weight:700;">{remaining} / {usage["limit_count"] if usage else 3}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )
