import re
import secrets
from datetime import datetime, timedelta

import streamlit as st

from auth import login, register
from database import save_verification_code, verify_email_code, get_user_by_email
from mailer import send_verification_email


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
                if not user.get("is_verified"):
                    st.error("请先完成邮箱验证")
                    return
                st.session_state.user_id = user["id"]
                st.session_state.user_email = user["email"]
                st.session_state.page = "main"
                st.rerun()
            else:
                st.error("邮箱或密码错误")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("没有账号？立即注册", use_container_width=True):
            st.session_state.reg_step = "form"
            st.session_state.page = "register"
            st.rerun()


def render_register():
    step = st.session_state.get("reg_step", "form")

    if step == "form":
        _render_reg_form()
    elif step == "verify":
        _render_verify_code()


def _render_reg_form():
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
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                st.error("邮箱格式不正确")
                return
            if password != confirm:
                st.error("两次密码不一致")
                return
            if len(password) < 6:
                st.error("密码至少6位")
                return
            # Check duplicate
            existing = get_user_by_email(email)
            if existing:
                st.error("该邮箱已注册")
                return
            # Create user (unverified)
            msg = register(email, password)
            if msg:
                st.error(msg)
                return
            # Generate 6-digit code
            code = f"{secrets.randbelow(900000) + 100000}"
            expire = (datetime.now() + timedelta(minutes=10)).isoformat()
            sent_time = datetime.now().isoformat()
            save_verification_code(email, code, expire, sent_time)
            ok, msg = send_verification_email(email, code)
            if not ok:
                # Send failed, clear the code so it can't be used
                from database import _get_conn as _gconn
                _c = _gconn()
                _c.execute(
                    "UPDATE users SET verification_code = NULL, verification_expire_time = NULL, "
                    "verification_attempts = 0 WHERE email = ?",
                    (email,),
                )
                _c.commit()
                _c.close()
                st.error(f"验证码发送失败: {msg}，请稍后重试")
                # Delete the unverified user
                _c2 = _gconn()
                _c2.execute("DELETE FROM users WHERE email = ? AND is_verified = 0", (email,))
                _c2.commit()
                _c2.close()
                return
            # Store in session for verify step
            st.session_state.reg_email = email
            st.session_state.reg_code = code
            st.session_state.reg_expire = expire
            st.session_state.reg_step = "verify"
            st.rerun()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("已有账号？去登录", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


def _render_verify_code():
    from database import (_get_conn as _gconn, get_user_by_email as _gube,
                          get_verification_sent_time as _gst)
    email = st.session_state.get("reg_email", "")

    # Check cooldown
    _sent = _gst(email)
    _cooldown = 0
    if _sent:
        _elapsed = (datetime.now() - datetime.fromisoformat(_sent)).total_seconds()
        _cooldown = max(0, 60 - int(_elapsed))

    _cooldown_text = f'<p style="text-align:center;color:#fbbf24;font-size:12px;">{_cooldown}秒后可重新发送</p>' if _cooldown > 0 else ""
    st.markdown(
        f"<h2 style='text-align:center;margin-bottom:8px;'>验证邮箱</h2>"
        f"<p style='text-align:center;color:#94a3b8;font-size:14px;'>验证码已发送至<br/>"
        f"<strong style='color:#f8fafc;'>{email}</strong></p>"
        f"{_cooldown_text}",
        unsafe_allow_html=True,
    )

    with st.form("verify_form"):
        code = st.text_input("验证码", placeholder="输入6位数字验证码", max_chars=6)
        submitted = st.form_submit_button("验证", type="primary", use_container_width=True)
        if submitted:
            if not code or len(code) != 6 or not code.isdigit():
                st.error("请输入6位数字验证码")
                return
            ok, msg = verify_email_code(email, code)
            if ok:
                _user = _gube(email)
                st.success("邮箱验证成功！")
                if _user:
                    st.session_state.user_id = _user["id"]
                    st.session_state.user_email = _user["email"]
                    st.session_state.reg_step = ""
                    st.session_state.page = "main"
                    st.rerun()
            else:
                st.error(msg)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        _disabled = _cooldown > 0
        if st.button(
            "重新发送验证码",
            use_container_width=True,
            disabled=_disabled,
            help=f"请等待{_cooldown}秒" if _disabled else None,
        ):
            code = f"{secrets.randbelow(900000) + 100000}"
            expire = (datetime.now() + timedelta(minutes=10)).isoformat()
            sent_time = datetime.now().isoformat()
            save_verification_code(email, code, expire, sent_time)
            ok, msg = send_verification_email(email, code)
            if ok:
                st.session_state.reg_code = code
                st.session_state.reg_expire = expire
                st.success("验证码已重新发送")
            else:
                st.error(f"发送失败: {msg}")
                _c = _gconn()
                _c.execute(
                    "UPDATE users SET verification_code = NULL WHERE email = ?", (email,)
                )
                _c.commit()
                _c.close()
            st.rerun()
        if st.button("返回重新填写", use_container_width=True):
            st.session_state.reg_step = "form"
            st.rerun()
