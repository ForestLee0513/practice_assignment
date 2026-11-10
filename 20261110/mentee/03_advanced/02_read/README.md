# 실습 02 · JSON 목록·상세 조회

수강생용입니다. BEGIN/END 사이 TODO를 구현합니다. 미완성 요청은 NotImplementedError 또는 미등록 Route로 실패할 수 있습니다.

**PPT 12–19쪽 / 35분 / 심화**

## 작업 순서

1. 이전 교시 서버를 Ctrl+C로 종료합니다.
2. 아래 교시 폴더를 현재 작업 폴더로 사용합니다. 이 폴더가 프로젝트 루트입니다.
3. 요구된 TODO를 구현하고 서버를 실행합니다. 앞 교시가 미완성이어도 이 폴더의 선행 기능은 제공되어 있습니다.
4. /docs에서 아래 예상 결과와 실제 파일을 대조합니다.

```powershell
# 수강생용 폴더에서 시작한 경우
cd ".\03_심화\02_read"
python -m uvicorn main:app --reload
```

브라우저: `http://127.0.0.1:8000/docs` · 첫 확인: `http://127.0.0.1:8000/health`

활성화를 하지 않았다면 현재 교시 폴더에서 다음처럼 같은 가상환경 Python을 직접 사용합니다.

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

심화의 app.main:app 실행에서도 app 폴더 안으로 cd하지 않습니다. 새로운 교시로 이동할 때 이전 서버는 반드시 종료합니다.

## 완성할 부분

| TODO ID | 파일 | 완료 요구사항 |
|---|---|---|
| H02-03 | `main.py` | 조회 결과가 None이면 HTTP의 404로 변환하세요. |
| H02-01 | `logic.py` | 읽고 필터링한 entries 목록을 반환하세요. 저장 함수를 호출하지 마세요. |
| H02-02 | `logic.py` | 항목의 id와 knowledge_id가 일치하면 그 dict를 반환하세요. 없으면 아래 None으로 진행하세요. |
| H02-04 | `tests/test_api.py` | 정상·404·422 GET 이후 파일 바이트가 before와 같은지 검사하세요. |

## 요청·응답·저장 확인

1. GET /health → 200, {"status":"ok"}
2. GET /docs → 200인 문서 화면. 실행 결과는 Server response에서 읽습니다.
3. 초기 파일: next_id=4, entries 3건 (ID 1·2·3). 이 폴더에서 이미 변경했다면 실제 상태를 먼저 확인합니다.
4. GET /api/knowledge → 200, entries 배열만 반환. GET /api/knowledge/2 → title=서버 실행.
5. GET /api/knowledge/9999 → 404, detail=Knowledge not found. GET /api/knowledge/foo → 422. GET 전후 파일은 변하지 않습니다.
6. category=api → 초기 ID 2·3, category=setup → 초기 ID 1, category=unknown → 200과 []. 생략은 전체입니다.


## 자동 검사 (선택한 심화 수준의 과제)

가상환경에 requirements-test.txt의 패키지를 설치한 뒤, 현재 프로젝트 루트에서 실행합니다.

```powershell
python -m pytest -q tests/test_api.py
```

conftest.py가 각 테스트마다 임시 파일을 새로 만들고 DATA만 바꿉니다. 실제 data/knowledge.json을 건드리지 않습니다.
정답이 미완성이면 테스트가 실패하는 것이 정상입니다. 테스트를 지우거나 assert를 pass로 바꾸지 마세요.


## 완료 기준과 주의

요청 Method·Path·Body·상태코드와 파일의 변화를 설명할 수 있어야 합니다. 코드가 실행된다는 이유만으로 정답은 아닙니다.
이 교시의 저장 파일은 이 폴더의 data/knowledge.json이며, 다른 교시와 공유하지 않습니다. 01에는 저장 파일이 없습니다.
파일 처리·잠금·초기화 도구는 제공 코드입니다. 내부를 모두 새로 구현하는 과제가 아닙니다.
/health는 경로 응답 확인일 뿐 AI 모델·DB 준비 상태를 확인하지 않습니다. 인증·DB·LLM 호출은 오늘 추가하지 않습니다.

## 구현한 조회 기능의 상세 동작 구조

아래 설명은 현재 구현된 코드를 기준으로 합니다. 존재하지 않는 ID의 404 응답 메시지는 `Knowledge not found`입니다. 기존 테스트는 404 상태 코드만 검사하며 메시지 본문은 검사하지 않습니다.

### 1. 파일별 역할과 요청 흐름

| 파일 | 역할 | 주요 입력과 출력 |
|---|---|---|
| `main.py` | URL을 함수에 연결하고 HTTP 응답과 오류를 처리 | 요청 → 목록·단일 항목·HTTP 오류 |
| `logic.py` | 파일에서 읽은 데이터의 필터링과 ID 검색 | category → list, knowledge_id → dict 또는 None |
| `storage.py` | JSON 파일 경로와 읽기·쓰기, 공용 잠금 제공 | JSON 파일 → Python dict |
| `data/knowledge.json` | 실제 지식 데이터 보관 | 최상위 객체에 next_id와 entries 저장 |
| `tests/conftest.py` | 테스트마다 독립적인 임시 저장소와 클라이언트 제공 | 고정 데이터 → client와 임시 파일 경로 |
| `tests/test_api.py` | 응답과 조회 전후 파일 보존 확인 | API 호출 → assert 검증 |

