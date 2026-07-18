import json
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from core.parser import extract_text
from database import init_db, get_usage
from usage_tracker import get_remaining
from middleware import run_with_usage_check
from ui_auth import render_login, render_register
from user_center import render_user_center
from history import render_history
from admin import render_admin

st.set_page_config(page_title="ResumeOptimizer AI", page_icon="✨", layout="wide")

init_db()

_CSS = """
<style>
.stApp{background-color:#0b1120}
section[data-testid="stSidebar"]{min-width:240px;max-width:280px;background:#0b1120;border-right:1px solid #1f2937}
section[data-testid="stSidebar"] .stApp{background:#0b1120}
section.main .block-container{padding-top:2rem;padding-bottom:2rem}
.hero-section{text-align:center;padding:32px 16px 24px;background:linear-gradient(135deg,#0b1120,#1e3a5f);border-radius:12px;margin-bottom:16px}
.hero-title{font-size:36px;font-weight:700;color:#f8fafc;margin:0}
.hero-subtitle{font-size:16px;color:#cbd5e1;margin-top:8px}
.privacy-banner{display:flex;align-items:center;gap:8px;margin-bottom:20px;padding:10px 16px;border-radius:10px;border:1px solid #334155;background:#1e293b;font-size:13px;color:#cbd5e1}
.input-card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;height:100%;transition:box-shadow .2s,border-color .2s}
.input-card:hover{box-shadow:0 4px 24px rgba(0,0,0,.4);border-color:#475569}
.input-card-icon{font-size:24px;margin-bottom:8px}
.input-card-title{font-size:16px;font-weight:600;color:#f8fafc;margin-bottom:4px}
.input-card-hint{font-size:12px;color:#94a3b8;margin-bottom:12px}
.file-status{padding:6px 12px;border-radius:8px;font-size:13px;font-weight:500}
.file-status-ready{background:#064e3b;color:#6ee7b7}
.file-status-empty{background:rgba(51,65,85,.35);color:#94a3b8}
.char-count{font-size:11px;color:#94a3b8;text-align:right;margin-top:4px}
.cta-container{text-align:center;margin:24px 0}
div.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1e40af,#3b82f6)!important;border:none!important;border-radius:12px!important;font-size:16px!important;font-weight:600!important;padding:12px 40px!important;color:#f8fafc!important;transition:all .2s!important}
div.stButton>button[kind="primary"]:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(37,99,235,.4)!important;filter:brightness(1.1)}
.dashboard-header{text-align:center;margin-bottom:24px;padding:20px 0;border-bottom:1px solid #334155}
.dashboard-header h2{margin:0;color:#f8fafc}
.score-card{background:linear-gradient(135deg,#111827,#1e293b);border:1px solid #334155;border-radius:12px;padding:32px 24px;text-align:center;margin-bottom:24px;position:relative;overflow:hidden}
.score-ring{display:inline-flex;align-items:center;justify-content:center;width:140px;height:140px;border-radius:50%;margin-bottom:12px;position:relative}
.score-ring-inner{position:absolute;top:12px;left:12px;right:12px;bottom:12px;border-radius:50%;background:rgba(17,24,39,.92);display:flex;align-items:center;justify-content:center;flex-direction:column}
.score-number{font-size:48px;font-weight:800;line-height:1}
.score-total{font-size:16px;color:#94a3b8}
.score-label{font-size:16px;color:#cbd5e1;font-weight:600;margin-top:4px}
.score-summary{font-size:14px;color:#94a3b8;margin-top:8px;line-height:1.5;max-width:480px;margin-left:auto;margin-right:auto}
.score-high .score-ring{background:conic-gradient(#4ade80 var(--pct),rgba(148,163,184,.08) var(--pct))}
.score-mid .score-ring{background:conic-gradient(#fbbf24 var(--pct),rgba(148,163,184,.08) var(--pct))}
.score-low .score-ring{background:conic-gradient(#f87171 var(--pct),rgba(148,163,184,.08) var(--pct))}
.score-high .score-number{color:#4ade80}
.score-mid .score-number{color:#fbbf24}
.score-low .score-number{color:#f87171}
.section-title{font-size:15px;font-weight:600;color:#e2e8f0;margin-bottom:10px;display:flex;align-items:center;gap:6px}
.section-card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:18px;margin-bottom:14px;transition:border-color .2s}
.section-card:hover{border-color:#475569}
.strength-card{background:#1e293b;border:1px solid #334155;border-left:4px solid #047857;border-radius:0 12px 12px 0;padding:18px;margin-bottom:14px}
.risk-card{background:#1e293b;border:1px solid #334155;border-left:4px solid #B91C1C;border-radius:0 12px 12px 0;padding:18px;margin-bottom:14px}
.count-badge{display:inline-flex;align-items:center;gap:4px;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600}
.count-badge.green{background:#064e3b;color:#6ee7b7}
.count-badge.red{background:#450a0a;color:#fca5a5}
.count-badge.blue{background:#172554;color:#93c5fd}
.tag{display:inline-block;padding:4px 12px;border-radius:20px;font-size:13px;margin:2px 4px 2px 0;font-weight:500;border:1px solid transparent;transition:border-color .2s}
.tag-green{background:#064e3b;color:#6ee7b7;border-color:#047857}
.tag-red{background:#450a0a;color:#fca5a5;border-color:#991b1b}
.tag-blue{background:#172554;color:#93c5fd;border-color:#1D4ED8}
.tag-neutral{background:#1e293b;color:#94a3b8;border-color:#334155}
.gap-card{border-left:3px solid;border-radius:0 10px 10px 0;padding:12px 14px;margin-bottom:8px;background:#1e293b;transition:border-color .2s}
.gap-high{border-color:#B91C1C}
.gap-mid{border-color:#f59e0b}
.gap-low{border-color:#047857}
.gap-skill{font-weight:600;font-size:14px;margin-bottom:4px;color:#f8fafc}
.gap-detail{font-size:13px;color:#94a3b8;line-height:1.5}
.compare-row{display:flex;gap:12px;margin:10px 0;flex-wrap:wrap;align-items:stretch}
.compare-box{flex:1;min-width:180px;padding:14px;border-radius:10px;font-size:13px;line-height:1.6;transition:border-color .2s}
.compare-box.original{background:#450a0a;color:#fecaca;border:1px solid #991b1b}
.compare-box.improved{background:#064e3b;color:#bbf7d0;border:1px solid #047857}
.compare-label{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;opacity:.75}
.compare-arrow{display:flex;align-items:center;justify-content:center;font-size:20px;color:#94a3b8;min-width:24px}
.suggestion-reason{font-size:13px;color:#94a3b8;margin-top:10px;padding:10px 14px;background:#111827;border-radius:8px;border:1px solid #334155}
.step-marker{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:#1e40af;color:#f8fafc;font-size:12px;font-weight:700;margin-right:8px;flex-shrink:0}
.advice-block{background:linear-gradient(135deg,#1e293b,#111827);border-radius:10px;padding:16px 20px;margin-top:14px;font-size:14px;color:#cbd5e1;border-left:4px solid #2563eb}
.feedback-container{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;margin-top:24px;text-align:center}
div[data-testid="stExpander"] details{background:#1e293b;border:1px solid #334155;border-radius:10px;transition:border-color .2s}
div[data-testid="stExpander"] details:hover{border-color:#475569}
div[data-testid="stExpander"] summary{color:#e2e8f0;font-weight:500}
div[data-testid="stExpander"] details[open] summary{border-bottom:1px solid #334155}
.stTextArea textarea{background:#111827!important;border-radius:10px!important;border:1px solid #334155!important;color:#f8fafc!important;transition:border-color .2s}
.stTextArea textarea:focus{border-color:#2563eb!important;box-shadow:0 0 0 3px rgba(37,99,235,.2)!important}
.stTextArea textarea::placeholder{color:#94a3b8!important}
[data-testid="stFileUploader"] section{background:#111827!important;border-radius:10px!important;border:1px dashed #334155!important;transition:border-color .2s}
[data-testid="stFileUploader"] p{color:#94a3b8!important}
div.stAlert{border-radius:10px!important}
div[data-testid="stNotification"]{background:#1e293b!important;border-color:#334155!important;color:#f8fafc!important}
div[data-testid="stNotification"] [kind="warning"],.stAlert[kind="warning"]{background:#451a03!important;border-color:#78350f!important;color:#fde68a!important}
div[data-testid="stNotification"] [kind="error"],.stAlert[kind="error"]{background:#450a0a!important;border-color:#991b1b!important;color:#fca5a5!important}
div.stButton>button:not([kind="primary"]){background:#334155!important;color:#cbd5e1!important;border:1px solid #475569!important;border-radius:10px!important;transition:all .2s}
div.stButton>button:not([kind="primary"]):hover{background:#475569!important;color:#f8fafc!important;border-color:#64748b!important}
.stCaption{color:#94a3b8}
.stMarkdown,div[data-testid="stMarkdown"] p,div[data-testid="stMarkdown"] span,.stMarkdown p{color:#cbd5e1}
@media(max-width:768px){
.hero-title{font-size:24px}
.hero-subtitle{font-size:14px}
.input-card{padding:14px}
.compare-row{flex-direction:column}
.compare-box{min-width:100%}
.score-card{padding:20px 12px}
.score-ring{width:110px;height:110px}
.score-ring-inner{top:10px;left:10px;right:10px;bottom:10px}
.score-number{font-size:36px}
.score-total{font-size:13px}
.fade-in{opacity:1!important;transform:translateY(0)!important}
}
@keyframes skeleton-pulse{0%,100%{opacity:.4}50%{opacity:.8}}
@keyframes score-pop{0%{transform:scale(.6);opacity:0}60%{transform:scale(1.08)}100%{transform:scale(1);opacity:1}}
@keyframes fade-up{0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
.skeleton{background:linear-gradient(90deg,#1e293b 25%,#334155 50%,#1e293b 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px}
.skeleton-row{height:16px;margin-bottom:8px}
.skeleton-row.short{width:60%}
.skeleton-tag{display:inline-block;width:64px;height:28px;border-radius:20px;margin:2px 4px;animation:skeleton-pulse 1.5s infinite}
.skeleton-card{padding:20px;border-radius:12px;border:1px solid #334155;margin-bottom:14px}
.skeleton-ring{width:140px;height:140px;border-radius:50%;margin:0 auto 12px;animation:skeleton-pulse 1.5s infinite;background:#1e293b}
.score-animate{animation:score-pop .6s ease-out}
.section-card.animate{animation:fade-up .5s ease-out forwards;opacity:0;transform:translateY(8px)}
.section-card.animate:nth-child(1){animation-delay:.1s}
.section-card.animate:nth-child(2){animation-delay:.2s}
.section-card.animate:nth-child(3){animation-delay:.3s}
.tag-icon{display:inline-flex;align-items:center;gap:4px}
.tag-icon svg{width:12px;height:12px;flex-shrink:0}
.hero-logo{display:block;margin:0 auto 12px;width:48px;height:48px}
</style>
"""


