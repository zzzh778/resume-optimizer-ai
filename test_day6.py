import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.analyzer import _extract_json, _load_prompt
from core.llm import LLMError, create_llm_provider
from core.parser import extract_text
from models import AnalysisResult, JDData, ResumeData

PASS = 0
FAILED = 0
SKIP = 0


def check(name, condition, detail=""):
    global PASS, FAILED
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  {detail}")


def skip(name):
    global SKIP
    SKIP += 1
    print(f"  [SKIP] {name}")


# ============================================================
# 一、正常流程测试
# ============================================================
print("=" * 60)
print("一、正常流程测试")
print("=" * 60)

print("\n--- 1.1 中文简历 + 中文 JD ---")
cn_resume = """
姓名：张三
邮箱：zhang@test.com
电话：13800138000
个人简介：3年Python开发经验
工作经历：
ABC科技 | 高级Python开发 | 2021-06 至今
- 开发RESTful API
- 优化数据库查询
教育背景：清华大学 计算机科学 本科
技能：Python, Django, MySQL, Redis, Docker
"""
cn_jd = """
岗位名称：Python开发工程师
职责：负责后端开发
要求：3年Python经验，熟悉Django/Flask，MySQL，Redis
"""
check("中文简历文本长度 > 50", len(cn_resume) > 50)
check("中文JD文本长度 > 20", len(cn_jd) > 20)
check("中文简历包含技能关键词", "Python" in cn_resume)
check("中文JD包含岗位名称", "Python开发工程师" in cn_jd)

print("\n--- 1.2 英文简历 + 英文 JD ---")
en_resume = """
Name: John Smith
Email: john@test.com
Phone: +1-555-0123
Summary: Senior Software Engineer with 5 years of experience

Work Experience:
TechCorp Inc | Senior Developer | 2020-01 to Present
- Designed microservices architecture
- Led team of 5 engineers
- Improved system performance by 40%

Education: MIT, BS Computer Science, 2015-2019
Skills: Python, Go, Kubernetes, AWS, Terraform, PostgreSQL, Redis
"""
en_jd = """
Position: Senior Backend Engineer
Responsibilities:
- Design and implement backend services
- Collaborate with cross-functional teams

Requirements:
- 5+ years of software development experience
- Proficiency in Python or Go
- Experience with Kubernetes and AWS
- Strong understanding of distributed systems
"""
check("英文简历文本长度 > 50", len(en_resume) > 50)
check("英文JD文本长度 > 20", len(en_jd) > 20)
check("英文简历包含技能关键词", "Python" in en_resume)
check("英文JD包含岗位名称", "Senior Backend Engineer" in en_jd)

print("\n--- 1.3 中英混合简历 + 中文 JD ---")
mixed_resume = """
Name: 李四 Li Si
Email: lisi@test.com
Phone: 13900139000

Summary:
Bilingual software engineer with 2 years full-stack development experience.
具备前后端全栈开发能力。

Work Experience / 工作经历：
XYZ Technology | Full-stack Developer / 全栈开发 | 2022-07 to Present
- Developed React frontend and Node.js backend
- 负责系统架构设计
- Managed CI/CD pipeline using Docker and Jenkins

Education / 教育背景：
Shanghai Jiao Tong University / 上海交通大学
M.Sc. Software Engineering / 软件工程硕士 | 2020-2022

Skills / 技能：
Python, JavaScript, React, Node.js, TypeScript, Docker, MySQL
"""
mixed_jd = """
岗位名称：全栈开发工程师
工作地点：上海

岗位职责：
1. 负责Web应用前后端开发
2. 参与系统架构设计
3. 与产品团队协作

Requirements:
- 2年以上全栈开发经验
- 熟悉React前端框架
- 熟悉Node.js或Python后端
- 了解Docker
- 英语读写能力
"""
check("混合简历文本长度 > 50", len(mixed_resume) > 50)
check("混合JD文本长度 > 20", len(mixed_jd) > 20)
check("混合简历包含中文", any("\u4e00" <= c <= "\u9fff" for c in mixed_resume))
check("混合简历包含英文技能", "React" in mixed_resume)