조회 요청은 다음 순서로 처리됩니다.

```text
클라이언트의 GET 요청
  → FastAPI가 경로를 선택하고 입력값을 검증
  → main.py가 logic.py의 조회 함수 호출
  → logic.py가 LOCK을 획득하고 storage.read_data() 호출
  → JSON 파일을 dict로 읽은 뒤 LOCK 해제
  → 메모리에서 목록 필터링 또는 ID 검색
  → main.py에서 결과 반환 또는 404 예외 발생
  → FastAPI가 JSON 응답 생성
```

`logic.py`는 HTTP 상태 코드를 결정하지 않습니다. 검색 실패는 `None`으로 반환하고, 이를 HTTP 404로 바꾸는 책임은 `main.py`에 있습니다. 이 구조에서는 데이터 조회 함수의 결과를 HTTP 외의 코드에서도 사용할 수 있습니다.

### 2. 목록 조회와 카테고리 필터링

`GET /api/knowledge`는 `main.py`의 `list_knowledge()`로 연결됩니다. `category: str | None = None`은 생략 가능한 쿼리 매개변수이며, 생략하면 `None`, 전달하면 문자열로 처리됩니다.

```text
GET /api/knowledge
  → list_knowledge(category=None)
  → repo.list_entries(None)
  → 전체 entries 반환

GET /api/knowledge?category=api
  → list_knowledge(category="api")
  → repo.list_entries("api")
  → category가 "api"인 항목만 반환
```

`list_entries()`의 내부 처리 순서는 다음과 같습니다.

1. `with LOCK:` 안에서 `read_data()`를 실행해 저장 파일 전체를 읽습니다.
2. `data["entries"]`를 꺼냅니다. 최상위 객체의 `next_id`는 응답에 포함하지 않습니다.
3. `category is not None`이면 리스트 컴프리헨션으로 `entry["category"] == category`인 항목만 새 목록에 담습니다.
4. 최종 `entries`를 반환합니다. FastAPI는 이 Python 목록을 JSON 배열로 응답합니다.

필터는 문자열의 정확한 일치를 비교합니다. 대소문자 변경이나 공백 제거는 하지 않으며, `?category=`처럼 빈 문자열을 보내도 필터가 적용됩니다. 일치하는 항목이 없으면 오류 대신 `200 OK`와 빈 배열 `[]`을 반환합니다. 초기 데이터에서 `category=api`의 결과는 ID 2·3이며, 원래 저장 순서를 유지합니다.

### 3. ID로 단일 항목 조회

`GET /api/knowledge/2`는 `get_knowledge(knowledge_id: int)`로 연결됩니다. FastAPI가 경로의 `2`를 정수로 변환하고, 함수는 `repo.find_entry(2)`를 호출합니다.

현재 검색 코드는 다음과 같습니다.

```python
entries = data['entries']
data_index = next(
    (index for (index, d) in enumerate(entries) if d["id"] == knowledge_id),
    None,
)

if data_index is not None:
    return entries[data_index]

return None
```

`enumerate(entries)`는 각 항목에 대해 `(목록 인덱스, 항목 dict)`를 만듭니다. 초기 데이터에서 ID 2인 항목은 인덱스 1에 있습니다. 따라서 ID를 목록 인덱스로 직접 사용하지 않고, 각 dict의 `id` 값을 비교합니다.

제너레이터 표현식은 ID가 일치하는 항목의 인덱스만 차례로 제공합니다. `next(..., None)`은 첫 번째 일치 인덱스를 얻으면 검색을 끝내고, 끝까지 일치하는 항목이 없으면 기본값 `None`을 반환합니다. 중복 ID가 있다면 첫 번째 항목이 선택됩니다.

`data_index is not None`으로 검사하는 이유는 첫 항목의 인덱스가 `0`이기 때문입니다. `if data_index:`로 검사하면 0을 거짓으로 판단해 정상 항목을 놓칩니다. 현재 구현은 인덱스 0도 정상적으로 반환합니다.

목록과 상세 조회 모두 요청마다 JSON 파일 전체를 읽습니다. 상세 검색은 최악의 경우 모든 항목을 순회하므로, 데이터가 커지면 파일 읽기와 검색 비용도 함께 증가합니다.

### 4. 정상 응답과 404·422 오류가 나뉘는 위치

| 요청 예시 | 처리 위치 | 결과 |
|---|---|---|
| `GET /api/knowledge/2` | 정수 검증 → 검색 성공 → dict 반환 | 200과 해당 항목 |
| `GET /api/knowledge/9999` | 정수 검증 → 검색 실패 → main.py에서 예외 발생 | 404와 오류 메시지 |
| `GET /api/knowledge/foo` | FastAPI의 정수 입력 검증 실패 | 422와 검증 오류 정보 |

