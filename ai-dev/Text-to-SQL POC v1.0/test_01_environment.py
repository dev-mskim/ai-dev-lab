"""
1단계 테스트: 환경 설정 점검
실행: python test_01_environment.py
점검: 패키지 설치, .env 파일, Claude API 연결
"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0


def check(label, fn):
    global PASS, FAIL
    try:
        result = fn()
        msg = f" → {result}" if isinstance(result, str) else ""
        print(f"  [OK] {label}{msg}")
        PASS += 1
    except Exception as e:
        print(f"  [FAIL] {label}")
        print(f"         └ {e}")
        FAIL += 1


print("=" * 50)
print("  1단계 테스트: 환경 설정 점검")
print("=" * 50)

# ── 패키지 설치 확인 ──────────────────────────
print("\n[패키지 설치 확인]")

check("Python 버전",
      lambda: f"Python {sys.version.split()[0]}")

check("anthropic",
      lambda: __import__("anthropic").__version__)

check("streamlit",
      lambda: __import__("streamlit").__version__)

check("chromadb",
      lambda: __import__("chromadb").__version__)

check("sqlalchemy",
      lambda: __import__("sqlalchemy").__version__)

check("sentence_transformers",
      lambda: __import__("sentence_transformers").__version__)

check("python-dotenv",
      lambda: __import__("dotenv") and "OK")

# ── .env 파일 및 API 키 확인 ──────────────────
print("\n[API 키 설정 확인]")

from dotenv import load_dotenv
load_dotenv(encoding="utf-8")

check(".env 파일 로드",
      lambda: "OK")

api_key = os.getenv("ANTHROPIC_API_KEY", "")

check("API 키 존재 및 형식 확인 (sk-ant- 로 시작)",
      lambda: "OK" if api_key.startswith("sk-ant-") else (_ for _ in ()).throw(Exception("키 없음 또는 형식 오류. .env 파일 확인 필요")))

# ── Claude API 실제 호출 ──────────────────────
print("\n[Claude API 연결 확인]")

check("Claude API 실제 호출", lambda: (
    __import__("anthropic").Anthropic(api_key=api_key)
    .messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say OK"}]
    ).content[0].text.strip()
))

# ── 결과 ──────────────────────────────────────
total = PASS + FAIL
print(f"\n{'=' * 50}")
print(f"  결과: {PASS}/{total} 항목 통과")
if FAIL == 0:
    print("  1단계 환경 설정 완료! 2단계 진행 가능합니다.")
else:
    print("  [FAIL] 항목을 확인하세요. TROUBLESHOOTING.md 참고")
print("=" * 50)