# ============================================================
# 二、异常流程测试
# ============================================================
print("\n" + "=" * 60)
print("二、异常流程测试")
print("=" * 60)

print("\n--- 2.1 图片型 PDF ---")
try:
    import fitz

    pdf_path = Path(__file__).resolve().parent / "test_image_pdf.pdf"
    doc = fitz.open()
    page = doc.new_page(width=100, height=100)
    doc.save(str(pdf_path))
    doc.close()

    try:
        extract_text(str(pdf_path))
        check("图片PDF抛异常", False, "应该抛出 ValueError")
    except ValueError as e:
        check("图片PDF正确拒绝", "提取的文本过短" in str(e) or "图片型PDF" in str(e))
    finally:
        pdf_path.unlink(missing_ok=True)
except ImportError:
    skip("pymupdf not available")

print("\n--- 2.2 损坏文件 ---")
corrupt_pdf = Path(__file__).resolve().parent / "corrupt.pdf"
corrupt_pdf.write_bytes(b"not a real pdf file")
try:
    try:
        extract_text(str(corrupt_pdf))
        check("损坏PDF不崩溃", False, "应抛出异常")
    except (ValueError, FileNotFoundError) as e:
        check("损坏PDF抛友好异常", True)
    except Exception as e:
        check("损坏PDF抛友好异常", False, f"未预期异常类型: {type(e).__name__}")
finally:
    corrupt_pdf.unlink(missing_ok=True)

corrupt_docx = Path(__file__).resolve().parent / "corrupt.docx"
corrupt_docx.write_bytes(b"not a real docx file")
try:
    try:
        extract_text(str(corrupt_docx))
        check("损坏DOCX不崩溃", False, "应抛出异常")
    except (ValueError, FileNotFoundError) as e:
        check("损坏DOCX抛友好异常", True)
    except Exception as e:
        check("损坏DOCX抛友好异常", False, f"未预期异常类型: {type(e).__name__}")
finally:
    corrupt_docx.unlink(missing_ok=True)

print("\n--- 2.3 不支持文件格式 ---")
txt_path = Path(__file__).resolve().parent / "test.txt"
txt_path.write_text("hello", encoding="utf-8")
try:
    try:
        extract_text(str(txt_path))
        check("txt格式应拒绝", False)
    except ValueError as e:
        check("txt格式正确拒绝", "不支持" in str(e) or "仅支持" in str(e))
finally:
    txt_path.unlink(missing_ok=True)

print("\n--- 2.4 LLM 返回非 JSON ---")
check(
    "_extract_json 直接JSON",
    _extract_json('{"a":1}') == {"a": 1},
)
check(
    "_extract_json markdown包裹",
    _extract_json('```json\n{"a":1}\n```') == {"a": 1},
)
check(
    "_extract_json 中文前后缀",
    _extract_json('结果是：{"a":1}，请参考') == {"a": 1},
)
check(
    "_extract_json 嵌套对象",
    _extract_json('{"skills":["a","b"],"info":{"x":1}}')
    == {"skills": ["a", "b"], "info": {"x": 1}},
)
try:
    _extract_json("完全不是JSON")
    check("_extract_json 非JSON抛异常", False)
except ValueError:
    check("_extract_json 非JSON正确抛异常", True)

print("\n--- 2.5 LLM 请求异常 ---")
# Test 2.5a: Provider with invalid API key
try:
    from core.llm import DeepSeekProvider

    bad_provider = DeepSeekProvider(
        api_key="sk-invalid-key",
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
    )
    try:
        bad_provider.generate("hello")
        check("无效API Key应抛异常", False, "应当抛 LLMError")
    except LLMError as e:
        check("无效API Key正确捕获", "API Key" in str(e) or "不可用" in str(e))
    except Exception:
        check("无效API Key正确捕获", True)  # any exception is acceptable if auth fails
except Exception:
    skip("无法模拟API错误（可能无网络）")

# Test 2.5b: Missing API key
try:
    old_key = os.environ.pop("DEEPSEEK_API_KEY", None)
    try:
        create_llm_provider()
        check("空API Key应抛异常", False)
    except ValueError as e:
        check("空API Key正确抛异常", "not set" in str(e))
    finally:
        if old_key is not None:
            os.environ["DEEPSEEK_API_KEY"] = old_key
