"""Query Rewrite: 원문 질문 보존, 모호 질문은 확인 요청, LLM 오류는 숨기지 않습니다."""
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from coursekit.fixtures import rewrite_fixture

# Rewrite 클래스 (모델 설정, 상태, 검색 질문, 사유)
class RewriteResult(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    status: Literal['ready','clarification_required']
    search_query: str=Field(max_length=800)
    reason: str=Field(max_length=200)

# 프롬프트에 사용할 Context
RULES=('당신은 검색 질문 Rewrite 구성요소입니다. 마지막 질문을 검색 가능한 독립 질문으로 바꾸세요. '
       'History에서 명확한 사실만 복원하고 조건·부정·날짜를 추측하지 마세요. '
       '대상이 불분명하면 status=clarification_required, search_query는 빈 문자열로 반환하세요. '
       '그렇지 않으면 status=ready, search_query에 독립 질문을 쓰세요.')

# rewrite chain을 만들기 위한 함수
# 정의된 모델이 없으면 기존에 완성했던 create_chat_model()을 통해 기본 모델 불러옴
# 정의된 모델이 있다면 해당 모델에 응답 요청 후 내용 반환
# prompt 생성 후 model.with_structured_output을 실행해서 JSON 등으로 규격화 된 응답 생성 후 반환
def make_rewrite_chain(model=None):
    from langchain_core.prompts import ChatPromptTemplate
    from coursekit.llm import create_chat_model
    model=create_chat_model() if model is None else model
    prompt=ChatPromptTemplate.from_messages([('system',RULES),('human','History:\n{history}\n\n최종 질문: {original_question}')])
    return prompt | model.with_structured_output(RewriteResult,method='json_schema',strict=True)


def rewrite_query(original_question,history,*,offline=False,chain=None):
    # 원본 문자열에서 앞/뒤 문자 공백 제거
    if not original_question.strip():raise ValueError('질문은 비어 있을 수 없습니다.')
    # 오프라인 상태일 경우
    if offline:
        # 고정된 예제 반환
        search=rewrite_fixture(original_question,history)
        # invoke 후 반환 받은 결과물을 기반으로 RewriteResult 클래스 치환
        return RewriteResult(status='ready',search_query=search,reason='교육용 고정 Rewrite') if search else RewriteResult(status='clarification_required',search_query='',reason='대화에서 대상을 확인할 수 없습니다.')
    # rewrite langchain 반환 단, 이미 파라미터로 받은 chain이 있다면 해당 chain사용
    chain=make_rewrite_chain() if chain is None else chain
    # 응답받은 rewrite langchain을 invoke로 동기 실행
    response=chain.invoke({'original_question':original_question,'history':str(history)})
    # RewriteResult 인스턴스가 아닌 경우 LLM 응답 반환 미일치 처리
    if not isinstance(response,RewriteResult):raise TypeError('LLM Structured Output 타입 불일치')
    # status가 ready 이면서 검색 질문이 공백인 경우 예외 처리
    if response.status=='ready' and not response.search_query.strip():raise ValueError('ready인데 검색 질문이 비었습니다.')
    # 확인 요청 상태인데 검색 질문이 있는 경우에 대한 예외처리
    if response.status=='clarification_required' and response.search_query:raise ValueError('확인 요청에는 검색 질문을 생성하지 않습니다.')
    # 예외처리 성공 시 요청 반환
    return response
