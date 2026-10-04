from operator import add
from typing import Any, Dict, List, Literal

from typing_extensions import Annotated, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    route: Literal["rag", "sql", "both"]

    rag_result: Dict[str, Any]
    sql_result: Dict[str, Any]
    validation_result: Dict[str, Any]

    final_answer: str

    trace_id: str
    trace: Annotated[List[Dict[str, Any]], add]