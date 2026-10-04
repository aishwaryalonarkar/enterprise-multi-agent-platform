from langchain_openai import ChatOpenAI

from app.tools.rag_tools import retrieve_documents


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)


def rag_agent(question: str) -> dict:

    documents = retrieve_documents(question)

    if not documents:
        return {
            "answer": "No relevant documents were found.",
            "sources": [],
            "context": "",
        }

    context_parts = []

    for document in documents:
        source = document.metadata.get(
            "source",
            "unknown",
        )

        context_parts.append(
            f"SOURCE: {source}\n"
            f"{document.page_content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are the enterprise RAG specialist.

Answer the user's question using ONLY the
provided enterprise documents.

If the documents do not contain enough information,
say that clearly.

User question:
{question}

Enterprise documents:
{context}

Return a concise, factual answer.
"""

    response = llm.invoke(prompt)

    sources = [
        document.metadata.get("source", "unknown")
        for document in documents
    ]

    return {
        "answer": response.content,
        "sources": list(dict.fromkeys(sources)),
        "context": context,
    }