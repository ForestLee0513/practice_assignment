"""01 · AI Agent vs 고정 RAG/Workflow · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def classify_request(question: str) -> str:
    """질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent. """
    # TODO D29-01-B-01: 질문 성격을 'rag'·'db'·'agent' 중 선택. 규정+상태 복합은 agent.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    q=question.lower()
    has_db=any(t in q for t in ('상태','인덱싱','revision','ready','pending'))
    has_doc=any(t in q for t in ('찾아','내용','설명','근거','검색'))
    if has_db and has_doc:return 'agent'
    if has_db:return 'db'
    return 'rag'

def plan_for_request(question: str) -> dict:
    """처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다."""
    # TODO D29-01-B-02: 처리 전략과 사용할 Tool 목록을 반환. 조건문은 Agent 자체가 아닙니다.
    # 힌트: Tool 선택 계획과 실제 Agent 판단은 다릅니다. 반환하는 strategy/tools 값을 확인하세요.
    mode=classify_request(question)
    tools={'rag':['rag_search'],'db':['lookup_status'],'agent':['rag_search','lookup_status']}[mode]
    return {'strategy':mode,'tools':tools,'decision':'고정 조건에 따른 실습용 계획; 실제 Agent 선택은 06에서 LLM 수행'}

