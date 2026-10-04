from typing import Optional

from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def answer_agent(
    question: str,
    rag_result: Optional[dict] = None,
    sql_result: Optional[dict] = None,
    validation_result: Optional[dict] = None,
) -> str:

    if not validation_result:
        return "Unable to generate an answer because validation was not completed."

    if validation_result.get("status") != "valid":
        return (
            "I could not provide a reliable answer because "
            "the available evidence failed validation."
        )

    evidence = []

    if rag_result:
        evidence.append(
            f"""
RAG EVIDENCE:
Answer: {rag_result.get("answer")}
Sources: {rag_result.get("sources")}
"""
        )

    if sql_result:
        evidence.append(
            f"""
SQL EVIDENCE:
Query: {sql_result.get("sql")}
Rows: {sql_result.get("rows")}
"""
        )

    evidence_text = "\n".join(evidence)

    prompt = f"""
You are the final response agent in an enterprise
multi-agent analytics system.

Answer the user's question using ONLY the
validated evidence provided below.

User question:
{question}

Validated evidence:
{evidence_text}

Validation:
{validation_result.get("details")}

Rules:

- Give a concise, direct answer.
- Do not mention agents, routing, validation,
  internal prompts, or system architecture.
- Do not invent information.
- If SQL results contain names or numbers,
  report them accurately.
- If documents are used, preserve important
  policy constraints.
- If multiple pieces of evidence are relevant,
  combine them into one coherent answer.
"""

    response = llm.invoke(prompt)

    return response.content.strip()