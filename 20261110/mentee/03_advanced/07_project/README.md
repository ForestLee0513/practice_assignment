# 실습 07 · 함께 통합하고 프로젝트 준비

수강생용입니다. BEGIN/END 사이 TODO를 구현합니다. 미완성 요청은 NotImplementedError 또는 미등록 Route로 실패할 수 있습니다.

**PPT 47–55쪽 / 40분 / 심화**

## 작업 순서

1. 이전 교시 서버를 Ctrl+C로 종료합니다.
2. 아래 교시 폴더를 현재 작업 폴더로 사용합니다. 이 폴더가 프로젝트 루트입니다.
3. 요구된 TODO를 구현하고 서버를 실행합니다. 앞 교시가 미완성이어도 이 폴더의 선행 기능은 제공되어 있습니다.
4. /docs에서 아래 예상 결과와 실제 파일을 대조합니다.

```powershell
# 수강생용 폴더에서 시작한 경우
cd ".\03_심화\07_project"
python -m uvicorn app.main:app --reload
```

브라우저: `http://127.0.0.1:8000/docs` · 첫 확인: `http://127.0.0.1:8000/health`

활성화를 하지 않았다면 현재 교시 폴더에서 다음처럼 같은 가상환경 Python을 직접 사용합니다.

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

심화의 app.main:app 실행에서도 app 폴더 안으로 cd하지 않습니다. 새로운 교시로 이동할 때 이전 서버는 반드시 종료합니다.

## 완성할 부분

| TODO ID | 파일                                 | 완료 요구사항                                               |
| ------- | ------------------------------------ | ----------------------------------------------------------- |
| H07-01  | `app/repositories/json_knowledge.py` | 생성 데이터와 next_id를 파일에 저장하는 연결을 완성하세요.  |
| H07-02  | `app/routers/knowledge.py`           | Repository 삭제가 성공한 경우 빈 204 응답을 반환하세요.     |
| H07-03  | `tests/test_api.py`                  | 잘못된 입력이 422이며 저장 파일을 바꾸지 않는지 검사하세요. |
| H07-04  | `tests/test_api.py`                  | 없는 category를 조회한 목록이 200과 빈 배열인지 검사하세요. |

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

8교시가 되면 tests/test_daily_project.py의 H08-01~03을 완성합니다. 7교시는 위 test_api.py만 실행하며, 일일프로젝트 이후 `python -m pytest -q`로 전체를 확인합니다.

## 다음 교시

실습07*기록.md에 강사 예시 결과를 적고, 일일프로젝트*기록.md는 8교시에 작성합니다. 08_daily_project/README.md의 안내를 읽은 뒤 이 프로젝트를 계속 사용하세요. 데이터를 초기화하지 않습니다.

## 완료 기준과 주의

요청 Method·Path·Body·상태코드와 파일의 변화를 설명할 수 있어야 합니다. 코드가 실행된다는 이유만으로 정답은 아닙니다.
이 교시의 저장 파일은 이 폴더의 data/knowledge.json이며, 다른 교시와 공유하지 않습니다. 01에는 저장 파일이 없습니다.
파일 처리·잠금·초기화 도구는 제공 코드입니다. 내부를 모두 새로 구현하는 과제가 아닙니다.
/health는 경로 응답 확인일 뿐 AI 모델·DB 준비 상태를 확인하지 않습니다. 인증·DB·LLM 호출은 오늘 추가하지 않습니다.

## 일일프로젝트 기록 (README의 이어지는 부분)

[일일프로젝트 실행 기록](일일프로젝트_기록.md)을 작성하고 이 README와 함께 제출합니다.
읽기 쉽게 분리한 짧은 기록 틀이며 별도 장문 보고서가 아닙니다. 제출할 때 README에 합쳐도 됩니다.

## 구현 검토 및 풀이 기록

비교 기준은 `../../../mentor/03_advanced/07_project/`의 정답 코드입니다. 2026-11-10에 작성한 구현과 테스트를 검토했습니다.

### H07-01~04: 통합 구현 결과

| 항목                    | 작성한 코드                                                          | 검토 결과                                                                     |
| ----------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| H07-01 생성 결과 저장   | `write_data(data)`                                                   | 정답과 동일. 새 항목과 증가한 `next_id`를 전체 데이터에 함께 저장함           |
| H07-02 삭제 성공 응답   | `return Response(status_code=204)`                                   | 정답과 동일. Repository의 삭제 성공 결과를 본문 없는 HTTP 204 응답으로 연결함 |
| H07-03 잘못된 입력 검사 | `assert r.status_code == 422`와 `assert path.read_bytes() == before` | 정답과 동일. 입력 오류 응답과 저장 파일 불변을 함께 확인함                    |
| H07-04 빈 목록 검사     | `assert empty.status_code == 200`와 `assert empty.json() == []`      | 정답과 동일. 조건에 맞는 항목이 없는 목록 조회는 정상 200과 빈 배열임         |

