"""
전체 단계 통합 테스트 (단계별 테스트 파일을 순서대로 실행)
실행: python test_all.py

단계별 개별 실행:
  python test_01_environment.py   1단계: 환경 설정
  python test_02_database.py      2단계: 샘플 DB
  python test_03_vectordb.py      3단계: Vector DB
"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

python = sys.executable

tests = [
    ("1단계: 환경 설정",  "test_01_environment.py"),
    ("2단계: 샘플 DB",    "test_02_database.py"),
    ("3단계: Vector DB",  "test_03_vectordb.py"),
    ("4단계: 핵심 로직",  "test_04_sql_generator.py"),
]

print("=" * 50)
print("  전체 통합 테스트 시작")
print("=" * 50)

total_pass = 0
total_fail = 0

for title, filename in tests:
    print(f"\n>>> {title} ({filename})")
    print("-" * 50)

    result = subprocess.run(
        [python, filename],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output = result.stdout
    print(output)

    passed = output.count("[OK]")
    failed = output.count("[FAIL]")
    total_pass += passed
    total_fail += failed

print("=" * 50)
print(f"  최종 결과: {total_pass}/{total_pass + total_fail} 항목 통과")
if total_fail == 0:
    print("  모든 테스트 통과! 다음 단계 진행 가능합니다.")
else:
    print(f"  {total_fail}개 항목 실패. 위 [FAIL] 항목을 확인하세요.")
print("=" * 50)
