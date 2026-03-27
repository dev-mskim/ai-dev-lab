# 트러블슈팅 (에러 해결 모음)

> 발생한 에러와 해결 방법을 기록합니다.
> 같은 문제가 반복될 때 참고하세요.

---

## 환경 설정

### pip 실행 시 `No module named 'pip._vendor.rich.markup'` 오류

**증상**
```
ModuleNotFoundError: No module named 'pip._vendor.rich.markup'
```

**원인**
pip 설치 파일이 손상된 상태

**해결**
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

---

### `.venv\Scripts\activate` 실행 시 PowerShell 보안 오류

**증상**
```
이 시스템에서 스크립트를 실행할 수 없으므로 ... 파일을 로드할 수 없습니다.
```

**원인**
Windows PowerShell 스크립트 실행 정책이 제한됨

**해결**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Y 입력 후 엔터
```

---

### `dotenv` 버전 확인 시 `module 'dotenv' has no attribute '__version__'` 오류

**증상**
```
[FAIL] dotenv → module 'dotenv' has no attribute '__version__'
```

**원인**
`python-dotenv` 라이브러리는 `__version__` 속성을 제공하지 않음

**해결**
버전 확인 대신 import 성공 여부만 확인:
```python
# 변경 전
__import__("dotenv").__version__

# 변경 후
__import__("dotenv") and "OK"
```

---

### Claude API 호출 시 인증 오류

**증상**
```
TypeError: "Could not resolve authentication method.
Expected either api_key or auth_token to be set."
```

**원인**
`.env` 파일 로드 시 인코딩 문제로 API 키를 읽지 못함

**해결**
`load_dotenv()` 호출 시 인코딩 명시:
```python
# 변경 전
load_dotenv()

# 변경 후
load_dotenv(encoding='utf-8')
```

---

## ChromaDB

### ChromaDB 컬렉션 재생성 시 오류

**증상**
```
ValueError: Collection already exists
```

**원인**
동일한 이름의 컬렉션이 이미 존재

**해결**
생성 전 삭제 처리:
```python
try:
    client.delete_collection("schema")
except Exception:
    pass
collection = client.create_collection("schema")
```

---

## 향후 추가 예정

에러 발생 시 아래 형식으로 추가해주세요:

```
### 에러 제목

**증상**
에러 메시지 또는 현상

**원인**
원인 설명

**해결**
해결 방법 (코드 포함)
```
