import json
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from core.analyzer import run_analysis
from core.llm import LLMError
from core.parser import extract_text

st.set_page_config(page_title="简历优化助手", page_icon="📄", layout="wide")
st.title("AI 简历优化助手")
st.markdown("上传简历 + 输入岗位JD，AI帮你分析匹配度并给出优化建议")

if "result" not in st.session_state:
    st.session_state.result = None
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

col1, col2 = st.columns(2)

with col1:
    st.subheader("上传简历")
    uploaded_file = st.file_uploader("支持 PDF / DOCX 格式", type=["pdf", "docx"])

    resume_text = ""
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        try:
            resume_text = extract_text(tmp_path)
            st.success(f"解析成功，共 {len(resume_text)} 字符")
            with st.expander("预览解析内容"):
                st.text(resume_text[:1000])
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"文件读取失败: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

with col2:
    st.subheader("输入岗位描述 (JD)")
    jd_text = st.text_area(
        "粘贴目标岗位的职位描述",
        height=200,
        placeholder="请在此粘贴岗位描述（JD）...",
    )

st.divider()

analyze_btn = st.button("开始分析", type="primary", use_container_width=True)

if analyze_btn:
    if not resume_text:
        st.warning("请先上传简历文件")
    elif len(resume_text) < 50:
        st.warning("简历内容过短，请确认上传的是文本型PDF（非图片型）")
    elif not jd_text.strip():
        st.warning("请输入岗位描述（JD）")
    elif len(jd_text.strip()) < 20:
        st.warning("岗位描述过短，请补充完整的JD信息")
    else:
        with st.spinner("AI分析中，请稍候..."):
            try:
                result = run_analysis(resume_text, jd_text)
                st.session_state.result = result
                st.session_state.feedback_given = False
                st.rerun()
            except LLMError as e:
                st.error(str(e))
            except ValueError as e:
                st.error(f"分析失败: {e}")
            except Exception as e:
                st.error("AI服务暂时不可用，请稍后重试")


def _write_feedback(fb_type: str, note: str = ""):
    entry = {"ts": datetime.now().isoformat(timespec="seconds"), "type": fb_type, "note": note}
    log_path = Path(__file__).resolve().parent / "feedback.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


result = st.session_state.result
if result is not None:
    st.divider()
    st.header("分析结果")

    score = result.match_score
    if score >= 80:
        color = "green"
        emoji = "✅"
    elif score >= 60:
        color = "orange"
        emoji = "⚠️"
    else:
        color = "red"
        emoji = "❌"

    st.markdown(f"### 匹配度: :{color}[{score}/100] {emoji}")
    st.caption(result.match_summary)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("匹配技能")
        if result.matched_skills:
            for skill in result.matched_skills:
                st.markdown(f"✅ {skill}")
        else:
            st.caption("无匹配技能")

    with col_b:
        st.subheader("缺失技能")
        if result.missing_skills:
            for skill in result.missing_skills:
                st.markdown(f"❌ {skill}")
        else:
            st.caption("无缺失技能")

    if result.skill_gaps:
        st.subheader("技能差距分析")
        for gap in result.skill_gaps:
            importance_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(gap.importance, "⚪")
            with st.expander(f"{importance_icon} {gap.skill} ({gap.importance})"):
                st.markdown(gap.suggestion)

    if result.experience_gap:
        st.subheader("经验差距")
        st.info(result.experience_gap)

    if result.optimization_suggestions:
        st.subheader("优化建议")
        for i, suggestion in enumerate(result.optimization_suggestions, 1):
            with st.expander(f"建议{i}: {suggestion.section}"):
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    st.markdown("**原文**")
                    st.caption(suggestion.original or "无")
                with cols[1]:
                    st.markdown("**改进版本**")
                    st.success(suggestion.improved or "无")
                with cols[2]:
                    st.markdown("**修改原因**")
                    st.info(suggestion.reason or "无")

    if result.keyword_recommendations:
        st.subheader("建议添加的关键词")
        st.markdown(" ".join(f"`{kw}`" for kw in result.keyword_recommendations))

    if result.overall_advice:
        st.subheader("整体建议")
        st.markdown(f"> {result.overall_advice}")

    st.divider()
    st.subheader("反馈")

    if st.session_state.feedback_given:
        st.success("感谢您的反馈！")
    else:
        fb_type = st.radio("这个分析结果对您有帮助吗？", ["👍 有帮助", "👎 没帮助"], horizontal=True)
        fb_note = st.text_area("备注（可选）", placeholder="有什么建议或想法？")
        if st.button("提交反馈", use_container_width=True):
            _write_feedback("helpful" if "有帮助" in fb_type else "not_helpful", fb_note)
            st.session_state.feedback_given = True
            st.rerun()
