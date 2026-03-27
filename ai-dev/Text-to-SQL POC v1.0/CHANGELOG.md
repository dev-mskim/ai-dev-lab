# 변경 이력 (CHANGELOG)

> 형식: [날짜] - 변경 내용
> 버전 규칙: v주요기능.기능추가.버그수정

---

## [v0.3.0] - 2026-03-26

### Added
- `src/schema_loader.py` 생성
  - ChromaDB Vector DB 연동
  - 테이블 스키마 4개 + 관계 정보 저장
  - 자연어 기반 스키마 검색 기능
  - 다국어 임베딩 모델 적용 (paraphrase-multilingual-MiniLM-L12-v2)

---

## [v0.2.0] - 2026-03-26

### Added
- `src/db_setup.py` 생성
  - SQLite 샘플 DB 생성
  - 샘플 테이블 4개 생성 (CUSTOMERS, PRODUCTS, ORDERS, ORDER_ITEMS)
  - 샘플 데이터 삽입 (고객 8명, 상품 8개, 주문 12건, 주문상세 16건)
  - 중복 실행 방지 로직 추가

---

## [v0.1.0] - 2026-03-26

### Added
- 프로젝트 초기 환경 구성
  - Python 3.10 가상환경 (.venv) 생성
  - 필수 패키지 설치 (anthropic, streamlit, chromadb, sqlalchemy 등)
  - 프로젝트 폴더 구조 생성 (src/, data/, vectordb/)
  - `.env` 파일 구성 및 Claude API 키 연동
  - `GUIDE.md`, `PROGRESS.md` 문서 생성
  - `test_setup.py` 환경 점검 스크립트 생성

---

## 향후 예정

| 버전 | 내용 |
|------|------|
| v0.4.0 | sql_generator.py - 자연어→SQL 핵심 로직 |
| v0.5.0 | app.py - Streamlit 웹 UI |
| v0.6.0 | 통합 테스트 및 버그 수정 |
| v1.0.0 | Oracle ERP 연동 완료 |
