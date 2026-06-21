# LLM Evaluation Harness

`llm-evaluation-harness` defines the evaluation harness workspace for the
Modern LLM Systems 2026 / arXiv Report program.

This repository will organize evaluation adapters, datasets, and execution hooks after the shared project,
research ledger, and paper skeleton foundations are in place.

It is not the research ledger, paper repository, RAG implementation, inference
benchmark, agent runtime, memory layer, or observability stack.

## Repository Role

This repository owns:

* evaluation harness governance;
* future evaluation datasets;
* metric definition and calculation (recall@k, precision, citation accuracy);
* evaluation validation once introduced;
* paper-facing evaluation support when backed by approved evidence.

The central project board is:

* [Modern LLM Systems 2026 / arXiv Report](https://github.com/users/Shoko-official/projects/4)

## Current Scope

Milestone 0 is limited to governance.

Included:

* repository scope;
* roadmap;
* contribution rules;
* review rules.

Out of scope:

* evaluation datasets;
* scientific claims;
* evaluation benchmark runs;
* RAG, inference, agents, memory, or GraphRAG implementation.

## Evidence Policy

Future evaluation claims must reference approved research ledger material or stay
clearly marked as unresolved planning notes.

Unsupported claims must not be used as paper-ready evaluation content.

## Figure Policy

Allowed source formats:

* Mermaid text diagrams for workflows, architecture maps, dependency graphs, and
  concept maps.
* Python-generated images for visualizations that are not practical in Mermaid.

Not allowed by default:

* web images;
* screenshots unless explicitly approved;
* hand-drawn images;
* Figma, Canva, or PowerPoint exports;
* manually authored complex SVGs;
* binary figures without clear source;
* orphan figures.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
