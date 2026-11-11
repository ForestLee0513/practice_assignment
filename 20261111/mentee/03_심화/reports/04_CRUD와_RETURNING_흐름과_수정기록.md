# 심화 04. CRUD·RETURNING 흐름과 수정 기록

대상: `changes/04_crud.sql`

현재 파일은 새 지식을 추가하고, 그 행만 조회·수정·삭제한 다음 마지막에 모든 변경을 취소하는 흐름입니다. 조회·수정·삭제 조건은 모두 `id = 6`으로 작성되어 있습니다. **6은 이번 INSERT에서 실제로 반환된 ID가 6일 때만 올바른 값입니다.** DB 실행 결과는 직접 확인하지 않았으며, 아래 결과는 이 조건을 전제로 한 예상입니다.

## 1. 전체 실행 순서

```text
연결 DB 확인 → 기존 데이터 조회
→ BEGIN
→ INSERT와 RETURNING으로 새 ID 확인
→ 새 ID로 SELECT
→ 같은 ID의 content만 UPDATE
→ 같은 ID의 행 DELETE
→ 없는 ID의 UPDATE가 0행인지 확인
→ ROLLBACK
→ 기존 행 수와 전체 내용 비교
```

CRUD는 생성(Create), 조회(Read), 수정(Update), 삭제(Delete)를 뜻합니다. SQL에서는 각각 `INSERT`, `SELECT`, `UPDATE`, `DELETE`에 대응합니다. 이 실습에서 Create는 테이블 생성이 아니라 데이터 행 추가입니다.

각 `@step` 구간을 같은 DB 세션에서 순서대로 실행합니다. INSERT 결과를 확인한 뒤 다음 조건의 ID를 맞춰야 하므로 전체 파일을 한 번에 실행하지 않습니다.

## 2. 연결 확인과 시작 데이터 기록

처음의 `DO $guard$ ... $guard$;`는 현재 DB명이 허용된 개인 학습 DB 이름인지 검사합니다. 이후 `SET search_path TO public;`으로 스키마 검색 경로를 설정합니다. 연결 DB를 바꾸는 구문은 아닙니다.

```sql
SELECT id, title, content, category_id
FROM public.knowledge
ORDER BY id;
```

변경 전 ID·제목·본문·분류를 확인합니다. 이 결과는 마지막에 원상 복구를 확인할 기준입니다. S0 상태라면 3행이지만, 현재 데이터가 다르다면 실제 시작 상태를 기준으로 비교합니다.

없는 ID 변경 실험에 앞서 아래 조회가 0행인지도 확인합니다. 현재 파일에는 이 사전 조회가 별도 SQL로 들어 있지 않으므로 실행 전에 직접 확인합니다.

```sql
SELECT id FROM public.knowledge WHERE id = -1;
```

실제로 -1이 존재하면 0행 변경 실험을 진행하지 않습니다.

## 3. BEGIN: 변경을 한 묶음으로 시작

```sql
BEGIN;
```

이후 입력·수정·삭제를 하나의 트랜잭션에서 진행합니다. 같은 세션에서는 아직 커밋하지 않은 변경도 조회할 수 있습니다. 마지막 `ROLLBACK`까지 연결을 유지합니다.

## 4. INSERT와 RETURNING: 생성한 ID 확인

```sql
INSERT INTO public.knowledge (title, content, category_id)
VALUES ('임시 안내', '취소할 연습 데이터입니다.', 1)
RETURNING id, title, content, category_id;
```

열 목록과 VALUES의 값은 순서대로 대응합니다.

| 열 | 입력값 | 역할 |
|---|---|---|
| title | 임시 안내 | 제목 |
| content | 취소할 연습 데이터입니다. | 본문 |
| category_id | 1 | 참조할 분류의 ID |

`id`는 입력 목록에서 제외했으므로 테이블의 IDENTITY 설정에 따라 자동 생성됩니다. `category_id = 1`을 쓰려면 `public.categories`에 id 1이 있어야 합니다.

`RETURNING`은 실제로 입력된 행의 지정한 열을 결과로 돌려줍니다. 실행 결과가 다음과 같다면 새 ID는 6입니다.

| id | title | content | category_id |
|---|---|---|---|
| 6 | 임시 안내 | 취소할 연습 데이터입니다. | 1 |

ID 자동 생성과 다음 SQL에 ID 전달은 별개입니다. 현재의 독립 SQL 문장들은 반환값을 자동으로 기억하지 않으므로, 결과의 숫자를 다음 SELECT·UPDATE·DELETE에 직접 넣습니다. 변수로 전달하는 자동화도 가능하지만 현재 파일은 직접 확인하는 방식입니다.

확인을 위해 INSERT를 다시 실행하면 새 행이 또 추가됩니다. 이미 실행했다면 그때의 반환 결과를 확인합니다.

## 5. SELECT: 새 행만 확인

```sql
SELECT id, title, content, category_id
FROM public.knowledge
WHERE id = 6;
```

방금 생성한 행이 맞는지 확인합니다. 실제 반환 ID가 6이었다면 `임시 안내` 한 행이 나와야 합니다. 다음 UPDATE 전에 대상 ID와 현재 본문을 확인하는 단계입니다.

## 6. UPDATE: 본문만 수정

