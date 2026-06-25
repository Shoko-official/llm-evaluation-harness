# LLM Evaluation Harness: Milestone 7 Documentation

This directory contains design documents, schemas, and verification instructions for the LLM evaluation harness.

---

## 1. Agent Task Evaluation

Agent task evaluation measures an agent's ability to execute multi-step instructions, invoke correct tools, and arrive at successful task completion.

### Evaluation Metrics
* **Task Success Rate**: Ratio of test cases where the agent successfully completes the task instruction.
* **Tool Call Accuracy (F1 Score)**: Evaluates whether the agent called the expected set of tools, measuring set overlap precision and recall.
* **Average Steps Taken**: Mean number of reasoning-action turns taken by the agent.
* **Average Execution Time**: Mean wall-clock duration of the agent run in milliseconds.

### JSON Schemas
* **Input Schema** (`evaluation/schemas/agent_input.json`): Declares the query ID, task instruction, expected tools to be invoked, and a reference answer.
* **Output Schema** (`evaluation/schemas/agent_output.json`): Logs actual tools used, generated answer, steps taken, success flag, tool accuracy, and execution duration.

---

## 2. Dataset Quality Metrics

Used for evaluating synthetic datasets generated via bootstrapping pipelines (e.g., self-instruct style methods).

### Evaluation Metrics
* **Instruction Diversity Score**: Ratio of unique instruction tokens/structures to the total dataset size.
* **Sample Relevance**: Lexical overlap-based heuristic measuring how well the generated output aligns with the corresponding instruction.
* **Grammatical Correctness**: Syntactic cleanliness score checking formatting, capitalization, punctuation, and repetition.
* **Complexity Score**: Richness rating based on word counts and use of logical connectors (e.g., `if`, `then`, `else`, `because`).
* **Overall Dataset Quality Score**: Weighted composite score aggregated across all samples.

### JSON Schemas
* **Input Schema** (`evaluation/schemas/dataset_quality_input.json`): List of synthetic samples containing sample IDs, instructions, and generated outputs.
* **Output Schema** (`evaluation/schemas/dataset_quality_output.json`): Summary metrics (diversity, overall quality, sample count) and individual sample quality scores.

---

## 3. Running Validation

To validate datasets and outputs against these schemas, use the `scripts/validate_evaluation.py` tool.

### Agent Evaluation Validation
```bash
python scripts/validate_evaluation.py --agent --input evaluation/datasets/agent_mock_input.json --output evaluation/datasets/agent_mock_output.json
```

### Dataset Quality Validation
```bash
python scripts/validate_evaluation.py --dataset-quality --input evaluation/datasets/dataset_quality_mock_input.json --output evaluation/datasets/dataset_quality_mock_output.json
```

### Repository Check
Run the full test suite and validation scripts locally:
```bash
make validate
make test
```
