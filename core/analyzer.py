import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from core.llm import LLMError, create_llm_provider
from models import AnalysisResult, JDData, ResumeData

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str, **kwargs) -> str:
    path = _PROMPTS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "prompt" not in data:
        raise ValueError(f"Invalid prompt file format: {path}")
    return data["prompt"].format(**kwargs)


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError(f"无法从LLM返回中解析JSON:\n{text[:500]}")


def parse_resume(resume_text: str) -> ResumeData:
    provider = create_llm_provider()
    prompt = _load_prompt("resume", resume_text=resume_text)
    response = provider.generate(prompt)
    data = _extract_json(response)
    return ResumeData(**data)


def parse_jd(jd_text: str) -> JDData:
    provider = create_llm_provider()
    prompt = _load_prompt("jd", jd_text=jd_text)
    response = provider.generate(prompt)
    data = _extract_json(response)
    return JDData(**data)


def run_analysis(resume_text: str, jd_text: str) -> AnalysisResult:
    with ThreadPoolExecutor(max_workers=2) as executor:
        resume_future = executor.submit(parse_resume, resume_text)
        jd_future = executor.submit(parse_jd, jd_text)
        resume_data = resume_future.result()
        jd_data = jd_future.result()

    resume_json = json.dumps(resume_data.model_dump(), ensure_ascii=False, indent=2)
    jd_json = json.dumps(jd_data.model_dump(), ensure_ascii=False, indent=2)

    provider = create_llm_provider()
    prompt = _load_prompt("analysis", resume_data=resume_json, jd_data=jd_json)
    response = provider.generate(prompt)
    data = _extract_json(response)
    return AnalysisResult(**data)
