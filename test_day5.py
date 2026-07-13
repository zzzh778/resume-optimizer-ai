import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import _write_feedback


def test_write_feedback():
    log_path = Path(__file__).resolve().parent / "feedback.log"
    if log_path.exists():
        log_path.unlink()

    _write_feedback("helpful", "建议精准")
    _write_feedback("not_helpful", "")

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    entry1 = json.loads(lines[0])
    assert entry1["type"] == "helpful"
    assert entry1["note"] == "建议精准"
    assert "ts" in entry1

    entry2 = json.loads(lines[1])
    assert entry2["type"] == "not_helpful"
    assert entry2["note"] == ""

    log_path.unlink()
    print("[PASS] Feedback writes JSONL correctly")


def test_feedback_log_privacy():
    log_path = Path(__file__).resolve().parent / "feedback.log"
    if log_path.exists():
        log_path.unlink()

    _write_feedback("helpful")

    content = log_path.read_text(encoding="utf-8")
    assert "resume" not in content.lower()
    assert "jd" not in content.lower()
    assert "phone" not in content.lower()
    assert "email" not in content.lower()

    log_path.unlink()
    print("[PASS] Feedback log contains no resume/jd data (privacy)")


if __name__ == "__main__":
    test_write_feedback()
    test_feedback_log_privacy()
    print("\nAll UI module tests passed.")
    print(f"\nTo launch the app: streamlit run app.py")
