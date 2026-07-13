import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.analyzer import _extract_json, _load_prompt
from core.parser import extract_text
from models import (
    AnalysisResult,
    Education,
    JDData,
    OptimizationSuggestion,
    ResumeData,
    SkillGap,
    WorkExperience,
)


class TestModels:
    def test_resume_data_empty(self):
        r = ResumeData()
        assert r.name == ""
        assert r.skills == []
        assert r.work_experience == []
        print("[PASS] ResumeData empty default")

    def test_resume_data_full(self):
        r = ResumeData(
            name="张三",
            email="zhang@test.com",
            phone="13800138000",
            summary="Python工程师",
            work_experience=[
                WorkExperience(
                    company="ABC科技",
                    position="高级工程师",
                    start_date="2020-01",
                    end_date="2023-06",
                    responsibilities=["后端开发", "系统设计"],
                )
            ],
            education=[
                Education(
                    school="清华大学",
                    degree="本科",
                    major="计算机科学",
                    start_date="2016",
                    end_date="2020",
                )
            ],
            skills=["Python", "Java", "Docker"],
            certifications=["AWS认证"],
            languages=["中文", "英文"],
        )
        assert r.name == "张三"
        assert len(r.skills) == 3
        assert len(r.work_experience) == 1
        assert r.work_experience[0].company == "ABC科技"
        assert len(r.education) == 1
        assert r.education[0].school == "清华大学"
        print("[PASS] ResumeData full instantiation")

    def test_jd_data_empty(self):
        jd = JDData()
        assert jd.job_title == ""
        assert jd.required_skills == []
        assert jd.keywords == []
        print("[PASS] JDData empty default")

    def test_jd_data_full(self):
        jd = JDData(
            job_title="高级Python开发",
            department="技术部",
            location="北京",
            required_skills=["Python", "Django", "MySQL"],
            preferred_skills=["Docker", "AWS"],
            experience_years="3-5年",
            education_requirement="本科及以上",
            responsibilities=["负责后端开发", "系统架构设计"],
            keywords=["Python", "Django", "微服务"],
        )
        assert jd.job_title == "高级Python开发"
        assert len(jd.required_skills) == 3
        assert jd.experience_years == "3-5年"
        print("[PASS] JDData full instantiation")

    def test_analysis_result_empty(self):
        a = AnalysisResult()
        assert a.match_score == 0
        assert a.matched_skills == []
        assert a.optimization_suggestions == []
        print("[PASS] AnalysisResult empty default")

    def test_analysis_result_full(self):
        a = AnalysisResult(
            match_score=75,
            match_summary="整体匹配度较好",
            matched_skills=["Python", "Django"],
            missing_skills=["Docker", "AWS"],
            skill_gaps=[
                SkillGap(
                    skill="Docker",
                    importance="high",
                    suggestion="建议学习Docker基础并通过项目实践",
                )
            ],
            experience_gap="经验3年，要求3-5年，略有不足",
            optimization_suggestions=[
                OptimizationSuggestion(
                    section="技能部分",
                    original="Python",
                    improved="Python (精通Django/Flask框架)",
                    reason="突出框架能力",
                )
            ],
            keyword_recommendations=["微服务", "高并发"],
            overall_advice="建议补充Docker和AWS经验",
        )
        assert a.match_score == 75
        assert len(a.skill_gaps) == 1
        assert a.skill_gaps[0].importance == "high"
        assert len(a.optimization_suggestions) == 1
        print("[PASS] AnalysisResult full instantiation")

    def test_from_json_dict(self):
        json_str = '{"name":"李四","skills":["Go","Rust"]}'
        r = ResumeData(**json.loads(json_str))
        assert r.name == "李四"
        assert r.skills == ["Go", "Rust"]
        assert r.work_experience == []
        print("[PASS] ResumeData from JSON dict")


class TestParser:
    def test_file_not_found(self):
        try:
            extract_text("nonexistent_file.pdf")
            assert False, "Should raise"
        except FileNotFoundError:
            print("[PASS] FileNotFoundError on missing file")

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test")
            tmp = f.name
        try:
            try:
                extract_text(tmp)
                assert False, "Should raise"
            except ValueError as e:
                assert "不支持" in str(e)
            print("[PASS] Unsupported format raises ValueError")
        finally:
            os.unlink(tmp)

    def test_pdf_extraction(self):
        test_pdf = Path(__file__).resolve().parent / "test_resume.pdf"
        if not test_pdf.exists():
            print("[SKIP] test_resume.pdf not found")
            return
        text = extract_text(str(test_pdf))
        assert len(text) > 0
        print(f"[PASS] PDF extraction: {len(text)} chars")

    def test_docx_extraction(self):
        test_docx = Path(__file__).resolve().parent / "test_resume.docx"
        if not test_docx.exists():
            print("[SKIP] test_resume.docx not found")
            return
        text = extract_text(str(test_docx))
        assert len(text) > 0
        print(f"[PASS] DOCX extraction: {len(text)} chars")


class TestAnalyzer:
    def test_extract_json_direct(self):
        data = _extract_json('{"score": 80}')
        assert data["score"] == 80
        print("[PASS] _extract_json direct JSON")

    def test_extract_json_with_noise(self):
        data = _extract_json('这是分析结果：\n```json\n{"score": 90}\n```\n希望对你有帮助')
        assert data["score"] == 90
        print("[PASS] _extract_json with markdown noise")

    def test_extract_json_nested(self):
        data = _extract_json('{"skills": ["a", "b"], "info": {"x": 1}}')
        assert data["skills"] == ["a", "b"]
        assert data["info"]["x"] == 1
        print("[PASS] _extract_json nested object")

    def test_extract_json_failure(self):
        try:
            _extract_json("这不是JSON")
            assert False, "Should raise"
        except ValueError as e:
            assert "无法从LLM返回中解析JSON" in str(e)
        print("[PASS] _extract_json failure raises ValueError")

    def test_load_prompt(self):
        prompt = _load_prompt("resume", resume_text="TEST")
        assert "TEST" in prompt
        assert "{resume_text}" not in prompt
        print("[PASS] _load_prompt with substitution")


if __name__ == "__main__":
    print("=== Test Models ===")
    tm = TestModels()
    tm.test_resume_data_empty()
    tm.test_resume_data_full()
    tm.test_jd_data_empty()
    tm.test_jd_data_full()
    tm.test_analysis_result_empty()
    tm.test_analysis_result_full()
    tm.test_from_json_dict()

    print("\n=== Test Parser ===")
    tp = TestParser()
    tp.test_file_not_found()
    tp.test_unsupported_format()
    tp.test_pdf_extraction()
    tp.test_docx_extraction()

    print("\n=== Test Analyzer ===")
    ta = TestAnalyzer()
    ta.test_extract_json_direct()
    ta.test_extract_json_with_noise()
    ta.test_extract_json_nested()
    ta.test_extract_json_failure()
    ta.test_load_prompt()

    print("\nAll tests passed.")
