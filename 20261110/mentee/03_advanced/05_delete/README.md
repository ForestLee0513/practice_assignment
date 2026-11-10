# 실습 05 · 삭제와 실패 후 데이터 보존

수강생용입니다. BEGIN/END 사이 TODO를 구현합니다. 미완성 요청은 NotImplementedError 또는 미등록 Route로 실패할 수 있습니다.

**PPT 33–38쪽 / 40분 / 심화**

## 작업 순서

1. 이전 교시 서버를 Ctrl+C로 종료합니다.
2. 아래 교시 폴더를 현재 작업 폴더로 사용합니다. 이 폴더가 프로젝트 루트입니다.
3. 요구된 TODO를 구현하고 서버를 실행합니다. 앞 교시가 미완성이어도 이 폴더의 선행 기능은 제공되어 있습니다.
4. /docs에서 아래 예상 결과와 실제 파일을 대조합니다.

```powershell
# 수강생용 폴더에서 시작한 경우
cd ".\03_심화\05_delete"
python -m uvicorn main:app --reload
```

브라우저: `http://127.0.0.1:8000/docs` · 첫 확인: `http://127.0.0.1:8000/health`

활성화를 하지 않았다면 현재 교시 폴더에서 다음처럼 같은 가상환경 Python을 직접 사용합니다.

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

심화의 app.main:app 실행에서도 app 폴더 안으로 cd하지 않습니다. 새로운 교시로 이동할 때 이전 서버는 반드시 종료합니다.

## 완성할 부분

| TODO ID | 파일                | 완료 요구사항                                                                |
| ------- | ------------------- | ---------------------------------------------------------------------------- |
| H05-02  | `main.py`           | 삭제 성공 시 본문 없는 204를 반환하세요.                                     |
| H05-01  | `logic.py`          | 대상 위치를 제거하고 저장한 뒤 True를 반환하세요. next_id는 변경하지 마세요. |
| H05-03  | `tests/test_api.py` | 삭제 상태가 204이고 실제 응답 바이트가 비어 있는지 확인하세요.               |
| H05-04  | `tests/test_api.py` | 404와 422 삭제 요청 이후 파일 내용이 이전과 같은지 확인하세요.               |

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
10. DELETE 정상 → 204와 빈 본문. 같은 ID GET/DELETE → 404. 나머지 지식과 next_id는 유지됩니다.

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

## 응답 객체와 204 응답 확인 정리

`r = client.delete("/api/knowledge/2")`에서 `r` 자체가 클라이언트가 받은 응답 객체입니다. `r.json()`은 응답 전체를 가져오는 기능이 아니라, 응답 본문을 JSON으로 해석해 파이썬 값으로 바꾸는 메서드입니다.

| 표현            | 확인하는 내용        | 예시                                   |
| --------------- | -------------------- | -------------------------------------- |
| `r`             | 응답 객체 자체       | 상태 코드·헤더·본문에 접근할 수 있음   |
| `r.status_code` | HTTP 상태 코드       | `204`                                  |
| `r.headers`     | 응답 헤더            | `r.headers.get("content-type")`        |
| `r.text`        | 문자열로 해석한 본문 | 빈 본문이면 `""`                       |
| `r.content`     | bytes 형태의 본문    | 빈 본문이면 `b""`                      |
| `r.json()`      | JSON으로 해석한 본문 | JSON 객체라면 dict, 배열이라면 list 등 |

### 삭제 성공 응답 검사

05번 과제의 삭제 성공 응답은 **204 No Content**로, 본문이 없습니다. 따라서 JSON 해석 대신 상태 코드와 빈 본문을 검사합니다.

```python
r = client.delete("/api/knowledge/2")
assert r.status_code == 204
assert r.content == b""
```

과제 H05-03은 실제 응답 바이트를 확인하도록 요구하므로, 현재 코드와 mentor 정답은 모두 `assert r.content == b""`를 사용합니다.

빈 본문에 `r.json()`을 호출하면 해석할 JSON이 없어 JSON 해석 오류가 발생합니다. 빈 본문은 JSON의 `{}`, `[]`, `null`과도 다릅니다. 이 값들은 각각 내용이 있는 JSON 본문입니다.

### 응답과 저장 파일은 별도로 검사

`r.content`는 HTTP 응답 본문이고, `path.read_bytes()`는 저장 파일의 내용입니다. 삭제 성공 시 응답은 비어 있어야 하지만, 파일에서는 대상 항목이 제거되어야 합니다. 나머지 항목과 next_id는 유지되어야 합니다.

반대로 없는 ID에 대한 404나 잘못된 ID 형식에 대한 422 요청에서는 저장 파일이 바뀌면 안 되므로 다음처럼 검사합니다.

```python
before = path.read_bytes()
assert client.delete("/api/knowledge/9999").status_code == 404
assert client.delete("/api/knowledge/foo").status_code == 422
assert path.read_bytes() == before
```

## 기존 풀이·현재 코드·mentor 정답 비교 기록

비교 기준은 `../../../mentor/03_advanced/05_delete/`입니다.

| 항목                     | 기존 풀이                                     | 현재 코드                   | mentor 정답 및 판단                                                                           |
| ------------------------ | --------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------- |
| H05-01 삭제              | `pop(i)` → `write_data(data)` → `return True` | 동일                        | 정답과 같은 동작. `return True`가 END 주석 뒤에 있지만 같은 조건 블록 안이므로 실행 차이 없음 |
| H05-02 성공 응답         | `Response(None, 204)`                         | `Response(status_code=204)` | 현재 코드는 정답과 동일                                                                       |
| H05-03 빈 본문 검사      | `assert r.text == ""`                         | `assert r.content == b""`   | 기존에는 문자열로 검사했고, 현재는 정답과 같이 응답 바이트를 검사함                           |
| H05-04 실패 시 파일 보존 | `assert path.read_bytes() == before`          | 동일                        | 정답과 동일                                                                                   |

### 기존 응답 생성 방식도 동작했던 이유

```python
# 기존 풀이
return Response(None, 204)

# 현재 코드 및 mentor 정답
return Response(status_code=204)
```

기존 풀이의 첫 번째 위치 인자 `None`은 본문, 두 번째 위치 인자 `204`는 상태 코드입니다. 이 경우에도 빈 본문과 204 응답을 만듭니다. 현재 코드는 기본 본문을 사용하고 상태 코드를 이름으로 지정하므로 의미를 더 쉽게 읽을 수 있습니다. 이전 풀이가 삭제 동작 오류를 일으킨 것은 아닙니다.

### 검증 결과

현재 구현으로 테스트를 실행한 결과 **19개 모두 통과**했습니다. H05-01~H05-04는 mentor 정답과 같은 동작을 합니다. 문서 정리 중 구현과 테스트 파일은 수정하지 않았습니다.
