# 응용 07. 트랜잭션과 인덱스 SQL 흐름

대상: `sql/07_transaction_index.sql`. 현재 ROLLBACK, COMMIT, id 3을 수정하는 두 번째 UPDATE가 작성되어 있습니다. 아래는 파일 기준 설명이며 실제 DB 실행 결과는 아닙니다.

## 1. 시작 본문 확인

연결 DB 검사와 검색 경로 설정 후 id 2의 본문을 조회해 기록합니다. id 1·2·3이 실제로 있는 상태에서 실습합니다. 변경 대상이 없으면 UPDATE는 오류 대신 0행이 될 수 있습니다.

## 2. 변경을 취소하는 흐름

```sql
BEGIN;
UPDATE public.knowledge
SET content = '취소할 임시 안내입니다.'
WHERE id = 2
RETURNING id, content;
ROLLBACK;
SELECT id, content FROM public.knowledge WHERE id = 2;
```

UPDATE의 RETURNING에서는 임시 본문이 보이지만 마지막 조회에서는 시작 본문으로 돌아와야 합니다. ROLLBACK은 해당 BEGIN 이후의 변경을 취소합니다.

## 3. 변경을 확정하는 흐름

```sql
BEGIN;
UPDATE public.knowledge
SET content = '실행 전에 가상환경을 확인합니다.'
WHERE id = 2
RETURNING id, content;
COMMIT;
```

COMMIT은 현재 트랜잭션의 변경을 확정합니다. 이후 새로운 트랜잭션에서 ROLLBACK해도 이 변경은 취소되지 않습니다. 이 단계 뒤의 상태를 교안에서는 S1이라고 부릅니다.

새 연결을 직접 열고 같은 DB인지 확인한 다음 본문을 조회합니다.

```sql
SELECT current_database() AS database_name;
SELECT id, content FROM public.knowledge WHERE id = 2;
```

`@step ... reconnect=true`는 주석이므로 일반 SQL 실행만으로 연결이 바뀌지는 않습니다. 새 연결에서도 확정한 본문이 보여야 합니다.

## 4. 두 변경을 한 묶음으로 취소

```sql
BEGIN;
UPDATE public.knowledge SET content = '묶음 연습 1' WHERE id = 1;
UPDATE public.knowledge SET content = '묶음 연습 2' WHERE id = 3
RETURNING id, content;
SELECT id, content FROM public.knowledge WHERE id IN (1,3) ORDER BY id;
ROLLBACK;
```

두 UPDATE는 같은 BEGIN에 속합니다. SELECT에서 두 임시 본문을 확인하고 ROLLBACK하면 둘 다 복구됩니다. RETURNING은 바로 앞의 두 번째 UPDATE에만 붙어 있으므로 첫 번째 UPDATE의 행까지 반환하지는 않습니다. `IN (1,3)`은 두 ID 중 하나인 행을 선택합니다.

복구 상태를 바로 확인하려면 ROLLBACK 뒤 같은 SELECT를 다시 실행합니다. 파일의 마지막 전체 조회에서도 확인할 수 있습니다. 앞서 별도 트랜잭션에서 커밋한 id 2의 본문은 유지됩니다.

## 5. 기존 인덱스 확인

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'knowledge'
ORDER BY indexname;
```

시스템 뷰에서 인덱스 이름과 정의를 확인합니다. 기본 키의 인덱스가 있다고 category_id용 인덱스도 있는 것은 아닙니다. 같은 이름이 있으면 정의를 확인한 후 다음 CREATE 구간을 건너뜁니다.

## 6. 인덱스 생성 전 실행계획

```sql
EXPLAIN SELECT id, title FROM public.knowledge WHERE category_id = 1;
```

EXPLAIN은 서버가 선택한 실행계획과 예상 비용·행 수를 보여줍니다. 이 형태는 조회 자체를 실행해 실제 시간을 측정하지 않습니다. `cost`는 밀리초가 아닙니다. 이미 인덱스가 있다면 이 결과를 엄밀한 인덱스 생성 전 결과라고 부를 수 없습니다.

## 7. 인덱스 생성

```sql
CREATE INDEX idx_knowledge_category_id ON public.knowledge(category_id);
```

분류 번호로 찾을 때 활용할 수 있는 인덱스를 만듭니다. 실제 사용 여부는 서버가 데이터 크기·분포·비용을 보고 선택합니다. 작은 실습 표에서는 전체를 읽는 Seq Scan이 정상적인 선택일 수 있습니다.

이 구간은 앞의 ROLLBACK 뒤에 있습니다. 파일은 자동 커밋 환경을 전제로 하며, 수동 트랜잭션 모드라면 인덱스 생성도 확정 여부를 확인해야 합니다.

## 8. 실제 조회를 포함한 계획 확인

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title FROM public.knowledge WHERE category_id = 1;
```

ANALYZE는 여기의 SELECT를 실제 실행해 실제 행 수·시간 등을 보여주고, BUFFERS는 버퍼 접근 통계를 추가합니다. 생성 전 쿼리는 추정 계획만 보므로 두 출력을 단순한 실제 시간 전후 비교로 해석하지 않습니다. 한 번의 짧은 실행만으로 성능 향상을 단정하지도 않습니다.

## 9. 최종 상태

- id 2에는 커밋한 본문이 남습니다.
- id 1·3의 묶음 변경은 취소됩니다.
- 지식의 행 수는 변하지 않습니다.
- category_id 인덱스 정의를 확인할 수 있어야 합니다.

전체 흐름: **한 변경 취소 → 다른 변경 확정 → 새 연결 확인 → 두 변경 동시 취소 → 인덱스 확인·생성 → 실행계획 확인**.
