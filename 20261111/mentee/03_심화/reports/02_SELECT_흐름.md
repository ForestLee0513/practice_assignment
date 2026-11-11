# 심화 02. SELECT·조건·정렬

아래 결과는 제공된 초기 데이터(S0)와 실습 SQL 기준 예상값이며 실제 DB 실행 결과는 아닙니다.

## 실행 전 알아둘 점

- 현재 연결한 DB가 개인 학습 DB인지 확인합니다. `SELECT current_database()`는 현재 DB를 조회하며 다른 DB로 연결을 바꾸지는 않습니다.
- `--` 뒤는 주석입니다. `@step`과 `TODO`도 주석 안에서는 실행되지 않습니다. 반면 `__TODO_TABLE__`처럼 SQL 본문에 남은 토큰은 실제 이름으로 바꿔야 합니다.
- 한 `@step` 구간씩 선택 실행합니다.

대상: `queries/02_select.sql`

먼저 준비 실습에서 `public.categories`와 `public.knowledge` 및 S0 데이터가 생성되어 있어야 합니다. 1번의 연결 확인만으로 이 테이블들이 만들어지지는 않습니다.

### 1. 전체 목록

현재 파일의 `__TODO_TABLE__`을 완성하면 다음 형태입니다. 이번 수정에서는 2번 SQL 파일의 빈칸은 변경하지 않았습니다.

```sql
SELECT id, title, category_id
FROM public.knowledge
ORDER BY id;
```

이 쿼리를 이해하는 논리적 순서는 `FROM`으로 대상 표 선택 → `SELECT`로 결과 열 선택 → `ORDER BY`로 정렬입니다. 실제 서버 내부의 물리적 처리 순서를 고정한다는 의미는 아닙니다. `ORDER BY id`는 기본적으로 오름차순이며 정렬을 생략하면 표시 순서는 보장되지 않습니다.

S0 예상 결과:

| id | title | category_id |
|---|---|---|
| 1 | 실습 파일 보관 | 1 |
| 2 | 서버 실행 | 2 |
| 3 | 질문 작성 | 1 |

### 2. 한 건 조회

```sql
SELECT id, title, content FROM public.knowledge
WHERE id = 2;
```

`WHERE`가 조건에 맞는 행을 남깁니다. S0에서는 `서버 실행` 한 건입니다. 실제 데이터가 달라졌다면 먼저 목록에서 ID를 확인합니다.

### 3. 분류별 조회

```sql
SELECT id, title FROM public.knowledge
WHERE category_id = 1
ORDER BY id;
```

지식 자신의 번호인 `id`와 소속 분류 번호인 `category_id`는 역할이 다릅니다. 이 조건은 분류 1에 속한 지식을 찾으며 S0에서는 id 1, 3이 나옵니다.

### 4. 없는 데이터 조회

```sql
SELECT id, title FROM public.knowledge WHERE id = -1;
```

해당 ID가 없으면 결과는 0행입니다. 문법 오류나 연결 실패와는 다릅니다.

### 5. 여러 조건과 패턴 검색

```sql
SELECT id, title FROM public.knowledge
WHERE category_id = 1 AND title LIKE '%실습%'
ORDER BY id
LIMIT 1;
```

논리적 흐름은 **표 선택 → 두 조건을 모두 만족하는 행 필터링 → 결과 열 선택 → ID 정렬 → 최대 한 행 반환**입니다. `%`는 0개 이상의 문자이므로 `%실습%`은 앞뒤 어느 위치든 `실습`이 포함된 제목을 찾습니다. S0에서는 id 1입니다.

실습의 일반적인 문자열 비교에서 `LIKE`는 대소문자를 구분하고 `ILIKE`는 구분하지 않습니다. 한글 `실습` 검색에서는 영문 대소문자 차이를 관찰할 수 없습니다. 패턴 검색은 문장의 의미나 유사도를 판단하는 검색은 아닙니다.

### 6. NULL과 빈 문자열 비교

```sql
SELECT label, label IS NULL AS is_missing
FROM (VALUES (NULL::text), (''::text), ('안내')) AS s(label)
WHERE label IS NULL;
```

`VALUES`는 세 행으로 구성된 임시 조회 데이터를 만듭니다. 실제 테이블을 생성하지 않습니다. `s`는 이 데이터의 별칭, `label`은 열 이름입니다. `::text`는 값을 text 자료형으로 명시하는 형변환이며 NULL을 다른 문자열로 채우는 명령이 아닙니다.

- `NULL`: 값이 없거나 알 수 없음.
- `''`: 값은 있지만 길이가 0인 문자열.
- `'안내'`: 문자열 값.

`WHERE label IS NULL`이 첫 행만 남기고 `label IS NULL AS is_missing`이 결과에 true/false 판단 열을 추가합니다. 결과는 NULL과 true 한 행입니다. NULL을 검사할 때는 `= NULL` 대신 `IS NULL`을 사용합니다.

### 7. 동점 정렬

```sql
SELECT id, score
FROM (VALUES (3,10), (1,10), (2,5)) AS s(id,score)
ORDER BY score DESC, id;
```

점수를 내림차순으로 정렬하고 점수가 같으면 ID 오름차순을 적용합니다. 따라서 ID 순서는 1 → 3 → 2입니다. 여러 정렬 기준은 왼쪽부터 우선 적용합니다.