```sql
UPDATE public.knowledge
SET content = '수정 연습 안내입니다.'
WHERE id = 6
RETURNING id, title, content;
```

`WHERE`가 대상을 정하고 `SET`이 변경할 열과 값을 정합니다. 결과는 수정된 행의 ID·제목·본문입니다. 정상 흐름에서는 한 행이 반환되며 ID·제목·분류·전체 행 수는 그대로이고 본문만 바뀝니다.

0행이라면 해당 ID가 없거나 다른 연결에서 실행했는지 확인합니다. 기본 키로 한 행을 지정했으므로 정상적인 이 쿼리에서 여러 행이 수정될 수는 없습니다.

## 7. DELETE: 새 행만 삭제

```sql
DELETE FROM public.knowledge
WHERE id = 6
RETURNING id, title;
```

같은 ID의 지식 한 행을 삭제하고 삭제된 ID·제목을 반환합니다. `RETURNING`은 삭제가 수행되더라도 삭제 대상 행의 값을 보여줄 수 있습니다. 테이블 자체나 분류 테이블은 삭제하지 않습니다.

이 시점에는 새로 추가한 행이 없어집니다. 하지만 아직 트랜잭션을 확정한 상태는 아닙니다.

## 8. 없는 ID 수정: 0행과 오류 구분

```sql
UPDATE public.knowledge
SET content = '변경되면 안 됨'
WHERE id = -1
RETURNING id;
```

사전 조회에서 id -1이 없음을 확인했다면 수정 대상이 없어서 변경은 0행, RETURNING 결과도 0행입니다. SQL이 정상 처리됐지만 조건에 맞는 데이터가 없는 경우이며 의도적인 문법 오류가 아닙니다.

## 9. ROLLBACK과 최종 확인

```sql
ROLLBACK;

SELECT COUNT(*) AS knowledge_count
FROM public.knowledge;

SELECT id, title, content, category_id
FROM public.knowledge
ORDER BY id;
```

`ROLLBACK`은 BEGIN 이후의 입력·수정·삭제를 모두 취소합니다. 3번은 트랜잭션 안에서 테이블을 생성했으므로 테이블이 사라졌지만, 4번의 `public.knowledge`는 기존 테이블이므로 그대로 남고 이번 데이터 변경만 취소됩니다.

`COUNT(*)`는 열의 NULL 여부와 관계없이 전체 행 수를 셉니다. 이 실습은 취소 후 실제 행 수를 확인하는 것이 목적이므로 `COUNT(*)`를 사용합니다. `MAX(id)`는 가장 큰 ID일 뿐 행 수가 아닙니다.

앞서 작성했던 `COUNT(id)`는 id가 NULL이 아닌 행만 셉니다. 이 테이블에서는 id가 기본 키라 NULL이 없으므로 결과는 같지만, 전체 행 수를 세려는 의도를 직접 드러내도록 SQL과 문서의 예제를 `COUNT(*)`로 맞췄습니다. 중복값은 두 방식 모두 그대로 세며, `COUNT(*)`의 `*`는 모든 열의 값을 결과로 조회한다는 의미가 아닙니다.

행 수만 같다고 원래 내용이 복구됐다고 단정하지 않습니다. 마지막 전체 조회의 ID·제목·본문·분류까지 시작 전 결과와 비교합니다. 단독으로 실습하고 다른 세션의 변경이 없다면 시작 상태와 같아야 합니다.

IDENTITY에 사용된 시퀀스 번호는 ROLLBACK으로 되돌아가지 않습니다. 다음 INSERT가 7 또는 그 이후 번호를 받더라도 정상입니다. 재실행할 때는 이번에 반환된 ID로 세 조건을 다시 맞춥니다.

## 10. 작성 중 잘못됐던 조건과 수정

수정 전에는 새 행 조회·수정·삭제에 다음 조건이 사용됐습니다.

```sql
WHERE id = id
```

이는 새 ID를 변수로 참조하는 표현이 아닙니다. 각 행의 id 열을 자기 자신과 비교합니다. 이 테이블의 id는 NULL이 없는 기본 키이므로 모든 행에서 참입니다. 따라서 전체 조회, 전체 본문 수정, 전체 행 삭제가 발생할 수 있습니다.

현재 파일은 세 곳 모두 다음 조건으로 수정되어 있습니다.

```sql
WHERE id = 6
```

이제 하나의 기본 키 값만 대상으로 삼습니다. 단, 숫자 6이 이번 INSERT에서 반환된 값인지 확인해야 합니다. 파일 내용만으로 실제 반환 ID를 검증할 수는 없습니다.

잘못된 조건으로 실행했어도 같은 트랜잭션이 아직 커밋되지 않았다면 같은 세션에서 `ROLLBACK;`으로 취소합니다. SQL 실행 오류로 트랜잭션이 중단됐을 때도 ROLLBACK을 별도로 실행한 뒤 BEGIN부터 다시 시작합니다. 이미 커밋한 변경은 이후 ROLLBACK으로 되돌릴 수 없습니다.

## 확인 범위

현재 파일의 조회·수정·삭제 조건이 모두 id 6을 사용하는지, RETURNING과 마지막 ROLLBACK 및 전체 조회가 있는지 확인했습니다. 실제 PostgreSQL 실행 결과나 반환 ID, 시작 전후 데이터 일치는 검증하지 않았습니다.