07번 풀이에는 수정이 필요한 동작 차이가 없었습니다. 정답과의 차이는 TODO 안내와 해설 주석입니다.

생성 함수는 같은 `with LOCK:` 안에서 파일 읽기 → 입력 딕셔너리 복사 → ID 지정 → 목록 추가 → `next_id` 증가 → 파일 저장을 수행합니다. 응답이 성공한 것과 파일에 저장된 것은 각각 확인해야 하므로 생성 테스트는 POST 201, 상세 재조회 결과, 파일의 항목 수·`next_id`·마지막 항목을 함께 검사합니다. 잠금은 단일 프로세스 범위입니다.

삭제 함수는 Repository의 `False`를 404로, `True`를 빈 204 응답으로 연결합니다. 목록 필터 결과가 없는 경우의 `200 + []`와 특정 ID가 없는 경우의 404는 의미가 다릅니다.

### 함께 작성한 08번 테스트: B 재조회 수정 과정

처음 B 수정 검사는 PUT 응답의 상태와 `content`만 확인했습니다. 이후 재조회 코드를 추가하면서 `client.get(b["id"])`로 정수 ID를 URL 인자에 전달하여 `TypeError`가 발생했습니다.

상세 경로 문자열로 수정한 뒤 재조회가 정상 실행됐지만, 당시에는 GET 응답으로 `r`을 덮어쓰고 `content`만 비교하여 PUT의 상태 코드와 전체 본문·기존 ID 검사가 빠져 있었습니다.

최종 구현은 PUT 응답의 200을 먼저 검사하고, B의 기존 ID와 수정한 필드 전체를 묶은 `expected`를 만들어 GET 응답 전체와 비교합니다.

```python
assert r.status_code == 200  # PUT 응답
expected = dict(changed, id=b["id"])

r = client.get(f"/api/knowledge/{b['id']}")
assert r.status_code == 200
assert r.json() == expected
```

이제 H08-01 요구사항을 충족합니다. mentor 정답과 같은 전체 본문 비교를 수행하며, 현재 구현에는 GET의 200을 명시적으로 확인하는 검사도 있습니다. `r`을 재사용할 때는 새 요청 결과를 대입하기 전에 이전 응답에 필요한 검사를 끝내야 합니다.

H08-02는 422와 파일 바이트 불변을 검사하여 정답과 같습니다. `before_invalid == path.read_bytes()`처럼 동등 비교의 좌우 순서를 바꿔도 검사 의미는 같습니다.

### C 삭제의 204·빈 본문·404가 각각 확인하는 것

처음 H08-03은 DELETE 204와 삭제 후 GET 404만 검사했습니다. 최종 구현에는 DELETE 직후 `assert r.content == b""`를 추가하여 세 가지 요구사항을 모두 충족했습니다.

- DELETE 204: 삭제 요청이 성공했다는 상태 코드입니다.
- DELETE의 `r.content == b""`: 삭제 성공 응답에 본문이 없는지 확인합니다.
- 이후 GET 404: 삭제된 C를 다시 조회할 수 없는지 확인합니다.

GET 404가 나와도 앞선 DELETE 응답의 본문까지 검사한 것은 아닙니다. `r`을 GET 응답으로 덮어쓰기 전에 빈 본문을 확인해야 합니다.

```python
assert r.status_code == 204
assert r.content == b""
r = client.get(f"/api/knowledge/{c['id']}")
assert r.status_code == 404
```

07번의 `test_delete_empty_body_and_other_entries`에 있던 빈 본문 검사를 08번 시나리오에서도 명시적으로 수행합니다. 삭제 성공 응답의 형식과 삭제 후 데이터 부재를 각각 확인한다는 점을 배웠습니다.

### 실제 검증 결과

07_project 폴더에서 기존 가상환경으로 실행했습니다.

```bash
PYTHONDONTWRITEBYTECODE=1 /home/swchoi/projects/python/practice_assignment/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_api.py tests/test_daily_project.py
```

최종 결과는 **21개 통과**입니다. 07번 API 테스트 20개와 08번 일일프로젝트 테스트 1개가 포함됩니다. Starlette TestClient의 httpx 사용 중단 예정 경고가 1건 발생했습니다.

테스트는 fixture의 임시 JSON 파일을 사용합니다. 이후 실제 Uvicorn 서버를 `http://localhost:8000`에서 실행해 HTTP 요청과 두 차례 SIGINT 종료·재실행도 검증했습니다. 수정한 B와 C 삭제 상태, 기존 3건 보존, 최종 5건·next_id=7을 확인했습니다. 상세 결과는 [일일프로젝트 실행 기록](일일프로젝트_기록.md)의 3·4번 표에 기록했습니다. 브라우저 직접 조작은 포함하지 않았습니다. 최종 수정 후에도 21개 테스트가 모두 통과했으며, H08-01의 PUT 상태·전체 재조회 본문 검사와 H08-03의 빈 본문 검사도 코드에서 확인했습니다. H07-01~04 및 H08-01~03의 코드 요구사항을 모두 충족합니다.
