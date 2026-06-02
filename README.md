# OurRights

A Retrieval-Augmented Generation (RAG) agent that answers questions about **Israeli disability and hostility-victim rights** (זכויות נפגעי פעולות איבה ונכים). It retrieves from official source material and uses an LLM to produce grounded, source-based answers in Hebrew — built to minimize hallucination by answering only from ingested documents.

## How it works

The pipeline runs in stages:

1. **Collect sources** — `discover_links.py` / `extract_links.py` / `build_sources.py` gather official source URLs into `all_potential_links.json` and `hostilities_sources.json`.
2. **Scrape & structure** — `smart_ingest.py` fetches each source and turns it into clean, structured Markdown under `smart_data/`.
3. **Embed** — `ingest_to_chroma.py` chunks the Markdown (header-aware splitting) and embeds it into a local **ChromaDB** vector store (`chroma_db/`) using OpenAI `text-embedding-3-small`.
4. **Answer** — `final_rag_agent.py` takes a user profile (status, disability category, percentage), runs **multi-query retrieval** across several focused queries, and feeds the retrieved documents to an OpenAI chat model to generate the final answer.

`test_chunking.py` and `test_retrieval.py` are scratch scripts for inspecting chunking and retrieval quality.

## Tech stack

Python · LangChain · ChromaDB · OpenAI (embeddings + chat) · BeautifulSoup · requests

## Setup

```bash
# 1. (recommended) create a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. install dependencies
pip install langchain-openai langchain-chroma langchain-text-splitters langchain-core \
            chromadb openai beautifulsoup4 requests tqdm python-dotenv

# 3. add your OpenAI key — create a .env file in the project root:
echo "OPENAI_API_KEY=sk-..." > .env
```

> The API key is read from the `OPENAI_API_KEY` environment variable. **Never commit it.**

## Run

```bash
# (one-time) build the vector store from the scraped sources
python ingest_to_chroma.py

# ask the rights agent
python final_rag_agent.py
```

The user profile is currently set inside `final_rag_agent.py` (`user_form_data`) — edit it there to change the query. It's structured to be driven by a frontend form.

## Status

Research / prototype project. The retrieval pipeline and agent run end-to-end from the command line; there is no web UI in this repo yet.
