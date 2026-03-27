"""
직접 질문 테스트용 파일
sql_generator.py 를 수정하지 않고 여기서 질문을 바꿔서 실행하세요

실행: python run_query.py
"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

from src.sql_generator import ask

# ─────────────────────────────────────────
# 여기에 원하는 질문을 입력하세요
# ─────────────────────────────────────────
questions = [
    "홍길동의 거주지는 어디인가요?",
]
# ─────────────────────────────────────────

for q in questions:
    print("\n" + "=" * 50)
    print(f"질문: {q}")
    print("=" * 50)
    try:
        res = ask(q)
        print(f"[SQL]\n{res['sql']}\n")
        print(f"[결과] {len(res['result'])}건")
        print(f"[답변] {res['answer']}")
    except Exception as e:
        print(f"[오류] {e}")
