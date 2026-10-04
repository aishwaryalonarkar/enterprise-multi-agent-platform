from typing import Optional

from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def validator_agent(
    question: str,
    rag_result: Optional[dict] = None,
    sql_result: Optional[dict] = None,
) -> dict:

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
You are the validation agent in an enterprise
multi-agent analytics system.

Your job is to determine whether the COMBINED evidence
is sufficient to answer the user's question accurately.

Important:

Different agents specialize in different types of evidence.

RAG evidence comes from enterprise documentation,
policies, procedures, and knowledge-base documents.

SQL evidence comes from structured enterprise data
such as customers, transactions, and support tickets.

These sources do NOT need to contain the same information.

For example:

- RAG may say that customer-specific records are not
  contained in enterprise documents.
- SQL may provide the actual customer records.

That is NOT a contradiction. The two sources can complement
each other.

User question:
{question}

Evidence:
{evidence_text}

Validation rules:

1. Determine whether the combined evidence answers
   the user's question.

2. Treat statements about the LIMITATIONS of a source
   as valid evidence, not contradictions.

3. If SQL provides specific database results and RAG
   only provides general policy information, the SQL
   results remain valid for database questions.

4. Mark INVALID only when:
   - required evidence is missing,
   - evidence directly contradicts itself,
   - the SQL result is clearly unusable,
   - or the evidence does not actually answer the question.

5. Do not require every agent to independently answer
   the entire question.

Return:

VALID

or

INVALID

Then explain your reasoning.
"""

    response = llm.invoke(prompt)
    validation_text = response.content.strip()

    return {
        "status": (
            "valid"
            if validation_text.upper().startswith("VALID")
            else "invalid"
        ),
        "details": validation_text,
    }