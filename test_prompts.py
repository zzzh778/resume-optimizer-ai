import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.analyzer import _load_prompt


def test_load_resume():
    prompt = _load_prompt("resume", resume_text="张三\n工程师\nPython, Java")
    assert "张三" in prompt, "Should contain the substituted text"
    assert "resume_text" not in prompt, "Placeholder should be replaced"
    print("[PASS] resume.yaml loaded and formatted")


def test_load_jd():
    prompt = _load_prompt("jd", jd_text="招聘Python开发\n要求3年经验")
    assert "招聘Python开发" in prompt, "Should contain the substituted text"
    assert "jd_text" not in prompt, "Placeholder should be replaced"
    print("[PASS] jd.yaml loaded and formatted")


def test_load_analysis():
    prompt = _load_prompt("analysis", resume_data="{}", jd_data="{}")
    assert "{}" in prompt, "Should contain the substituted JSON data"
    assert "resume_data" not in prompt, "Placeholder should be replaced"
    assert "jd_data" not in prompt, "Placeholder should be replaced"
    print("[PASS] analysis.yaml loaded and formatted")


def test_missing_file():
    try:
        _load_prompt("nonexistent", text="test")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError:
        print("[PASS] Missing file raises FileNotFoundError")


def test_yaml_structure():
    prompts_dir = Path(__file__).resolve().parent / "prompts"
    for name in ["resume", "jd", "analysis"]:
        path = prompts_dir / f"{name}.yaml"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "name" in data, f"{name}.yaml missing 'name' key"
        assert "prompt" in data, f"{name}.yaml missing 'prompt' key"
        assert isinstance(data["prompt"], str), f"{name}.yaml prompt is not a string"
        print(f"[PASS] {name}.yaml structure valid")


if __name__ == "__main__":
    test_yaml_structure()
    test_load_resume()
    test_load_jd()
    test_load_analysis()
    test_missing_file()
    print("\nAll tests passed.")
