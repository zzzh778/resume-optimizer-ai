import streamlit as st

from database import (
    get_user_count,
    get_analysis_stats,
    get_all_users,
    get_all_analysis_records,
    update_user_plan,
    update_user_role,
    update_user_usage_limit,
)
from token_tracker import get_token_stats


def render_admin():
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("请先登录")
        st.session_state.page = "login"
        st.rerun()
        return

    st.markdown(
        "<h2 style='margin-bottom:16px;'>管理后台</h2>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs(["📊 概览", "👥 用户管理", "📋 分析记录", "💰 Token 统计"])

    with tab1:
        render_overview()

    with tab2:
        render_user_management()

    with tab3:
        render_all_records()

    with tab4:
        render_token_stats()


def render_overview():
    stats = get_user_count()
    analysis = get_analysis_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总用户数", stats["total"])
    with col2:
        st.metric("今日新增", stats["today"])
    with col3:
        st.metric("免费用户", stats["free"])
    with col4:
        st.metric("付费用户", stats["pro"])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总分析次数", analysis["total"])
    with col2:
        st.metric("今日分析", analysis["today"])

    if analysis["trend"]:
        st.divider()
        st.caption("最近 7 天分析趋势")
        trend_data = analysis["trend"]
        for day in sorted(trend_data.keys()):
            bar_width = min(trend_data[day] * 20 + 20, 100)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;font-size:12px;">'
                f'<span style="width:80px;color:#94a3b8;">{day}</span>'
                f'<span style="height:20px;width:{bar_width}%;background:#6366f1;border-radius:4px;min-width:20px;"></span>'
                f'<span style="color:#cbd5e1;">{trend_data[day]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )


def render_user_management():
    users = get_all_users()

    st.caption(f"共 {len(users)} 名用户")
    st.divider()

    for user in users:
        remaining = max(0, user["limit_count"] - user["used_count"])
        with st.expander(
            f"#{user['id']}  {user['email']}  "
            f"[{user['role']}]  {user['plan']}  剩余{remaining}次"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**邮箱:** {user['email']}")
                st.markdown(f"**角色:** {user['role']}")
                st.markdown(f"**套餐:** {user['plan']}")
                st.markdown(f"**注册时间:** {user['created_at']}")
            with col2:
                st.markdown(f"**总次数:** {user['limit_count']}")
                st.markdown(f"**已用次数:** {user['used_count']}")
                st.markdown(f"**剩余次数:** {remaining}")

            st.divider()
            op_col1, op_col2, op_col3 = st.columns(3)

            with op_col1:
                new_plan = st.selectbox(
                    "修改套餐",
                    ["free", "pro", "enterprise"],
                    index=["free", "pro", "enterprise"].index(user["plan"]),
                    key=f"plan_{user['id']}",
                )
                if st.button("更新套餐", key=f"btn_plan_{user['id']}"):
                    if update_user_plan(user["id"], new_plan):
                        st.success("套餐已更新")
                        st.rerun()

            with op_col2:
                new_role = st.selectbox(
                    "修改角色",
                    ["user", "admin"],
                    index=["user", "admin"].index(user["role"]),
                    key=f"role_{user['id']}",
                )
                if st.button("更新角色", key=f"btn_role_{user['id']}"):
                    if update_user_role(user["id"], new_role):
                        st.success("角色已更新")
                        st.rerun()

            with op_col3:
                new_limit = st.number_input(
                    "总次数限制",
                    min_value=0,
                    max_value=9999,
                    value=user["limit_count"],
                    key=f"limit_{user['id']}",
                )
                if st.button("更新次数", key=f"btn_limit_{user['id']}"):
                    if update_user_usage_limit(user["id"], new_limit):
                        st.success("次数限制已更新")
                        st.rerun()


def render_all_records():
    records = get_all_analysis_records(limit=100)
    st.caption(f"共 {len(records)} 条分析记录")
    st.divider()

    if not records:
        st.markdown(
            '<div style="text-align:center;padding:32px 0;color:#64748b;">暂无分析记录</div>',
            unsafe_allow_html=True,
        )
        return

    for record in records:
        score = record["match_score"]
        color = "#4ade80" if score >= 80 else "#fbbf24" if score >= 60 else "#f87171"

        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #334155;border-radius:10px;'
            f'padding:12px 16px;margin-bottom:8px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-size:13px;color:#cbd5e1;">{record["email"]}</div>'
            f'<div style="font-size:11px;color:#64748b;margin-top:2px;">{record["created_at"]}</div>'
            f"</div>"
            f'<div style="text-align:right;">'
            f'<div style="font-size:20px;font-weight:700;color:{color};">{score}</div>'
            f'<div style="font-size:10px;color:#64748b;">/100</div>'
            f"</div></div>"
            f'<div style="font-size:12px;color:#64748b;margin-top:4px;">'
            f'{record["analysis_summary"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def render_token_stats():
    stats = get_token_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("今日 Tokens", f"{stats['today']['tokens']:,}")
    with col2:
        st.metric("总 Tokens", f"{stats['total']['tokens']:,}")
    with col3:
        st.metric("今日成本", f"${stats['today']['cost']:.6f}")
    with col4:
        st.metric("总成本", f"${stats['total']['cost']:.6f}")

    st.divider()
    st.caption("今日明细")
    st.markdown(
        f'<div style="display:flex;gap:16px;font-size:13px;color:#94a3b8;">'
        f"<span>Input: {stats['today']['input']:,} tokens</span>"
        f"<span>Output: {stats['today']['output']:,} tokens</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("资源使用总计")
    st.markdown(
        f'<div style="display:flex;gap:16px;font-size:13px;color:#94a3b8;">'
        f"<span>Input: {stats['total']['input']:,} tokens</span>"
        f"<span>Output: {stats['total']['output']:,} tokens</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if stats["models"]:
        st.divider()
        st.caption("模型使用排行")
        for m in stats["models"]:
            st.markdown(
                f'<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;'
                f'padding:10px 14px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:13px;">'
                f'<span style="color:#cbd5e1;">{m["model_name"]}</span>'
                f'<span style="color:#f8fafc;">{m["calls"]} 次调用</span>'
                f"</div>"
                f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-top:4px;">'
                f"<span>{m['tokens']:,} tokens</span>"
                f"<span>${m['cost']:.6f}</span>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
