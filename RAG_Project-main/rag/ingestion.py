from pathlib import Path
import re
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode


TOOL_NAMES = {
    ".cursor": "cursor",
    ".kiro": "kiro",
    ".claude": "claude_code",
}


def detect_tool(path: Path) -> str:
    for part in path.parts:
        if part in TOOL_NAMES:
            return TOOL_NAMES[part]
    return "unknown"


def enrich_metadata(node: BaseNode, data_root: Path) -> None:
    source = Path(str(node.metadata.get("file_path", "")))
    if source:
        try:
            relative = source.resolve().relative_to(data_root.resolve())
        except ValueError:
            relative = source
    else:
        relative = Path("unknown.md")

    node.metadata["source_file"] = str(relative).replace("\\", "/")
    node.metadata["tool"] = detect_tool(relative)
    node.metadata["heading"] = node.metadata.get("heading", "")


def load_nodes(data_dir: Path, chunk_size: int = 500, chunk_overlap: int = 80):
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

    documents = SimpleDirectoryReader(
        input_dir=str(data_dir),
        recursive=True,
        required_exts=[".md"],
        filename_as_id=True,
    ).load_data()

    if not documents:
        raise RuntimeError(f"No Markdown files found under {data_dir}")

    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    nodes = splitter.get_nodes_from_documents(documents, show_progress=False)

    for node in nodes:
        enrich_metadata(node, data_dir)

    return nodes
