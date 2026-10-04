import time
import uuid
from typing import Any, Dict, Optional

from langgraph.graph import END, START, StateGraph

from app.graph.state import AgentState
from app.agents.supervisor import supervisor_agent
from app.agents.rag_agent import rag_agent
from app.agents.sql_agent import sql_agent
from app.agents.validator import validator_agent
from app.agents.answer_agent import answer_agent


def create_trace_event(
    name: str,
    start_time: float,
    status: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create one immutable trace event.

    Each node returns its own event. LangGraph merges
    parallel trace events using the reducer defined
    in AgentState.
    """

    return {
        "name": name,
        "duration_seconds": round(
            time.perf_counter() - start_time,
            4,
        ),
        "status": status,
        "metadata": metadata or {},
    }


def supervisor_node(state: AgentState) -> AgentState:

    start_time = time.perf_counter()

    try:
        decision = supervisor_agent(state["question"])

        event = create_trace_event(
            name="supervisor",
            start_time=start_time,
            metadata={
                "route": decision.route,
                "reasoning": decision.reasoning,
            },
        )

        return {
            "route": decision.route,
            "trace": [event],
        }

    except Exception as exc:

        event = create_trace_event(
            name="supervisor",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": [event],
        }


def rag_node(state: AgentState) -> AgentState:

    start_time = time.perf_counter()

    try:
        result = rag_agent(state["question"])

        event = create_trace_event(
            name="rag",
            start_time=start_time,
            metadata={
                "sources": result.get("sources", []),
            },
        )

        return {
            "rag_result": result,
            "trace": [event],
        }

    except Exception as exc:

        event = create_trace_event(
            name="rag",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": [event],
        }


def sql_node(state: AgentState) -> AgentState:

    start_time = time.perf_counter()

    try:
        result = sql_agent(state["question"])

        event = create_trace_event(
            name="sql",
            start_time=start_time,
            metadata={
                "row_count": len(result.get("rows", [])),
                "sql": result.get("sql"),
            },
        )

        return {
            "sql_result": result,
            "trace": [event],
        }

    except Exception as exc:

        event = create_trace_event(
            name="sql",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": [event],
        }


def validator_node(state: AgentState) -> AgentState:

    start_time = time.perf_counter()

    try:
        result = validator_agent(
            question=state["question"],
            rag_result=state.get("rag_result"),
            sql_result=state.get("sql_result"),
        )

        event = create_trace_event(
            name="validator",
            start_time=start_time,
            metadata={
                "validation_status": result.get("status"),
            },
        )

        return {
            "validation_result": result,
            "trace": [event],
        }

    except Exception as exc:

        event = create_trace_event(
            name="validator",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": [event],
        }


def answer_node(state: AgentState) -> AgentState:

    start_time = time.perf_counter()

    try:
        final_answer = answer_agent(
            question=state["question"],
            rag_result=state.get("rag_result"),
            sql_result=state.get("sql_result"),
            validation_result=state.get("validation_result"),
        )

        event = create_trace_event(
            name="answer",
            start_time=start_time,
        )

        return {
            "final_answer": final_answer,
            "trace": [event],
        }

    except Exception as exc:

        event = create_trace_event(
            name="answer",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": [event],
        }


def route_from_supervisor(state: AgentState):

    route = state["route"]

    if route == "rag":
        return ["rag"]

    if route == "sql":
        return ["sql"]

    if route == "both":
        return ["rag", "sql"]

    raise ValueError(f"Unknown route: {route}")


def build_workflow():

    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("sql", sql_node)
    graph.add_node("validator", validator_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "rag": "rag",
            "sql": "sql",
        },
    )

    graph.add_edge("rag", "validator")
    graph.add_edge("sql", "validator")

    graph.add_edge("validator", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


workflow = build_workflow()


def run_workflow(question: str):

    state = {
        "question": question,
        "trace_id": str(uuid.uuid4()),
        "trace": [],
    }

    return workflow.invoke(state)