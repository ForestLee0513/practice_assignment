# 실습 04 · 같은 지식의 본문 수정

수강생용입니다. BEGIN/END 사이 TODO를 구현합니다. 미완성 요청은 NotImplementedError 또는 미등록 Route로 실패할 수 있습니다.

**PPT 28–32쪽 / 35분 / 심화**

## 작업 순서

1. 이전 교시 서버를 Ctrl+C로 종료합니다.
2. 아래 교시 폴더를 현재 작업 폴더로 사용합니다. 이 폴더가 프로젝트 루트입니다.
3. 요구된 TODO를 구현하고 서버를 실행합니다. 앞 교시가 미완성이어도 이 폴더의 선행 기능은 제공되어 있습니다.
4. /docs에서 아래 예상 결과와 실제 파일을 대조합니다.

```powershell
# 수강생용 폴더에서 시작한 경우
cd ".\03_심화\04_update"
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
| H04-03 | `main.py` | 데이터 함수가 None을 반환하면 Router에서 404를 보내세요. |
| H04-01 | `logic.py` | fields의 복사본 updated를 만들고 기존 요청 ID를 유지하세요. |
| H04-02 | `logic.py` | 찾은 위치 i를 교체하고 저장하세요. 다른 항목과 next_id는 그대로 두세요. |
| H04-04 | `tests/test_api.py` | 두 번 수정한 뒤 next_id와 항목 수가 변하지 않았는지 검사하세요. |

## 요청·응답·저장 확인

1. GET /health → 200, {"status":"ok"}
2. GET /docs → 200인 문서 화면. 실행 결과는 Server response에서 읽습니다.
3. 초기 파일: next_id=4, entries 3건 (ID 1·2·3). 이 폴더에서 이미 변경했다면 실제 상태를 먼저 확인합니다.
4. GET /api/knowledge → 200, entries 배열만 반환. GET /api/knowledge/2 → title=서버 실행.
5. GET /api/knowledge/9999 → 404, detail=Knowledge not found. GET /api/knowledge/foo → 422. GET 전후 파일은 변하지 않습니다.
6. category=api → 초기 ID 2·3, category=setup → 초기 ID 1, category=unknown → 200과 []. 생략은 전체입니다.
7. 정상 POST → 201. 초기 상태에서 첫 생성 ID는 4이며 entries=4건·next_id=5입니다. 실제 응답 ID로 재조회합니다.
8. 빈 content·필수값 누락·길이 초과 POST → 422, entries와 next_id 불변. 422 문구 전체는 버전별로 다를 수 있습니다.
9. PUT은 title·content·category를 모두 보냅니다. 정상 200·같은 ID·같은 개수·같은 next_id. 존재하지 않는 ID는 404, content만 보내면 422.


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

## 구현 검토 및 수정 기록

비교 기준은 `../../../mentor/03_advanced/04_update/`의 정답 파일입니다. 직접 수정한 현재 코드는 그대로 유지하고, 검토 과정과 정답과의 차이를 기록했습니다.

### 처음 구현에서 빠졌던 처리

처음에는 `updated = dict(fields)`로 복사하고 목록의 항목을 교체했지만, 기존 ID를 복사본에 지정하는 처리와 `write_data(data)` 호출이 빠져 있었습니다. 입력 필드는 title·content·category이므로 복사만으로는 id가 생기지 않습니다. 이 상태에서는 응답 모델이 요구하는 id가 없어 응답 검증 오류가 발생하고, 메모리에서 바꾼 내용도 파일에 저장되지 않습니다.

### 수정 과정에서 혼동했던 ID와 인덱스

다음 단계에서는 아래와 같이 작성했습니다.

```python
updated["id"] = i
data["entries"][knowledge_id] = updated
```

두 번째 줄에서는 리스트 위치에 ID를 사용한 것이 문제였습니다. `knowledge_id`는 요청한 항목의 식별자이고, `i`는 `enumerate()`가 알려주는 0부터 시작하는 리스트 위치입니다.

| 리스트 위치 i | 초기 항목 ID |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 2 | 3 |

ID 2를 수정하면 찾은 위치는 i=1입니다. 그런데 `updated["id"] = i`는 ID를 1로 바꾸고, `data["entries"][knowledge_id]`는 인덱스 2에 있는 ID 3 항목을 덮어씁니다. 당시 테스트는 응답 ID가 2 대신 1이라 실패했습니다. ID를 인덱스로 쓰면 값에 따라 IndexError가 발생할 수도 있습니다. 삭제 등으로 ID에 빈칸이 생겨도 두 값은 서로 다른 역할을 유지합니다.

### 직접 수정한 현재 코드

```python
updated = dict(fields)
updated["id"] = knowledge_id
data["entries"][i] = updated
write_data(data)
```

위 처리는 검색 조건 `if entry["id"] == knowledge_id:`를 만족한 경우에 수행됩니다. 원본 입력을 복사하고 기존 ID를 유지한 뒤, 검색으로 찾은 위치만 교체해 저장합니다. 새 항목을 추가하지 않으므로 항목 수와 next_id도 유지됩니다. 읽기부터 저장까지 기존 `with LOCK:` 안에서 처리합니다.

### 테스트에서 바꾼 비교 기준

처음 H04-04에는 `assert path.read_bytes() == before`를 작성했습니다. 하지만 이 테스트의 `before`는 JSON을 읽은 딕셔너리이므로 bytes와 비교할 수 없습니다. 수정 성공 시 본문은 바뀌어야 하므로 파일 전체가 이전과 같은지 검사하는 것도 목적에 맞지 않습니다.

완성한 검사는 다음과 같습니다.

```python
assert saved["next_id"] == before["next_id"]
assert len(saved["entries"]) == len(before["entries"])
```

기존 테스트는 같은 요청을 두 번 수행하고, 응답의 ID와 필드, 다른 항목의 유지 여부, 재조회한 본문도 함께 검사합니다. 반면 잘못된 요청이나 없는 ID에 대한 테스트에서는 파일이 바뀌면 안 되므로 바이트 단위의 동일성 검사가 적절합니다.

### mentor 정답과 현재 코드의 차이

| 항목 | mentor 정답 | 현재 작성한 내용 | 판단 |
|---|---|---|---|
| H04-01 입력 복사 | `updated = dict(fields)` | 동일 | 원본 입력을 변경하지 않음 |
| 기존 ID 유지 | H04-01 안에서 `updated["id"] = knowledge_id` | H04-02 안에서 같은 코드 수행 | 주석 구간만 다르며 실행 순서와 동작은 같음 |
| H04-02 교체 및 저장 | `data["entries"][i] = updated` 후 `write_data(data)` | 동일 | 찾은 항목만 교체하고 저장함 |
| H04-03 없는 항목 처리 | `updated is None`이면 404 발생 | 동일 | HTTP 오류는 Router에서 처리함 |
| H04-04 테스트 | 수정 후 next_id와 항목 수 유지 검사 | 같은 조건 검사 | 요구사항 충족 |
| 주석 | 정답 해설 | TODO 안내 주석과 테스트 설명 | 실행에 영향 없음 |

### 검증 결과

수정한 현재 구현으로 `tests/test_api.py`를 실행한 결과 **16개 테스트가 모두 통과**했습니다. 각 테스트는 임시 저장 파일을 사용하므로 실제 `data/knowledge.json`은 변경하지 않았습니다.

이번 수정의 핵심은 **ID는 항목의 식별자로 유지하고, 인덱스는 리스트에서 교체할 위치로 사용한다**는 점입니다.
