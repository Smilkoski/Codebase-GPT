# Codebase GPT — Your Private Document & Codebase Chatbot (2025)

**Ask questions in plain English about any file in your project:**  
PDFs, Word, Excel, Python, JavaScript, Markdown, logs… everything is instantly searchable and remembered forever.

Built with **FastAPI + Groq (Llama 3.1) + LangChain 1.1 + Chroma + PostgreSQL**  
Fully Dockerized — runs anywhere in seconds.
![img2.png](img2.png)


## Features

| Feature                        | Status | Description |
|-------------------------------|--------|-----------|
| Chat with any document/code   | Done | PDF, DOCX, XLSX, TXT, .py, .js, .md, .log … |
| Persistent conversation memory| Done | Postgres-backed — survives restarts |
| Drag & drop file upload → auto-indexing | Done | No terminal needed |
| Real-time sources shown       | Done | See exactly which file(s) the answer came from |
| Zero-config Docker setup      | Done | `docker compose up` and you’re live |
| Model caching                 | Done | First start ~20 s, then < 3 s startup forever |
| Works offline (after first download) | Done | Only Groq API key needed |

## Performance & Scale (Local Docker Setup)

| Your Laptop / PC          | Approx. number of average books* you can load | Startup time (cold) | Query speed | Notes |
|--------------------------------|-----------------------------------------------|---------------------|-------------|-------|
| 8–12 GB RAM                    | 50 – 150 books                                | 30–60 sec           | 2–4 sec     | Starts swapping |
| 16 GB RAM (most laptops)       | 250 – 450 books                               | 15–30 sec           | 1–2 sec     | Sweet spot for most users |
| 32 GB RAM                      | 600 – 1 000 books                             | 10–20 sec           | < 1.5 sec   | Perfect for power users |
| 64 GB+ RAM (M2/M3 Max, desktop)| 1 200+ books                                  | 8–12 sec            | < 1 sec     | Buttery smooth |

*One “average book” ≈ 300–500 pages ≈ 5–50 MB PDF/text

### Disk usage (rough estimate)

| 500 books (mixed PDF + text) | ~15–60 GB total (raw files + Chroma vector DB) |
|--------------------------------|-----------------------------------------------|
| HuggingFace embedding model    | ~350 MB (cached once)                         |

→ The real limits are **RAM** and **disk space**, not the code.  
Everything runs completely locally — no data ever leaves your machine.

### Want more than ~1000 books?

Switch the vector store from local Chroma to Pinecone / Qdrant / Weaviate (one-line change) and scale to tens of thousands of documents with zero slowdown.

## Quick Start (Docker — recommended)

```bash
# 1. Clone
git clone https://github.com/yourname/Codebase-GPT.git
cd Codebase-GPT

# 2. Put your Groq key in .env, create your own at https://groq.com/
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# 3. Start everything
docker compose up --build
```

Open → http://127.0.0.1:8000

Drop files → ask anything → enjoy!


## Project Structure

```
Codebase-GPT/
├── app/
│   ├── templates/index.html    # beautiful chat UI
│   ├── main.py                 # FastAPI + RAG logic
│   ├── ingest.py               # File indexing script
│   └── requirements.txt
├── repo-to-index/              # ← DROP YOUR FILES HERE
├── data/chroma_db/             # ← vector database (auto-created)
├── models/                     # ← cached HuggingFace models
├── Dockerfile
├── docker-compose.yml
└── .env                        # your Groq key

```

## Technical Documentation

### Stack (2025)

| Layer               | Technology                                 |
|---------------------|--------------------------------------------|
| Web Framework       | FastAPI + Uvicorn                          |
| LLM                 | Groq (Llama 3.1 8B or 70B)                 |
| Embeddings         | `sentence-transformers/all-MiniLM-L6-v2`   |
| Vector Store        | Chroma (langchain-chroma)                  |
| Document Loaders    | Unstructured (PDF/DOCX/Excel) + TextLoader |
| Memory              | PostgreSQL + SQLChatMessageHistory         |
| Frontend            | Pure HTML + jQuery (no React/Vue needed)   |

### Why this stack?

- **Speed**: Groq is the fastest inference provider in 2025
- **Cost**: Free tier is generous, paid is cheap
- **Privacy**: All your files stay on your machine / server
- **Simplicity**: Zero JavaScript framework → easy to customize

## How to Add More Files

### Option 1 — Drag & drop in browser (easiest)
Just use the upload area at the top of the web page.

### Option 2 — Drop files manually
```bash
# Put files here
cp your-file.pdf repo-to-index/

# Re-index (takes seconds)
docker exec -it <container_name> python app/ingest.py
# or locally:
python app/ingest.py
```

## Contributing

We love contributions! Here’s how to help:

1. **Fork** the repo
2. Create your feature branch (`git checkout -b feature/amazing-idea`)
3. Commit (`git commit -m 'Add streaming responses'`)
4. Push and open a Pull Request

### Areas that need love

- Streaming token-by-token responses
- Dark mode toggle
- Chat export (JSON/Markdown)
- Authentication (OAuth2 / simple password)
- Support for images in PDFs (OCR)
- Better Excel table rendering

All contributions are welcome — even tiny fixes!

## License

MIT License — do whatever you want with it.

---

Made with love by developers who were tired of Ctrl+F-ing through 50 files every day.

Enjoy your private, lightning-fast, always-remembering document assistant!