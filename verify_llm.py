import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.llm import create_llm_provider


def main():
    provider = create_llm_provider()
    print(f"Provider type: {type(provider).__name__}")

    response = provider.generate("回复OK")
    print(f"Response: {response}")

    if "OK" in response:
        print("[PASS] Verification successful")
    else:
        print(f"[WARN] Expected 'OK' in response, got: {response}")


if __name__ == "__main__":
    main()