검색에 실패하면 `find_entry()`가 `None`을 반환합니다. `main.py`는 `if entry == None:` 조건에서 다음 예외를 발생시킵니다.

```python
raise HTTPException(status_code=404, detail="Knowledge not found")
```

예외가 발생하면 아래의 `return entry`는 실행되지 않으며, FastAPI가 다음 응답을 만듭니다.

```json
{"detail": "Knowledge not found"}
```

반면 `foo`는 정수로 변환할 수 없어 경로 매개변수 검증 단계에서 거절됩니다. 이 경우 `get_knowledge()`와 `find_entry()`가 실행되기 전에 422 응답이 만들어지므로 저장 파일도 읽지 않습니다.

### 5. 조회 요청이 저장 파일을 변경하지 않는 이유

`read_data()`는 `DATA.open("r", encoding="utf-8")`로 파일을 읽고, `json.load()`로 메모리의 dict를 생성합니다. 목록 필터링과 ID 검색은 이 메모리 데이터에서 수행됩니다.

`logic.py`는 `write_data`를 import하고 있지만, 현재 조회 함수에서는 호출하지 않습니다. 따라서 조회 과정에는 파일 쓰기, `next_id` 증가, 항목 추가·수정·삭제가 없습니다. 메모리에서 필터링한 목록도 파일에 다시 저장하지 않습니다.

`LOCK`은 같은 프로세스에서 이 잠금을 사용하는 코드끼리 파일 접근을 조율합니다. 현재 조회 코드는 파일을 읽는 구간에만 잠금을 잡고, 읽기가 끝난 뒤에는 잠금을 해제한 상태에서 필터링과 검색을 수행합니다. `with` 블록은 읽기 중 예외가 발생해도 잠금을 해제합니다. 이 잠금이 여러 서버 프로세스 사이의 접근까지 조율하는 것은 아닙니다.

파일이 없거나 JSON이 손상되면 `read_data()`의 예외가 전달됩니다. 이 상황을 검색 결과 없음으로 처리하지 않으므로, 존재하지 않는 ID에 대한 404와 저장 파일 읽기 실패는 서로 다른 경우입니다.

### 6. 테스트가 임시 파일로 동작하는 구조

`isolated_client`는 각 테스트 실행 전에 다음 환경을 준비합니다.

1. pytest의 `tmp_path` 아래에 새로운 `knowledge.json`을 만듭니다.
2. `SEED`의 초기 데이터 3건을 JSON으로 저장합니다.
3. `monkeypatch.setattr(store, "DATA", test_file)`로 `storage.DATA`를 임시 경로로 바꿉니다.
4. `TestClient(app)`를 생성하고 `yield client, test_file`로 테스트에 전달합니다.
5. 테스트가 끝나면 클라이언트 컨텍스트를 종료하고, monkeypatch가 경로 변경을 복구합니다.

`logic.py`가 import한 `read_data()`도 실행할 때는 자신이 정의된 `storage` 모듈의 `DATA`를 참조합니다. 따라서 `storage.DATA`를 바꾸면 API의 실제 조회 경로가 임시 파일로 연결됩니다. 별도로 uvicorn 서버를 실행하지 않아도 TestClient를 통해 앱의 요청 처리 흐름을 검사할 수 있습니다.

각 테스트는 새 파일에서 시작하므로 다른 테스트의 파일 상태에 의존하지 않습니다. 실제 `data/knowledge.json`은 테스트 대상이 아닙니다.

### 7. 응답과 파일 보존 검증

| 테스트 | 확인하는 동작 |
|---|---|
| `test_health` | `/health`의 200 응답과 `{"status": "ok"}` |
| `test_list_and_filter` | 전체 ID 1·2·3, next_id 미포함, api 필터의 ID 2·3, unknown 필터의 빈 배열, 파일 보존 |
| `test_detail_and_errors` | ID 2의 제목, 없는 ID의 404, 잘못된 타입의 422, 파일 보존 |

파일 보존 검사는 요청 전에 원본 바이트를 보관하고 요청들이 끝난 뒤 다시 비교합니다.

```python
before = path.read_bytes()

# 정상 조회와 오류 요청 실행

assert path.read_bytes() == before
```

JSON을 파싱한 값만 비교하는 것이 아니라 바이트 전체를 비교하므로, 저장된 값뿐 아니라 공백·들여쓰기·줄바꿈 등 파일 내용의 변화도 감지합니다. 상세 조회 테스트는 정상·404·422 요청을 모두 실행한 후 최종 파일이 처음과 같은지 확인합니다. 중간에 파일이 변경되었다가 원상 복구되는 상황까지 검출하는 검사는 아닙니다.

기존 테스트는 상세 항목의 전체 필드나 404 메시지 본문까지 검사하지 않습니다. 또한 위 설명은 코드 검토에 따른 동작 설명이며, 문서 작성 환경에는 pytest가 설치되어 있지 않아 테스트 실행 결과를 확인하지 못했습니다.
