# Roadmap

This roadmap starts with governance only. Evaluation content starts after
Milestone 0 is complete and the repository has validation and CI.

## Milestone 0: Project Governance

Goal: establish a small, reviewable operating model for the evaluation
harness repository.

### Issues

1. [#1 Create evaluation harness governance documentation](https://github.com/Shoko-official/llm-evaluation-harness/issues/1)
2. [#2 Add issue and PR templates](https://github.com/Shoko-official/llm-evaluation-harness/issues/2)
3. [#3 Add minimal validation, CI, and folder structure](https://github.com/Shoko-official/llm-evaluation-harness/issues/3)

### Execution Order

1. Complete issue #1 before templates or validation.
2. Complete issue #2 before content changes.
3. Complete issue #3 before evaluation content.

No evaluation content should be added during Milestone 0.

## Acceptance Criteria

Milestone 0 is complete when:

* repository role is documented;
* roadmap exists;
* contribution and review rules exist;
* issue and PR templates exist;
* minimal validation commands exist;
* minimal CI exists;
* initial folders exist;
* no evaluation content has been added.

## Later Milestones

Expected sequence:

1. Define a minimal evaluation schema.
2. Implement retrieval metrics (recall@5, recall@10).
3. Add citation accuracy metric logic.
4. Add permission failure case simulations.
5. Create validation for evaluation files.
6. Connect evaluation results to paper tables.

Any change to evaluation structure, metrics, or evidence rules must happen in a
dedicated issue.
