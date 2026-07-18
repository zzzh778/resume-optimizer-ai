import streamlit as st

from database import get_user_history, delete_history_record


def render_history():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return

    st.divider()
    st.markdown(
        "<h3 style='margin-bottom:16px;'>分析记录</h3>",
        unsafe_allow_html=True,
    )

    records = get_user_history(user_id, limit=50)

    if not records:
        st.markdown(
            '<div style="text-align:center;padding:32px 0;color:#64748b;font-size:14px;">'
            "暂无分析记录</div>",
            unsafe_allow_html=True,
        )
        return

    for record in records:
        score = record["match_score"]
        if score >= 80:
            color = "#4ade80"
        elif score >= 60:
            color = "#fbbf24"
        else:
            color = "#f87171"

        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #334155;border-radius:10px;'
            f'padding:14px 16px;margin-bottom:10px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-size:14px;font-weight:600;color:#f8fafc;">'
            f'{record["resume_name"] or "未命名"}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:2px;">'
            f'{record["created_at"]}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:24px;font-weight:800;color:{color};">{score}</div>'
            f'<div style="font-size:10px;color:#64748b;">/100</div>'
            f'</div>'
            f"</div>"
            f'<div style="font-size:12px;color:#64748b;margin-top:6px;">'
            f'{record["analysis_summary"]}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.caption("最多显示最近 50 条记录")
