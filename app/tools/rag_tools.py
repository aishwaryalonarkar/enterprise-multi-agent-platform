from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENT_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"


_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# def build_vector_store() -> Chroma:
#     documents = []

#     for file_path in DOCUMENT_DIR.glob("*.md"):
#         text = file_path.read_text(encoding="utf-8")

#         documents.append(
#             Document(
#                 page_content=text,
#                 metadata={
#                     "source": file_path.name
#                 },
#             )
#         )

#     vector_store = Chroma.from_documents(
#         documents=documents,
#         embedding=_embeddings,
#         persist_directory=str(CHROMA_DIR),
#         collection_name="enterprise_documents",
#     )

#     return vector_store


def get_vector_store() -> Chroma:
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=_embeddings,
        collection_name="enterprise_documents",
    )

def retrieve_documents(
    question: str,
    k: int = 3,
) -> list[Document]:

    vector_store = get_vector_store()
    
    results = vector_store.similarity_search(
        question,
        k=k,
    )

    return results