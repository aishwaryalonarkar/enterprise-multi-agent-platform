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

def add_trace_event(
    state: AgentState,
    name: str,
    start_time: float,
    status: str = "success",
    metadata: Optional[Dict[str, Any]] = None,
) -> dict:
    """Create a trace event for an agent execution."""

    duration = time.perf_counter() - start_time

    event = {
        "name": name,
        "duration_seconds": round(duration, 4),
        "status": status,
        "metadata": metadata or {},
    }

    existing_trace = state.get("trace", {})

    events = existing_trace.get("events", [])
    events.append(event)

    return {
        "trace_id": state["trace_id"],
        "events": events,
    }


def supervisor_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()

    try:
        decision = supervisor_agent(state["question"])

        trace = add_trace_event(
            state=state,
            name="supervisor",
            start_time=start_time,
            metadata={
                "route": decision.route,
            },
        )

        return {
            "route": decision.route,
            "trace": trace,
        }

    except Exception as exc:
        trace = add_trace_event(
            state=state,
            name="supervisor",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": trace,
        }


def rag_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()

    try:
        result = rag_agent(state["question"])

        trace = add_trace_event(
            state=state,
            name="rag",
            start_time=start_time,
            metadata={
                "sources": result.get("sources", []),
            },
        )

        return {
            "rag_result": result,
            "trace": trace,
        }

    except Exception as exc:
        trace = add_trace_event(
            state=state,
            name="rag",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": trace,
        }


def sql_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()

    try:
        result = sql_agent(state["question"])

        trace = add_trace_event(
            state=state,
            name="sql",
            start_time=start_time,
            metadata={
                "row_count": len(result.get("rows", [])),
                "sql": result.get("sql"),
            },
        )

        return {
            "sql_result": result,
            "trace": trace,
        }

    except Exception as exc:
        trace = add_trace_event(
            state=state,
            name="sql",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": trace,
        }


def validator_node(state: AgentState) -> AgentState:
    start_time = time.perf_counter()

    try:
        result = validator_agent(
            question=state["question"],
            rag_result=state.get("rag_result"),
            sql_result=state.get("sql_result"),
        )

        trace = add_trace_event(
            state=state,
            name="validator",
            start_time=start_time,
            metadata={
                "validation_status": result.get("status"),
            },
        )

        return {
            "validation_result": result,
            "final_answer": result["details"],
            "trace": trace,
        }

    except Exception as exc:
        trace = add_trace_event(
            state=state,
            name="validator",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": trace,
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

        trace = add_trace_event(
            state=state,
            name="answer",
            start_time=start_time,
        )

        return {
            "final_answer": final_answer,
            "trace": trace,
        }

    except Exception as exc:
        trace = add_trace_event(
            state=state,
            name="answer",
            start_time=start_time,
            status="error",
            metadata={
                "error": str(exc),
            },
        )

        return {
            "trace": trace,
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
        "trace": {
            "events": [],
        },
    }

    return workflow.invoke(state)