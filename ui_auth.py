import streamlit as st

from auth import login, register


def render_login():
    st.markdown(
        "<h2 style='text-align:center;margin-bottom:24px;'>登录</h2>",
        unsafe_allow_html=True,
    )
    with st.form("login_form"):
        email = st.text_input("邮箱", placeholder="your@email.com")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录", type="primary", use_container_width=True)
        if submitted:
            if not email or not password:
                st.warning("请填写邮箱和密码")
                return
            user = login(email, password)
            if user:
                st.session_state.user_id = user["id"]
                st.session_state.user_email = user["email"]
                st.session_state.page = "main"
                st.rerun()
            else:
                st.error("邮箱或密码错误")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("没有账号？立即注册", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()


def render_register():
    st.markdown(
        "<h2 style='text-align:center;margin-bottom:24px;'>注册</h2>",
        unsafe_allow_html=True,
    )
    with st.form("register_form"):
        email = st.text_input("邮箱", placeholder="your@email.com")
        password = st.text_input("密码", type="password", placeholder="至少6位")
        confirm = st.text_input("确认密码", type="password")
        submitted = st.form_submit_button("注册", type="primary", use_container_width=True)
        if submitted:
            if not email or not password:
                st.warning("请填写邮箱和密码")
                return
            if password != confirm:
                st.error("两次密码不一致")
                return
            if len(password) < 6:
                st.error("密码至少6位")
                return
            msg = register(email, password)
            if msg:
                st.error(msg)
            else:
                st.success("注册成功，请登录")
                st.session_state.page = "login"
                st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("已有账号？去登录", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
