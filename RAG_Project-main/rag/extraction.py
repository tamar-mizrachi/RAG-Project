from pathlib import Path
import json
import hashlib
import re
from datetime import datetime, timezone

from llama_index.core import SimpleDirectoryReader
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI

from .config import Settings
from .models import KnowledgeItem, SourceInfo, StructuredKnowledge


CATEGORIES = ("decision", "rule", "warning", "change")


def _tool_for(path: Path) -> str:
    text = "/".join(path.parts).lower()
    if ".cursor" in text:
        return "cursor"
    if ".kiro" in text:
        return "kiro"
    if ".claude" in text:
        return "claude_code"
    return "unknown"


def _fallback_extract(text: str, source: str, tool: str) -> list[KnowledgeItem]:
    items = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        low = line.lower().strip()
        if not line.strip():
            continue

        category = None
        if any(k in low for k in ("decision", "decided", "chosen", "selected", "נבחר", "החלטה")):
            category = "decision"
        elif any(k in low for k in ("rule", "must", "should", "required", "חובה", "הנחיה")):
            category = "rule"
        elif any(k in low for k in ("warning", "caution", "sensitive", "do not", "אזהרה", "רגיש")):
            category = "warning"
        elif any(k in low for k in ("change", "changed", "added", "removed", "שינוי", "נוסף", "הוסר")):
            category = "change"

        if category:
            digest = hashlib.sha1(f"{source}:{i}:{line}".encode()).hexdigest()[:10]
            items.append(
                KnowledgeItem(
                    id=f"{category}-{digest}",
                    type=category,
                    title=line.strip("# -*"),
                    summary=line.strip(),
                    tags=[],
                    source=SourceInfo(
                        tool=tool,
                        file=source,
                        line_range=[i, i],
                    ),
                )
            )
    return items


def extract_structured_knowledge(settings: Settings) -> StructuredKnowledge:
    settings.require("openai_api_key")

    data_dir = Path(settings.data_dir)
    reader = SimpleDirectoryReader(
        input_dir=str(data_dir),
        recursive=True,
        required_exts=[".md"],
    )
    documents = reader.load_data()

    llm = OpenAI(model=settings.openai_model, api_key=settings.openai_api_key)

    result = StructuredKnowledge()
    all_items: list[KnowledgeItem] = []

    for doc in documents:
        source_path = Path(str(doc.metadata.get("file_path", "unknown.md")))
        try:
            relative = source_path.resolve().relative_to(data_dir.resolve())
        except ValueError:
            relative = source_path

        source = str(relative).replace("\\", "/")
        tool = _tool_for(relative)
        text = doc.text

        # The fallback guarantees a useful extraction even if the LLM
        # cannot produce a structured response.
        fallback = _fallback_extract(text, source, tool)

        prompt = f"""
Extract knowledge items from the Markdown document below.

Return ONLY valid JSON in this shape:
{{
  "items": [
    {{
      "type": "decision|rule|warning|change",
      "title": "short title",
      "summary": "short factual summary",
      "tags": ["tag1", "tag2"],
      "line_range": [1, 3]
    }}
  ]
}}

Do not invent facts. If there are no relevant items, return an empty list.

DOCUMENT:
{text[:12000]}
"""
        try:
            response = llm.chat([
                ChatMessage(role=MessageRole.USER, content=prompt)
            ])
            raw = response.message.content.strip()
            match = re.search(r"\{.*\}", raw, flags=re.S)
            payload = json.loads(match.group(0) if match else raw)
            extracted = []
            for idx, item in enumerate(payload.get("items", [])):
                item_type = item.get("type")
                if item_type not in CATEGORIES:
                    continue
                digest = hashlib.sha1(
                    f"{source}:{idx}:{item.get('title','')}".encode()
                ).hexdigest()[:10]
                extracted.append(
                    KnowledgeItem(
                        id=f"{item_type}-{digest}",
                        type=item_type,
                        title=str(item.get("title", "Untitled")),
                        summary=str(item.get("summary", "")),
                        tags=list(item.get("tags", [])),
                        source=SourceInfo(
                            tool=tool,
                            file=source,
                            line_range=item.get("line_range"),
                        ),
                    )
                )
            all_items.extend(extracted or fallback)
        except Exception:
            all_items.extend(fallback)

    for item in all_items:
        getattr(result, f"{item.type}s").append(item)

    result.generated_at = datetime.now(timezone.utc)
    return result


def save_knowledge(knowledge: StructuredKnowledge, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        knowledge.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load_knowledge(path: Path) -> StructuredKnowledge:
    if not path.exists():
        raise FileNotFoundError(
            f"Structured knowledge file not found: {path}. "
            "Run scripts/extract_knowledge.py first."
        )
    return StructuredKnowledge.model_validate_json(
        path.read_text(encoding="utf-8")
    )
