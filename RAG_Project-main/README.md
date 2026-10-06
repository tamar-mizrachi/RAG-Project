# RAG with LlamaIndex — Agentic Coding Knowledge Assistant

A complete implementation for assignment 09: **RAG with LlamaIndex**.

The application builds a knowledge layer from Markdown documentation produced by Agentic Coding tools and answers questions using:

- LlamaIndex
- Cohere embeddings
- Pinecone vector database
- OpenAI for response synthesis / structured extraction
- Gradio chat UI
- Event-driven workflow
- Structured JSON extraction
- Routing between semantic and structured retrieval

## 1. Architecture

```text
Markdown files
     |
     v
Loading (LlamaIndex SimpleDirectoryReader)
     |
     v
Chunking (SentenceSplitter)
     |
     v
Cohere Embeddings
     |
     v
Pinecone + VectorStoreIndex
     |
     +------------------------------+
     |                              |
     v                              v
Semantic Search                 Structured Search
Retriever                       JSON data
     |                              |
     +--------------+---------------+
                    v
                  Router
                    |
                    v
             Response Synthesis
                    |
                    v
                Gradio UI
```

The runtime workflow is event-driven:

```text
Start
  -> ValidateInput
  -> ClassifyQuestion
  -> SemanticRetrieve OR StructuredRetrieve
  -> ValidateEvidence
  -> SynthesizeAnswer
  -> Stop
```

If semantic evidence is weak, the workflow can request another retrieval attempt with a broader query before returning a safe answer.

## 2. Requirements covered

### Stage A — MVP
- [x] At least two Agentic Coding tool folders
- [x] Markdown loading
- [x] LlamaIndex node parsing / chunking
- [x] Cohere embeddings
- [x] VectorStoreIndex
- [x] Pinecone vector store
- [x] Metadata: tool, file, heading, path
- [x] Retriever
- [x] Postprocessing
- [x] Response synthesis
- [x] Gradio chat interface

### Stage B — Event-Driven
- [x] Explicit workflow steps
- [x] Events with clear inputs/outputs
- [x] State
- [x] Validation
- [x] Low-confidence handling
- [x] Retrieval retry path

### Stage C — Data Extraction
- [x] Decisions
- [x] Rules
- [x] Warnings
- [x] Changes
- [x] JSON schema with source metadata
- [x] Structured extraction
- [x] Router between semantic and structured search
- [x] Structured query generation

## 3. Folder structure

```text
RAG_LlamaIndex_Project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── prepare.py
├── rag/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── ingestion.py
│   ├── vector_store.py
│   ├── semantic_search.py
│   ├── extraction.py
│   ├── structured_search.py
│   ├── router.py
│   ├── workflow.py
│   └── ui.py
├── data/
│   ├── .cursor/
│   ├── .kiro/
│   └── .claude/
├── structured/
│   └── knowledge.json
├── scripts/
│   ├── create_pinecone_index.py
│   └── extract_knowledge.py
├── tests/
│   ├── test_models.py
│   ├── test_router.py
│   └── test_validation.py
├── docs/
│   └── workflow.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── SUBMISSION_CHECKLIST.md
```

## 4. Installation

Python 3.11 is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Copy environment file:

```powershell
Copy-Item .env.example .env
```

Fill in:

```text
OPENAI_API_KEY=
COHERE_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=agentic-coding-rag
PINECONE_NAMESPACE=agentic-coding
```

## 5. Pinecone

The embedding model configured in this project is Cohere Embed English v3 with 1024 dimensions.

Create the index:

```bash
python scripts/create_pinecone_index.py
```

Do not create an index with a different dimension unless you also change the embedding model and configuration consistently.

## 6. Build the vector index

```bash
python -m app.prepare
```

This:

1. Reads all `.md` files below `data/`.
2. Adds source metadata.
3. Splits documents into nodes.
4. Creates embeddings with Cohere.
5. Stores vectors in Pinecone through LlamaIndex.

## 7. Extract structured knowledge

```bash
python scripts/extract_knowledge.py
```

The result is written to:

```text
structured/knowledge.json
```

The JSON contains decisions, rules, warnings and changes, each with source information.

## 8. Run the application

```bash
python -m app.main
```

Gradio starts locally and exposes a chat interface.

## 9. Example questions

Semantic:

- How is the application installed?
- What architecture was chosen?
- Why was Pinecone selected?
- What was the design direction?

Structured:

- List all technical decisions.
- What is the latest RTL rule?
- What warnings were recorded?
- What changes were made recently?
- Which decisions came from Kiro?
- What rules are related to authentication?

## 10. Testing

Run:

```bash
pytest -q
```

The included tests validate the project logic without requiring API credentials.

## 11. Real project data

The `data/` directory contains intentionally small demonstration Markdown files so the project can run immediately after configuration.

For submission, replace/add them with Markdown files actually produced by at least two Agentic Coding tools. Keep the source metadata structure intact.

## 12. Security

Never commit `.env`, API keys or credentials.

The `.gitignore` file excludes:

- `.env`
- Python caches
- local virtual environments
- generated runtime files
- local logs

## 13. Important note

External services are required for a real end-to-end run:

- OpenAI
- Cohere
- Pinecone

The included tests are intentionally offline and do not need those services.
