# 실습 03 · 안내문 등록과 파일 저장

수강생용입니다. BEGIN/END 사이 TODO를 구현합니다. 미완성 요청은 NotImplementedError 또는 미등록 Route로 실패할 수 있습니다.

**PPT 20–27쪽 / 30분 / 심화**

## 작업 순서

1. 이전 교시 서버를 Ctrl+C로 종료합니다.
2. 아래 교시 폴더를 현재 작업 폴더로 사용합니다. 이 폴더가 프로젝트 루트입니다.
3. 요구된 TODO를 구현하고 서버를 실행합니다. 앞 교시가 미완성이어도 이 폴더의 선행 기능은 제공되어 있습니다.
4. /docs에서 아래 예상 결과와 실제 파일을 대조합니다.

```powershell
# 수강생용 폴더에서 시작한 경우
cd ".\03_심화\03_create"
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
| H03-01 | `logic.py` | fields를 복사한 entry를 만들고 현재 next_id를 id로 지정하세요. |
| H03-02 | `logic.py` | entry를 추가하고 다음 ID를 증가시켜 data 전체를 저장하세요. |
| H03-03 | `tests/test_api.py` | 초기 3건 기준 생성된 entry가 요청 필드와 새 id=4를 포함하는지 검사하세요. |
| H03-04 | `tests/test_api.py` | 잘못된 입력에 422가 나오고 파일이 변경되지 않았는지 모두 검사하세요. |

## 요청·응답·저장 확인

1. GET /health → 200, {"status":"ok"}
2. GET /docs → 200인 문서 화면. 실행 결과는 Server response에서 읽습니다.
3. 초기 파일: next_id=4, entries 3건 (ID 1·2·3). 이 폴더에서 이미 변경했다면 실제 상태를 먼저 확인합니다.
4. GET /api/knowledge → 200, entries 배열만 반환. GET /api/knowledge/2 → title=서버 실행.
5. GET /api/knowledge/9999 → 404, detail=Knowledge not found. GET /api/knowledge/foo → 422. GET 전후 파일은 변하지 않습니다.
6. category=api → 초기 ID 2·3, category=setup → 초기 ID 1, category=unknown → 200과 []. 생략은 전체입니다.
7. 정상 POST → 201. 초기 상태에서 첫 생성 ID는 4이며 entries=4건·next_id=5입니다. 실제 응답 ID로 재조회합니다.
8. 빈 content·필수값 누락·길이 초과 POST → 422, entries와 next_id 불변. 422 문구 전체는 버전별로 다를 수 있습니다.


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

비교 기준은 `../../../mentor/03_advanced/03_create/`의 정답 파일입니다. 현재 구현은 H03-01~H03-04 요구사항을 충족하며, 정답과 동작이 같습니다.

### 처음 잘못 이해했던 부분: 대입과 복사의 차이

처음에는 아래처럼 작성했습니다.

```python
next_id = data['next_id']
fields['id'] = next_id
entry = fields
data['entries'].append(fields)
```

`entry = fields`는 딕셔너리를 복사하지 않습니다. 두 변수가 같은 딕셔너리를 가리키므로, `fields['id'] = next_id`는 호출자가 전달한 원본까지 변경합니다. 따라서 등록과 저장은 되더라도 H03-01의 “fields를 복사한 entry”라는 요구사항은 충족하지 못했습니다.

예를 들어 원래 `fields`에 `title`, `content`, `category`만 있었다면, 이전 구현으로 `create(fields)`를 호출한 뒤에는 원본에도 `id`가 추가됐습니다. 직접 확인했을 때 원본 유지 여부는 `False`, `entry is fields`는 `True`였습니다.

### 해결 과정과 현재 구현

1. `dict(fields)`로 별도의 딕셔너리를 만듭니다.
2. 원본 대신 복사본 `entry`에 새 ID를 지정합니다.
3. 저장 목록에도 `entry`를 추가합니다.
4. `next_id`를 증가시키고 전체 데이터를 파일에 저장합니다.

현재 작성한 코드는 다음과 같습니다. 이 과정은 모두 기존 `with LOCK:` 안에서 수행됩니다.

```python
next_id = data['next_id']
entry = dict(fields)
entry['id'] = next_id

data['entries'].append(entry)
data['next_id'] += 1
write_data(data)
```

이제 `fields`는 변경되지 않고, `entry`에만 ID가 추가됩니다. `dict(fields)`는 얕은 복사지만, 이 과제의 입력 필드는 모두 문자열이므로 요구사항을 충족합니다.

### mentor 정답과 내가 작성한 코드의 차이

| 항목 | mentor 정답 | 현재 작성한 내용 | 판단 |
|---|---|---|---|
| H03-01 복사 | `entry = dict(fields)` | 동일 | 원본을 변경하지 않음 |
| H03-01 ID 지정 | `entry["id"] = data["next_id"]` | `next_id = data['next_id']` 후 `entry['id'] = next_id` | 중간 변수 사용 여부만 다르고 결과는 같음 |
| H03-02 저장 | `entry` 추가 → `next_id` 증가 → `write_data(data)` | 동일 | 처리 순서와 동작이 같음 |
| H03-03 생성 검사 | `assert entry == dict(payload, id=4)` | 동일 | 요청 필드와 새 ID를 함께 검사함 |
| H03-04 잘못된 입력 검사 | 상태 코드 422와 파일 바이트 불변 검사 | 동일 | 저장 내용과 `next_id`가 바뀌지 않았는지 확인함 |
| 주석과 표기 | 정답의 해설 주석, 큰따옴표 | TODO 안내 주석과 직접 적은 주석, 작은따옴표 | 실행 결과에는 영향 없음 |

정답 해설에는 ID 발급까지 같은 잠금 안에서 수행한다는 점과, 이 잠금은 단일 프로세스 범위이며 DB 트랜잭션은 아니라는 점도 적혀 있습니다. 현재 코드 역시 같은 잠금 안에서 처리합니다. 또한 테스트의 `id=4`는 매번 초기 3건의 임시 데이터로 시작하기 때문에 기대할 수 있는 값이며, 실제 파일에서 항상 첫 ID가 4라는 뜻은 아닙니다.

### 검증 결과와 배운 점

수정 후 `tests/test_api.py`를 실행한 결과 **14개 테스트가 모두 통과**했습니다. 테스트는 임시 저장 파일을 사용하므로 실제 `data/knowledge.json`은 변경하지 않습니다.

이전 구현도 기존 테스트 14개를 통과했습니다. HTTP 경로에서 `payload.model_dump()`로 새 딕셔너리를 만들어 `create()`에 전달하고, 테스트에는 `create()`가 전달받은 딕셔너리를 그대로 유지하는지 확인하는 항목이 없기 때문입니다. 따라서 테스트 통과와 별개로 과제의 복사 요구사항을 코드와 직접 호출로 확인해야 했습니다.

이번 수정의 핵심은 **`entry = fields`는 같은 객체를 공유하고, `entry = dict(fields)`는 별도의 딕셔너리를 만든다**는 차이를 이해하는 것입니다.
