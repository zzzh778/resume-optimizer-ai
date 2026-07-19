import os

import requests

RESEND_API_URL = "https://api.resend.com/emails"


def send_verification_email(to_email: str, code: str) -> tuple[bool, str]:
    api_key = os.getenv("RESEND_API_KEY", "")
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")

    if not api_key:
        print(f"[DEV MODE] Verification code for {to_email}: {code}")
        return True, "[DEV] Code printed to console (no RESEND_API_KEY set)"

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": from_email,
                "to": [to_email],
                "subject": "您的邮箱验证码",
                "html": f"""
                <div style="max-width:480px;margin:0 auto;padding:32px 24px;background:#111827;border-radius:12px;font-family:sans-serif;">
                    <h2 style="color:#f8fafc;margin:0 0 16px;">ResumeOptimizer AI</h2>
                    <p style="color:#cbd5e1;font-size:14px;line-height:1.6;">您的邮箱验证码为：</p>
                    <div style="text-align:center;padding:16px 0;">
                        <span style="display:inline-block;font-size:36px;font-weight:700;color:#6366f1;letter-spacing:8px;background:#1e293b;padding:12px 24px;border-radius:8px;">{code}</span>
                    </div>
                    <p style="color:#94a3b8;font-size:12px;">验证码有效期为10分钟。如果不是您本人操作，请忽略此邮件。</p>
                </div>
                """,
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return True, "验证码已发送"
        return False, f"邮件发送失败: {resp.text}"
    except Exception as e:
        return False, f"邮件服务异常: {e}"
