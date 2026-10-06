# Cursor Project Notes

## Architecture Decision

The team chose a Python backend with a Gradio user interface for the documentation assistant.

## UI Rule

The interface should remain simple and expose one main chat experience.

## Warning

Do not commit API keys or `.env` files to source control.

## Change

The project added Pinecone as the persistent vector store after the initial local prototype.
