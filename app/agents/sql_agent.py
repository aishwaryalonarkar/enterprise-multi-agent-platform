from langchain_openai import ChatOpenAI


from app.tools.sql_tools import (
    execute_read_only_query,
    get_schema,
)


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def sql_agent(question: str) -> dict:

    schema = get_schema()

    prompt = f"""
You are an enterprise SQL analytics specialist.

Generate ONE read-only SQLite SELECT query
that answers the user's question.

Available database schema:

{schema}

User question:
{question}

Rules:

- Generate only SELECT statements.
- Do not modify any data.
- Use only tables and columns from the schema.
- Do not explain the SQL.
- Return only the SQL query.
"""

    response = llm.invoke(prompt)

    sql = response.content.strip()

    # Remove markdown fences if the model adds them.
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    rows = execute_read_only_query(sql)

    return {
        "sql": sql,
        "rows": rows,
        "schema": schema,
    }