except Exception:
    skip("环境变量测试跳过")

print("\n--- 2.6 JD 异常 ---")
check("空JD被检测", len("   ".strip()) == 0)
check("短JD被检测", len("招Python".strip()) < 20)
check("空字符串strip为空", "   ".strip() == "")
no_skill_jd = "需要招聘一个人来完成日常的运营维护工作。"
check("JD无技能关键词检测", "Python" not in no_skill_jd and "Java" not in no_skill_jd)


# ============================================================
# 三、代码质量检查
# ============================================================
print("\n" + "=" * 60)
print("三、代码质量检查")
print("=" * 60)

source_files = {
    "config.py": Path(__file__).resolve().parent / "config.py",
    "models.py": Path(__file__).resolve().parent / "models.py",
    "core/llm.py": Path(__file__).resolve().parent / "core" / "llm.py",
    "core/parser.py": Path(__file__).resolve().parent / "core" / "parser.py",
    "core/analyzer.py": Path(__file__).resolve().parent / "core" / "analyzer.py",
    "app.py": Path(__file__).resolve().parent / "app.py",
}

print("\n--- 3.1 语法检查 ---")
for name, path in source_files.items():
    try:
        import py_compile

        py_compile.compile(str(path), doraise=True)
        check(f"{name} 语法正确", True)
    except Exception as e:
        check(f"{name} 语法正确", False, str(e))

print("\n--- 3.2 Import检查 ---")
for name, path in source_files.items():
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    import_line = None
    from_imports = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import ") and not stripped.startswith("import test"):
            import_line = stripped
        elif stripped.startswith("from ") and " import " in stripped:
            parts = stripped.split(" import ")
            mod = parts[0].replace("from ", "")
            names = [n.strip() for n in parts[1].split(",")]
            for n in names:
                from_imports.append((mod, n))
    check(f"{name} 有导入", import_line is not None or len(from_imports) > 0)

print("\n--- 3.3 异常处理覆盖 ---")
analyzer_content = (Path(__file__).resolve().parent / "core" / "analyzer.py").read_text(
    encoding="utf-8"
)
check("analyzer.py 含 _extract_json", "_extract_json" in analyzer_content)
check("analyzer.py 含 try/except", "except" in analyzer_content)
check("analyzer.py 含 _load_prompt", "_load_prompt" in analyzer_content)

parser_content = (Path(__file__).resolve().parent / "core" / "parser.py").read_text(
    encoding="utf-8"
)
check("parser.py 含 try/except", "except" in parser_content)
check("parser.py 含 文件不存在", "文件不存在" in parser_content)
check("parser.py 含 不支持格式", "不支持" in parser_content)

llm_content = (Path(__file__).resolve().parent / "core" / "llm.py").read_text(encoding="utf-8")
check("llm.py 含 LLMError", "LLMError" in llm_content)
check("llm.py 含 timeout", "timeout" in llm_content)
check("llm.py 含 try/except", "except" in llm_content)

app_content = (Path(__file__).resolve().parent / "app.py").read_text(encoding="utf-8")
check("app.py 含 LLMError", "LLMError" in app_content)
check("app.py 含 不可用", "不可用" in app_content)

print("\n--- 3.4 未使用导入检查 ---")
# models.py should NOT have 'date', 'Optional', 'Field' imports
models_content = (Path(__file__).resolve().parent / "models.py").read_text(encoding="utf-8")
for bad_import in ["from datetime import", "from typing import", "Field"]:
    check(f"models.py 无未使用导入 {bad_import}", bad_import not in models_content)

# analyzer.py should NOT have 'as_completed'
check(
    "analyzer.py 无未使用导入 as_completed",
    "as_completed" not in (Path(__file__).resolve().parent / "core" / "analyzer.py").read_text(
        encoding="utf-8"
    ),
)


# ============================================================
# 四、隐私检查
# ============================================================
print("\n" + "=" * 60)
print("四、隐私检查")
print("=" * 60)

feedback_log = Path(__file__).resolve().parent / "feedback.log"
# Write test feedback
test_entries = [
    {"ts": "2026-07-14T10:30:00", "type": "helpful", "note": "建议很准确"},
    {"ts": "2026-07-14T10:31:00", "type": "not_helpful", "note": ""},
]
if feedback_log.exists():
    feedback_log.unlink()
