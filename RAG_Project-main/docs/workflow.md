# Event-Driven Workflow

```mermaid
flowchart TD
    A[User Question] --> B[Validate Input]
    B --> C[Classify / Route]
    C -->|Semantic| D[Vector Retriever]
    C -->|Structured| E[JSON Structured Search]
    D --> F[Validate Evidence]
    E --> F
    F -->|Weak / Empty| G[Retry or Safe Failure]
    F -->|Sufficient| H[LLM Response Synthesis]
    H --> I[Answer + Sources]
```

## Steps

1. **Validate Input**
   - Reject empty questions.
   - Reject whitespace-only input.

2. **Route**
   - List/latest/change/rule/warning style questions use structured search.
   - Conceptual questions use semantic retrieval.

3. **Retrieve**
   - Semantic path uses Pinecone through LlamaIndex.
   - Structured path uses the extracted JSON schema.

4. **Validate Evidence**
   - Semantic evidence is evaluated by similarity scores.
   - No evidence results in a safe response rather than hallucination.

5. **Synthesize**
   - OpenAI receives only the question and retrieved evidence.
   - The answer includes source metadata.

## State

The workflow state contains:

- query
- selected route
- routing reason
- evidence
- confidence
- retry count

Events carry only the information needed by the next step.
