import os
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    TextLoader,
)

DOCS_DIR = Path("repo-to-index")
CHROMA_PATH = Path("data/chroma_db")

print(f"Scanning {DOCS_DIR.resolve()} for documents...")

docs = []
for file_path in DOCS_DIR.rglob("*"):
    if not file_path.is_file():
        continue

    try:
        if file_path.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            loader = UnstructuredWordDocumentLoader(str(file_path))
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(str(file_path))
        else:
            loader = TextLoader(str(file_path), encoding="utf-8")

        docs.extend(loader.load())
        print(f"Loaded: {file_path.name}")
    except Exception as e:
        print(f"Skipped {file_path.name}: {e}")

if not docs:
    print("No documents found — nothing to index!")
    exit()

print(f"Loaded {len(docs)} documents")

# Smart chunking
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

print("Loading embeddings model...")
os.makedirs("models", exist_ok=True)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="models"
)

print("Indexing into Chroma...")
os.makedirs(CHROMA_PATH, exist_ok=True)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(CHROMA_PATH)
)

print(f"Done! Vector DB saved to {CHROMA_PATH} — {len(chunks)} chunks ready for querying.")
