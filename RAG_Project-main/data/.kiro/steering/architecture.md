# Kiro Steering — Architecture

## Decision: Retrieval Strategy

Semantic retrieval is the default for conceptual questions. Structured retrieval is preferred for lists, latest rules, warnings, and change-history questions.

## Rule: Evidence First

Answers must be grounded in retrieved documentation. The assistant must not invent project facts.

## Warning: Authentication

Do not modify authentication-related configuration without validating the complete workflow.

## Change

The chunk size was adjusted to 500 tokens with overlap to improve retrieval context.
