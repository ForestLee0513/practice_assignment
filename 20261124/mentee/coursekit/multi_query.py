"""Multi-query 후보 통합: chunk_id 동일성·원 출처·발견 질문을 보존."""
from coursekit.documents import valid_document


def unique_queries(base,additional,max_queries=3):
    #최대 쿼리에 대한 예외 처리 1~4까지만 입력 받음
    if type(max_queries) is not int or not 1<=max_queries<=4:raise ValueError('max_queries 1~4')
    # 결과를 저장할 list
    result=[]
    # 쿼리순회
    for q in [base,*additional]:
        # 쿼리가 문자열이 아닌 경우 예외 처리
        if not isinstance(q,str):raise ValueError('질문은 문자열이어야 합니다.')
        # 쿼리의 앞 뒤 공백 제거
        q=q.strip()
        # result 안에 쿼리가 없을 경우에만 result에 추가
        if q and q not in result:result.append(q)
        # result의 길이가 max_queries 보다 같거나 높을 경우 해당 반복문 탈출
        if len(result)>=max_queries:break
    # 결과 반환 (list 형식)
    return result


def merge_found(results):
    """[(query, [Document...]), ...] -> stable unique Documents with found_by_query list."""
    # 병합된 문서 dict 
    merged={}
    # 결과를 query, docs를 빼와서 순차 반복
    for query,docs in results:
        # 문서 순차 반복
        for doc in docs:
            # 문서 검증
            valid_document(doc)
            # 문서의 메타데이터 중 chunk_id를 키로 지정
            key=doc.metadata['chunk_id']
            #  merged dict 안에 없는 키 일때만 추가
            if key not in merged:
                # 문서의 내용을 model_copy라는 속성이 있을 때 deep copy, 그 외는 shallow copy 처리
                clone=doc.model_copy(deep=True) if hasattr(doc,'model_copy') else doc.copy(deep=True)
                # 복제된 문서의 메타데이터 중 found_by_query를 실제 쿼리 요청 값으로 지정
                clone.metadata['found_by_query']=[query]
                # merged dict에 추가
                merged[key]=clone
            # 쿼리가 문서 중 metadata의 found_by_query의 내용이 없을 경우 예외 처리 
            elif query not in merged[key].metadata['found_by_query']:
                # 같은 ID의 본문이 달라진 경우 데이터 일관성 위반을 숨기지 않습니다.
                if merged[key].page_content!=doc.page_content:
                    raise ValueError(f'같은 chunk_id의 본문 불일치: {key}')
                merged[key].metadata['found_by_query'].append(query)
    # 병합된 dict를 value만 추출 후 list로 변환
    return list(merged.values())


def search_multiple(queries, search_fn,*,category,role='learner',candidate_k=5,max_queries=3,partial_ok=False):
    unique=unique_queries(queries[0],queries[1:],max_queries=max_queries)
    results,errors=[],[]
    for query in unique:
        try:
            docs=search_fn(query,category,candidate_k,role)
        except Exception as exc:
            errors.append({'query':query,'error_type':type(exc).__name__})
            if not partial_ok:raise
            continue
        results.append((query,docs))
    return {'queries':unique,'documents':merge_found(results),
            'errors':errors,'query_count':len(unique),'completed_count':len(results)}


# LLM Multi-query 확장: 각 쿼리 후보를 모델에서 생성할 수 있지만 정답/품질은 보장하지 않습니다.
from pydantic import BaseModel, ConfigDict, Field

class MultiQueryPlan(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    additional_queries:list[str]=Field(max_length=2)

def make_multiquery_chain(model=None):
    from langchain_core.prompts import ChatPromptTemplate
    from coursekit.llm import create_chat_model
    model=create_chat_model() if model is None else model
    prompt=ChatPromptTemplate.from_messages([
        ('system','검색 품질 향상을 위해 원 질문의 의미를 유지하는 검색 표현을 최대 2개 생성하세요. '
                  '날짜·부정·권한·문서 조건을 임의로 만들지 마세요. JSON 스키마를 지키세요.'),
        ('human','검색 질문: {query}')
    ])
    return prompt|model.with_structured_output(MultiQueryPlan,method='json_schema',strict=True)

def generate_queries_live(base,chain=None):
    chain=make_multiquery_chain() if chain is None else chain
    plan=chain.invoke({'query':base})
    if not isinstance(plan,MultiQueryPlan):raise TypeError('MultiQueryPlan Structured Output 필요')
    # 질문이 너무 길거나 비어 있으면 별도 검색하지 않습니다. 
    return [q.strip() for q in plan.additional_queries if isinstance(q,str) and q.strip() and len(q)<=800]
