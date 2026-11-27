"""03 · @tool·Pydantic·JSON Schema · 기본필수 · 수강생 TODO.

DB: 기존 report_agent_lab / 반드시 SELECT. 실제 Tool은 --live에서 실행됩니다.
"""

def validate_id(report_id: int) -> int:
    """실제 reports.report_id인 양의 정수만 허용합니다."""
    # TODO D29-03-B-01: 실제 reports.report_id인 양의 정수만 허용합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    from coursekit.contracts import report_id_from
    return report_id_from(report_id)


def register_status_tool():
    """@tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다."""
    # TODO D29-03-B-02: @tool을 사용해 실제 DB 상태 조회 함수를 등록하고 반환합니다.
    # 힌트: @tool 함수의 docstring, report_id:int, args_schema를 읽어보세요.
    from langchain.tools import tool
    import json
    from coursekit.db import fetch_report_status
    @tool('lookup_status')
    def lookup_status(report_id:int)->str:
        """기존 보고서 report_id의 인덱싱 상태를 읽기 전용 조회합니다. task_id가 아닙니다."""
        return json.dumps(fetch_report_status(validate_id(report_id)),ensure_ascii=False,default=str)

    return lookup_status
