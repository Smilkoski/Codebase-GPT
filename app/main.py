from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import sys
from pathlib import Path
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import create_engine

load_dotenv()

app = FastAPI(title="Codebase / Document GPT")
app.mount("/static", StaticFiles(directory="templates"), name="static")

os.makedirs("data/chroma_db", exist_ok=True)

os.makedirs("models", exist_ok=True)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="models"
)
os.makedirs("data/chroma_db", exist_ok=True)
vectorstore = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# LLM
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

# Postgres
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://root:root@postgres:5432/codebase_gpt")
engine = create_engine(POSTGRES_URL)


class Query(BaseModel):
    question: str
    session_id: str = "default"


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("app/templates/index.html") as f:
        return f.read()


@app.post("/query")
async def query(q: Query):
    # Load persistent chat history from Postgres
    history = SQLChatMessageHistory(session_id=q.session_id, connection=engine)

    # convert history to LangChain messages
    chat_history_messages = [
        HumanMessage(content=m.content) if m.type == "human" else AIMessage(content=m.content)
        for m in history.messages
    ]

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
            "chat_history": lambda x: chat_history_messages
        }
        | ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Use the context and conversation history to answer."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        | llm
        | StrOutputParser()
    )

    try:
        answer = chain.invoke(q.question)

        # Save to Postgres so next call sees it
        history.add_user_message(q.question)
        history.add_ai_message(answer)

        # Get sources
        docs = retriever.invoke(q.question)
        sources = list({Path(doc.metadata.get("source", "")).name for doc in docs})

        return {"answer": answer, "sources": sources}

    except Exception as e:
        print(f'Exception occurred: {e}')
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    os.makedirs("repo-to-index", exist_ok=True)

    for file in files:
        path = Path("repo-to-index") / file.filename
        with open(path, "wb") as f:
            f.write(await file.read())
        print(f"Saved: {file.filename}")

    venv_python = os.path.join(os.path.dirname(sys.executable), 'python.exe') if os.name == 'nt' else sys.executable
    result = subprocess.run([venv_python, "app/ingest.py"], capture_output=True, text=True, cwd=os.getcwd())

    if result.returncode != 0:
        print(f"Ingest failed: {result.stderr}")
        return {"message": "Files uploaded but indexing failed — check terminal"}

    print(f"Ingest output: {result.stdout}")
    return {"message": "Files uploaded and indexed!"}
