from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, MessageRole

from .config import Settings


def _semantic_source(node):
    md = getattr(node, "metadata", {}) or {}
    return {
        "tool": md.get("tool", "unknown"),
        "file": md.get("source_file", md.get("file_path", "unknown")),
        "heading": md.get("heading", ""),
        "score": getattr(node, "score", None),
    }


def _structured_source(item):
    source = item.source
    return {
        "tool": source.tool,
        "file": source.file,
        "heading": source.heading,
        "score": None,
    }


def build_synthesizer(settings: Settings):
    settings.require("openai_api_key")
    llm = OpenAI(model=settings.openai_model, api_key=settings.openai_api_key)

    async def synthesize(query, evidence):
        contexts = []
        sources = []

        for item in evidence:
            if hasattr(item, "source") and hasattr(item, "summary"):
                contexts.append(
                    f"[{item.source.tool} | {item.source.file}]\n"
                    f"{item.title}: {item.summary}"
                )
                sources.append(_structured_source(item))
            else:
                contexts.append(
                    f"[{_semantic_source(item)['tool']} | {_semantic_source(item)['file']}]\n"
                    f"{getattr(item, 'text', '')}"
                )
                sources.append(_semantic_source(item))

        prompt = f"""
You are a documentation assistant.

Answer the user's question using ONLY the evidence supplied below.
Do not invent facts.
If the evidence is insufficient, say so clearly.
Prefer concise, factual answers.
Mention uncertainty when the evidence is conflicting.

QUESTION:
{query}

EVIDENCE:
{chr(10).join(contexts)}
"""

        response = await llm.achat([
            ChatMessage(role=MessageRole.USER, content=prompt)
        ])
        return response.message.content, sources

    return synthesize
