import streamlit as st

from database import get_user_by_id
from usage_tracker import check_and_deduct, get_remaining


def require_auth():
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.warning("请先登录")
        st.session_state.page = "login"
        st.rerun()


def get_current_user():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def run_with_usage_check(user_id: int, analyze_func, resume_text: str, jd_text: str):
    ok, msg = check_and_deduct(user_id)
    if not ok:
        st.error(msg)
        return None
    result = analyze_func(resume_text, jd_text)
    remaining = get_remaining(user_id)
    st.caption(f"剩余分析次数: {remaining}")
    return result
