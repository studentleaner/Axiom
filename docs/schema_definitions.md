# Axiom Schema Definitions v0.1

This document outlines the standard JSON schema specification for Axiom entities. All schemas are designed to be human-readable, machine-validatable, and portable.

## 1. Global Schema Rules
All Axiom objects MUST contain the following fields:
- `id` (string): Unique identifier for the object. Dot-notation is recommended for namespaces (e.g., `sales.email.outreach`).
- `type` (string): The entity type (`prompt`, `skill`, `usecase`).
- `version` (string): SemVer compliant version string (e.g., `1.0.0`).
- `inputs` (array of strings): Expected dynamic variables.
- `metadata` (object): Key-value pairs for descriptive data.

## 2. Prompt Schema
The lowest-level primitive. Defines the text and template variables.

```json
{
  "$schema": "https://axiom.dev/schema/v0.1/prompt.json",
  "id": "summarize.basic",
  "type": "prompt",
  "version": "1.0.0",
  "template": "Please summarize the following text:\n{{text}}\n\nFocus on the main themes.",
  "inputs": ["text"],
  "tags": ["utility", "summarization"],
  "metadata": {
    "author": "prompt-engineering-team",
    "description": "A basic unopinionated summarizer."
  }
}
```

## 3. Skill Schema
A Skill aggregates prompts or defines a specific execution strategy.

```json
{
  "$schema": "https://axiom.dev/schema/v0.1/skill.json",
  "id": "rag.document_qa",
  "type": "skill",
  "version": "1.0.0",
  "inputs": ["query", "document_id"],
  "steps": [
    "retrieve_chunks",
    "rank_chunks",
    "generate_answer"
  ],
  "strategy": "pipeline",
  "metadata": {
    "description": "Standard Document Retrieval-Augmented Generation pipeline."
  }
}
```

## 4. UseCase Schema
A specialized assembly of Skills targeted at solving a holistic user objective.

```json
{
  "$schema": "https://axiom.dev/schema/v0.1/usecase.json",
  "id": "customer_support.inquiry_resolution",
  "type": "usecase",
  "version": "1.0.0",
  "inputs": ["customer_message", "customer_profile"],
  "skills": [
    "intent_classification",
    "rag.document_qa",
    "response_formatter"
  ],
  "metadata": {
    "department": "support",
    "criticality": "high"
  }
}
```

## 5. Storage Recommendations
Files should be organized functionally or by entity type.
```text
/axiom_registry
  /prompts
    summarize.basic.json
    extract.entities.json
  /skills
    rag.document_qa.json
  /usecases
    customer_support.json
```