def _inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def _write_feedback(fb_type: str, note: str = ""):
    entry = {"ts": datetime.now().isoformat(timespec="seconds"), "type": fb_type, "note": note}
    log_path = Path(__file__).resolve().parent / "feedback.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---- Session State ----
if "result" not in st.session_state:
    st.session_state.result = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "resume_text_cache" not in st.session_state:
    st.session_state.resume_text_cache = ""
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""
if "analyzing" not in st.session_state:
    st.session_state.analyzing = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""


# ================================================================
# UI Components
# ================================================================


def render_hero():
    st.markdown(
        """
        <div class="hero-section">
            <svg class="hero-logo" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="8" y="4" width="32" height="40" rx="4" fill="#1e40af" stroke="#3b82f6" stroke-width="1.5"/>
                <rect x="13" y="10" width="22" height="3" rx="1.5" fill="#93c5fd" opacity="0.6"/>
                <rect x="13" y="16" width="18" height="3" rx="1.5" fill="#93c5fd" opacity="0.4"/>
                <rect x="13" y="22" width="20" height="3" rx="1.5" fill="#93c5fd" opacity="0.3"/>
                <circle cx="34" cy="36" r="7" fill="#2563eb" stroke="#3b82f6" stroke-width="1.5"/>
                <path d="M32.5 36l3-3 3 3M34 33v6" stroke="#f8fafc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="hero-title">ResumeOptimizer AI</div>
            <div class="hero-subtitle">AI 驱动的简历优化助手 &mdash; 找到简历与目标岗位之间的差距，获取精准优化建议</div>
    """,
        unsafe_allow_html=True,
    )
    cols = st.columns([1, 0.15, 1, 0.15, 1, 0.15, 1])
    steps = [
        ("📄", "上传简历"),
        ("💼", "输入岗位"),
        ("🤖", "AI 分析"),
        ("✨", "优化建议"),
    ]
    for i, (icon, label) in enumerate(steps):
        col_idx = i * 2
        with cols[col_idx]:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.08);border-radius:10px;'
                f'padding:8px 12px;color:#e2e8f0;font-size:13px;text-align:center;">'
                f'{icon} {label}</div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def render_privacy_notice():
    st.markdown(
        '<div class="privacy-banner">'
        '<span style="font-size:16px;">🔒</span> '
        "<span>您的简历内容仅用于本次 AI 分析，<strong>不会保存或上传</strong>到任何服务器</span>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_input_section():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="input-card"><div class="input-card-icon">📄</div>'
            '<div class="input-card-title">上传简历</div>'
            '<div class="input-card-hint">支持 PDF / DOCX 格式</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "选择文件", type=["pdf", "docx"], label_visibility="collapsed"
        )
        resume_text = ""
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            try:
                resume_text = extract_text(tmp_path)
                st.session_state.resume_text_cache = resume_text
                st.session_state.resume_filename = uploaded_file.name
                st.markdown(
                    f'<div class="file-status file-status-ready">'
                    f'✅ 解析成功 &middot; {len(resume_text)} 字符</div>',
                    unsafe_allow_html=True,
                )
                with st.expander("预览内容"):
                    st.text(resume_text[:1000])
            except ValueError as e:
                st.markdown(
                    f'<div class="file-status" style="background:#fef2f2;color:#991b1b;">'
                    f'⚠️ {e}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.markdown(
                    f'<div class="file-status" style="background:#fef2f2;color:#991b1b;">'
                    f'⚠️ 文件读取失败: {e}</div>',
                    unsafe_allow_html=True,
                )
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        elif not st.session_state.resume_text_cache:
            st.markdown(
                '<div class="file-status file-status-empty">等待上传...</div>',
                unsafe_allow_html=True,
            )
        else:
            resume_text = st.session_state.resume_text_cache
            st.markdown(
                f'<div class="file-status file-status-ready">'
                f'✅ 已解析 &middot; {len(resume_text)} 字符</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="input-card"><div class="input-card-icon">💼</div>'
            '<div class="input-card-title">目标岗位 JD</div>'
            '<div class="input-card-hint">粘贴职位描述，AI 将分析匹配度</div>',
            unsafe_allow_html=True,
        )
        jd_text = st.text_area(
            "岗位描述",
            height=180,
            placeholder="请在此粘贴目标岗位的职位描述...\n\n例如：\n岗位名称：Python 开发工程师\n任职要求：\n- 3年 Python 经验\n- 熟悉 Django/Flask\n- ...",
            label_visibility="collapsed",
        )
        if jd_text.strip():
            st.markdown(
                f'<div class="char-count">{len(jd_text)} 字符</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    return resume_text or st.session_state.resume_text_cache, jd_text


def render_result_dashboard(result):
    score = result.match_score
    if score >= 80:
        score_class = "score-high"
        level = "优秀"
        level_color = "#047857"
    elif score >= 60:
        score_class = "score-mid"
        level = "良好"
        level_color = "#92400e"
    else:
        score_class = "score-low"
        level = "需提升"
        level_color = "#B91C1C"

    st.divider()
    st.markdown(
        '<div class="dashboard-header"><h2>分析报告</h2></div>',
        unsafe_allow_html=True,
    )

    # ---- Score Card with Ring ----
    pct = f"{score}%"
    st.markdown(
        f'<div class="score-card {score_class}">'
        f'<div class="score-ring" style="--pct:{pct}">'
        f'<div class="score-ring-inner">'
        f'<div class="score-number score-animate">{score}</div>'
        f'<div class="score-total">/ 100</div>'
        f'</div>'
        f'</div>'
        f'<div class="score-label">综合匹配度 <span style="color:{level_color};font-weight:700;">{level}</span></div>'
        f'<div class="score-summary">{result.match_summary}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ---- Three-column overview ----
    c1, c2, c3 = st.columns(3)
    with c1:
        cnt = len(result.matched_skills)
        st.markdown(
            f'<div style="text-align:center;padding:16px 8px;background:#1e293b;border:1px solid #334155;border-radius:12px;">'
            f'<div style="font-size:28px;font-weight:800;color:#047857;">{cnt}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:4px;">匹配技能</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        cnt = len(result.missing_skills)
        st.markdown(
            f'<div style="text-align:center;padding:16px 8px;background:#1e293b;border:1px solid #334155;border-radius:12px;">'
            f'<div style="font-size:28px;font-weight:800;color:#B91C1C;">{cnt}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:4px;">技能缺口</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        cnt = len(result.optimization_suggestions)
        st.markdown(
            f'<div style="text-align:center;padding:16px 8px;background:#1e293b;border:1px solid #334155;border-radius:12px;">'
            f'<div style="font-size:28px;font-weight:800;color:#1D4ED8;">{cnt}</div>'
            f'<div style="font-size:12px;color:#94a3b8;margin-top:4px;">优化建议</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Strengths & Risks with accent borders ----
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown('<div class="strength-card animate">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-title">匹配优势 '
            f'<span class="count-badge green">{len(result.matched_skills)}</span></div>',
            unsafe_allow_html=True,
        )
        if result.matched_skills:
            st.markdown(
                " ".join(
                    f'<span class="tag tag-green tag-icon"><svg viewBox="0 0 12 12" fill="none"><path d="M2.5 6l2.5 2.5 4.5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>{s}</span>'
                    for s in result.matched_skills
                ),
                unsafe_allow_html=True,
            )
        else:
            st.caption("暂无明显匹配的技能")
        st.markdown("</div>", unsafe_allow_html=True)

    with sc2:
        st.markdown('<div class="risk-card animate">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-title">技能缺口 '
            f'<span class="count-badge red">{len(result.missing_skills)}</span></div>',
            unsafe_allow_html=True,
        )
        if result.missing_skills:
            st.markdown(
                " ".join(
                    f'<span class="tag tag-red tag-icon"><svg viewBox="0 0 12 12" fill="none"><path d="M6 1v6M6 9.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>{s}</span>'
                    for s in result.missing_skills
                ),
                unsafe_allow_html=True,
            )
        else:
            st.caption("无技能缺口")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Experience Gap ----
    if result.experience_gap:
        st.markdown(
            f'<div style="background:#1e293b;border:1px solid #334155;border-radius:12px;'
            f'padding:14px 18px;margin-bottom:14px;font-size:14px;color:#94a3b8;">'
            f'<span style="font-weight:600;color:#f8fafc;">经验评估：</span>'
            f'{result.experience_gap}</div>',
            unsafe_allow_html=True,
        )

    # ---- Skill Gaps Detail ----
    if result.skill_gaps:
        st.markdown('<div class="section-card animate">', unsafe_allow_html=True)
        importance_labels = {"high": "高", "medium": "中", "low": "低"}
        st.markdown(
            f'<div class="section-title">技能差距分析 '
            f'<span class="count-badge blue">{len(result.skill_gaps)}</span></div>',
            unsafe_allow_html=True,
        )
        for gap in result.skill_gaps:
            imp = gap.importance if gap.importance in ("high", "mid", "low") else "mid"
            gap_class = f"gap-{imp}"
            label = importance_labels.get(gap.importance, gap.importance)
            imp_colors = {"high": "#B91C1C", "mid": "#92400e", "low": "#047857"}
            st.markdown(
                f'<div class="gap-card {gap_class}">'
                f'<div class="gap-skill">{gap.skill} '
                f'<span style="font-size:11px;color:{imp_colors.get(imp,"#94a3b8")};'
                f'font-weight:500;">{label}优先级</span></div>'
                f'<div class="gap-detail">{gap.suggestion}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Optimization Suggestions ----
    if result.optimization_suggestions:
        st.markdown('<div class="section-card animate">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-title">优化建议 '
            f'<span class="count-badge blue">{len(result.optimization_suggestions)}</span></div>',
            unsafe_allow_html=True,
        )
        for i, suggestion in enumerate(result.optimization_suggestions, 1):
            expander_title = (
                f'<span class="step-marker">{i}</span> {suggestion.section}'
            )
            with st.expander(expander_title):
                st.markdown(
                    '<div class="compare-row">'
                    f'<div class="compare-box original">'
                    f'<div class="compare-label">原文</div>'
                    f'{suggestion.original or "（无原文）"}'
                    f'</div>'
                    f'<span class="compare-arrow">→</span>'
                    f'<div class="compare-box improved">'
                    f'<div class="compare-label">优化建议</div>'
                    f'{suggestion.improved or "（无建议）"}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if suggestion.reason:
                    st.markdown(
                        f'<div class="suggestion-reason">'
                        f'<strong>修改原因：</strong>{suggestion.reason}</div>',
                        unsafe_allow_html=True,
                    )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Keywords ----
    if result.keyword_recommendations:
        st.markdown('<div class="section-card animate">', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">建议添加的关键词</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            " ".join(
                f'<span class="tag tag-blue tag-icon"><svg viewBox="0 0 12 12" fill="none"><path d="M3 2v8M5 2l-1 8M8 2l-1 8M10 2v8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>{kw}</span>'
                for kw in result.keyword_recommendations
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Overall Advice ----
    if result.overall_advice:
        st.markdown(
            f'<div class="advice-block">{result.overall_advice}</div>',
            unsafe_allow_html=True,
        )


def render_feedback():
    st.markdown(
        '<div class="feedback-container">',
        unsafe_allow_html=True,
    )
    if st.session_state.feedback_given:
        st.markdown(
            '<div style="font-size:16px;color:#166534;">✅ 感谢您的反馈！</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:15px;font-weight:600;color:#f8fafc;margin-bottom:12px;">'
            "这个分析对您有帮助吗？</div>",
            unsafe_allow_html=True,
        )
        fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 3])
        with fb_col1:
            if st.button("👍 有帮助", use_container_width=True):
                _write_feedback("helpful")
                st.session_state.feedback_given = True
                st.rerun()
        with fb_col2:
            if st.button("👎 没帮助", use_container_width=True):
                _write_feedback("not_helpful")
                st.session_state.feedback_given = True
                st.rerun()
        with fb_col3:
            fb_note = st.text_input(
                "备注（可选）",
                placeholder="有什么建议或想法？",
                label_visibility="collapsed",
            )
            if fb_note and st.button("提交备注", key="fb_note_btn"):
                _write_feedback("helpful", fb_note)
                st.session_state.feedback_given = True
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================
# Main
# ================================================================
# Main App
# ================================================================

_inject_css()

page = st.session_state.page

if page == "login":
    render_login()
elif page == "register":
    render_register()
elif page in ("main", "profile", "history", "admin"):
    with st.sidebar:
        st.markdown(
            f'<div style="padding:8px 0;">'
            f'<div style="font-size:13px;color:#94a3b8;">当前用户</div>'
            f'<div style="font-size:15px;font-weight:600;color:#f8fafc;">{st.session_state.user_email}</div>'
            f'<div style="margin-top:8px;font-size:13px;color:#94a3b8;">剩余分析次数: '
            f'<span style="color:#6ee7b7;font-weight:700;">{get_remaining(st.session_state.user_id)}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("📄 AI 分析", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
        if st.button("👤 用户中心", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()
        if st.button("📋 分析记录", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()
        from database import get_user_by_id
        _cu = get_user_by_id(st.session_state.user_id)
        if _cu and _cu["role"] == "admin":
            if st.button("🔧 管理后台", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()
        st.divider()
        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if page == "profile":
        render_user_center()
    elif page == "history":
        render_history()
    elif page == "admin":
        from database import get_user_by_id as _auth_check
        _cu = _auth_check(st.session_state.user_id)
        if _cu and _cu["role"] == "admin":
            render_admin()
        else:
            st.error("无权限访问管理后台")
            st.session_state.page = "main"
            st.rerun()
    elif page == "main":
        render_hero()
        render_privacy_notice()

        resume_text, jd_text = render_input_section()
        st.markdown('<div class="cta-container">', unsafe_allow_html=True)
        analyze_btn = st.button("开始 AI 分析", type="primary", use_container_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

        if analyze_btn:
            if not resume_text:
                st.warning("⚠️ 请先上传简历文件")
            elif len(resume_text) < 50:
                st.warning("⚠️ 简历内容过短，请确认上传的是文本型 PDF（非图片型）")
            elif not jd_text.strip():
                st.warning("⚠️ 请输入岗位描述（JD）")
            elif len(jd_text.strip()) < 20:
                st.warning("⚠️ 岗位描述过短，请补充完整的 JD 信息")
            else:
                st.session_state.analyzing = True
                st.session_state.result = None
                st.rerun()

        if st.session_state.get("analyzing"):
            st.markdown(
                '<div style="text-align:center;margin:24px 0;">'
                '<div class="skeleton-ring" style="width:80px;height:80px;"></div>'
                '<p style="color:#94a3b8;font-size:14px;margin-top:8px;">AI 正在分析您的简历...</p>'
                '<div class="skeleton-card"><div class="skeleton-row"></div><div class="skeleton-row short"></div></div>'
                '<div style="display:flex;gap:12px;margin-bottom:14px;">'
                '<div class="skeleton-card" style="flex:1;">'
                '<div class="skeleton-row short"></div><div class="skeleton-tag"></div><div class="skeleton-tag"></div>'
                '</div>'
                '<div class="skeleton-card" style="flex:1;">'
                '<div class="skeleton-row short"></div><div class="skeleton-tag"></div><div class="skeleton-tag"></div>'
                '</div></div>'
                '<div class="skeleton-card"><div class="skeleton-row"></div><div class="skeleton-row short"></div><div class="skeleton-row" style="width:40%"></div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            try:
                from core.analyzer import run_analysis
                from core.llm import LLMError

                result = run_with_usage_check(
                    st.session_state.user_id, run_analysis, resume_text, jd_text
                )
                if result is not None:
                    from database import create_analysis_record
                    create_analysis_record(
                        user_id=st.session_state.user_id,
                        resume_name=st.session_state.get("resume_filename", ""),
                        target_position="",
                        match_score=result.match_score,
                        analysis_summary=result.match_summary,
                    )
                    from core.llm import pop_token_usage
                    from token_tracker import save_analysis_token_batch
                    token_data = pop_token_usage()
                    if token_data:
                        save_analysis_token_batch(st.session_state.user_id, token_data)
                    st.session_state.result = result
                    st.session_state.feedback_given = False
                st.session_state.analyzing = False
                st.rerun()
            except LLMError as e:
                st.session_state.analyzing = False
                st.error(str(e))
            except ValueError as e:
                st.session_state.analyzing = False
                st.error(f"⚠️ 分析失败: {e}")
            except Exception:
                st.session_state.analyzing = False
                st.error("⚠️ AI 服务暂时不可用，请稍后重试")

        result = st.session_state.result
        if result is not None:
            render_result_dashboard(result)
            render_feedback()