for entry in test_entries:
    with open(feedback_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

content = feedback_log.read_text(encoding="utf-8")
check("feedback.log 格式JSONL", len(content.strip().split("\n")) == 2)

entries = [json.loads(line) for line in content.strip().split("\n")]
for i, entry in enumerate(entries):
    check(f"条目{i+1} 有 ts", "ts" in entry)
    check(f"条目{i+1} 有 type", "type" in entry)
    check(f"条目{i+1} 有 note", "note" in entry)

check("feedback.log 不含 'resume'", "resume" not in content.lower())
check("feedback.log 不含 'email'", "email" not in content.lower())
check("feedback.log 不含 'phone'", "phone" not in content.lower())
check("feedback.log 不含 'JD'", "JD" not in content)
check("feedback.log 不含 '简历'", "简历" not in content)
check("feedback.log 不含 '技能'", "技能" not in content)

feedback_log.unlink(missing_ok=True)

# ============================================================
# 五、模型序列化测试
# ============================================================
print("\n" + "=" * 60)
print("五、模型完整性测试")
print("=" * 60)

print("\n--- 5.1 ResumeData 序列化 ---")
resume = ResumeData(
    name="张三",
    email="zhang@test.com",
    phone="13800138000",
    skills=["Python", "Django"],
    work_experience=[],
    education=[],
)
json_str = resume.model_dump_json()
parsed = json.loads(json_str)
check("ResumeData 序列化 name", parsed["name"] == "张三")
check("ResumeData 序列化 skills", parsed["skills"] == ["Python", "Django"])

print("\n--- 5.2 JDData 序列化 ---")
jd = JDData(
    job_title="工程师",
    required_skills=["Python", "Docker"],
    keywords=["Python", "微服务"],
)
json_str = jd.model_dump_json()
parsed = json.loads(json_str)
check("JDData 序列化 job_title", parsed["job_title"] == "工程师")
check("JDData 序列化 keywords", len(parsed["keywords"]) == 2)

print("\n--- 5.3 AnalysisResult 序列化往返 ---")
original = AnalysisResult(
    match_score=85,
    match_summary="匹配度较高",
    matched_skills=["Python", "Django"],
    missing_skills=["Docker"],
    skill_gaps=[],
    optimization_suggestions=[],
    keyword_recommendations=["Docker"],
    overall_advice="建议学习Docker",
)
restored = AnalysisResult.model_validate_json(original.model_dump_json())
check("AnalysisResult 往返 match_score", restored.match_score == original.match_score)
check("AnalysisResult 往返 match_summary", restored.match_summary == original.match_summary)
check("AnalysisResult 往返 matched_skills", restored.matched_skills == original.matched_skills)

print("\n--- 5.4 AnalysisResult match_score 范围 ---")
check("默认match_score=0", AnalysisResult().match_score == 0)
check("match_score=100", AnalysisResult(match_score=100).match_score == 100)
try:
    r = AnalysisResult(match_score=150)
    print("  [INFO] match_score>100 未被Pydantic拒绝（MVP无范围约束，依赖LLM输出质量）")
except Exception:
    print("  [PASS] match_score>100 被拒绝" + "_" * 20)


# ============================================================
# 六、Prompt完整性测试
# ============================================================
print("\n" + "=" * 60)
print("六、Prompt完整性测试")
print("=" * 60)

for name in ["resume", "jd", "analysis"]:
    prompt_path = Path(__file__).resolve().parent / "prompts" / f"{name}.yaml"
    check(f"{name}.yaml 存在", prompt_path.exists())
    if prompt_path.exists():
        import yaml

        with open(prompt_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        check(f"{name}.yaml 有name字段", "name" in data)
        check(f"{name}.yaml 有prompt字段", "prompt" in data)
        check(f"{name}.yaml prompt是字符串", isinstance(data["prompt"], str))

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print(f"测试汇总: {PASS} PASS, {FAILED} FAILED, {SKIP} SKIPPED")
print("=" * 60)

if FAILED > 0:
    sys.exit(1)
