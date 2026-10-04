from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    route: Literal["rag", "sql", "both"] = Field(
        description=(
            "Choose exactly one route: "
            "rag for questions answered by enterprise documentation, "
            "sql for questions requiring structured database records, "
            "or both only when the question explicitly requires "
            "both documentation and database information."
        )
    )

    reasoning: str


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


router = llm.with_structured_output(RouteDecision)


def supervisor_agent(question: str) -> RouteDecision:

    prompt = f"""
You are the routing supervisor for an enterprise
multi-agent analytics system.

Your ONLY job is to decide which specialist agent
should answer the user's question.

AVAILABLE AGENTS
----------------

RAG:
Use RAG when the answer comes from enterprise
documentation, policies, procedures, rules,
guidelines, or knowledge-base content.

SQL:
Use SQL when the answer requires querying structured
enterprise records such as customers, transactions,
support tickets, counts, amounts, dates, or statuses.

BOTH:
Use BOTH only when the question genuinely requires
information from BOTH enterprise documentation AND
structured database records.

IMPORTANT ROUTING RULES
-----------------------

1. Policy, procedure, rule, eligibility, processing-time,
   or "what should happen" questions are RAG questions
   when the answer can be found in documentation.

2. A question mentioning a customer does NOT automatically
   require SQL.

3. A question mentioning payments does NOT automatically
   require SQL.

4. If the question asks what company policy says should
   happen, use RAG.

5. If the question asks for specific customer records,
   transaction records, counts, totals, dates, or statuses,
   use SQL.

6. Use BOTH only when BOTH types of information are needed
   to answer the question.

EXAMPLES
--------

Question:
"What is the refund eligibility window?"

Route:
rag

Question:
"How long are standard refund requests normally processed?"

Route:
rag

Question:
"What should happen when a customer has repeated
payment failures?"

Route:
rag

Question:
"How many transactions were refunded?"

Route:
sql

Question:
"How many customers are currently active?"

Route:
sql

Question:
"Which customers have failed payments and open support tickets?"

Route:
sql

Question:
"Which customers have refund-related support tickets
and what does the refund policy say about processing time?"

Route:
both

USER QUESTION
-------------

{question}

Return the best route and a short explanation.
"""

    return router.invoke(prompt)