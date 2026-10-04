from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DOCUMENT_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"


def build_vector_store():

    documents = []

    for file_path in DOCUMENT_DIR.glob("*.md"):

        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name
                },
            )
        )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="enterprise_documents",
    )

    print(f"Indexed {len(documents)} documents.")
    print(f"Vector store: {CHROMA_DIR}")


if __name__ == "__main__":
    build_vector_store()