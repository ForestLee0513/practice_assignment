"""경계값·오류/권한 정책: Advanced · Day29."""

def summarize_tool_messages(messages: list) -> dict:
    """Model 요청 수와 실제 ToolMessage 수를 별도로 집계."""
    # 해설 D29-06-A-03: create_agent에 실제 rag_search와 lookup_status 두 도구를 등록합니다.
    # 검수 기준: 모델의 Tool 선택은 비결정적이므로 요청 건수와 실제 ToolMessage를 따로 셉니다.
    from coursekit.contracts import count_tool_calls
    return count_tool_calls(messages)

def final_text(messages: list) -> str:
    """최종 AIMessage에서 텍스트만 추출합니다."""
    from langchain_core.messages import AIMessage

    # 마지막 메시지부터 역순으로 검사
    for m in reversed(messages):
        # ToolMessage 등은 제외
        if not isinstance(m, AIMessage):
            continue
        # Tool 호출 요청 메시지는 제외
        if m.tool_calls:
            continue
        # 문자열 / Content Block 리스트 모두 처리
        text = str(m.text).strip()

        if text:
            return text
        raise ValueError(
            "최종 AIMessage에 추출 가능한 텍스트가 없습니다."
        )

    raise ValueError("최종 AIMessage가 없습니다.")