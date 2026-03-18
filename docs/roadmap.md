# Axiom Development Roadmap

This document outlines the phased development plan for the Axiom Universal Prompt & Skill Runtime.

## Phase 1: Foundation (v0.1)
*Goal: Core schemas, parsing, and exact validation.*
- **Core Models:** Implement the base schema definitions using Pydantic (Python) or Zod (TS).
- **Entities:** `Prompt`, `Skill`, and `UseCase` data models.
- **Registry Engine:** Build the `AxiomRegistry` to recursively load, index, and cache JSON/YAML definitions from a local file system.
- **Dependency Resolution:** Ensure that when a `UseCase` is loaded, its dependent `Skill`s are verified.

## Phase 2: Runtime Engine (v0.2)
*Goal: Abstract Syntax Tree and Execution Plans.*
- **Execution Planner:** Implement the `Runtime` to accept a `UseCase` ID and dynamically build a deterministic cross-framework `ExecutionPlan`.
- **Variable Mapping:** Resolve `inputs` variables dynamically down the graph.
- **Validation:** Assert that the Runtime purely configures the plan and makes *zero* API calls.

## Phase 3: Framework Adapters (v0.3)
*Goal: Real-world framework integrations.*
- **Adapter API:** Design the standard `BaseAdapter` interface.
- **LangChain Adapter:** Compile Axiom execution plans into LCEL Runnables.
- **ContextFlow Adapter:** Compile execution plans into ContextFlow Pipelines.
- **Raw API Adapter:** Implement standard OpenAI API translation.

## Phase 4: Enterprise Workflows (v1.0)
*Goal: High scale and complexity.*
- **Workflows:** Add the `Workflow` entity for graph-based logic (branching, looping, conditions).
- **Remote Registries:** Allow fetching definitions from S3, Git, or a Database instead of just the local file system.
- **Version Locking:** Implement strict `id@version` locking and resolution.
- **Semantic Search:** Add an embedding-based index to find prompts via natural language search.
