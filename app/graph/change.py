from typing import Any, Literal
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    question: str

    route: Literal["rag", "sql", "both"]

    rag_result: dict[str, Any]
    sql_result: dict[str, Any]

    validation_result: dict[str, Any]

    final_answer: str

    trace_id: str