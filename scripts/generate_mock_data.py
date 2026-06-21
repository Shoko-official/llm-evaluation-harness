from __future__ import annotations

import argparse
import json
from pathlib import Path

def generate_mock_data(input_path: Path, output_path: Path) -> None:
    # Ensure parent directories exist
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Define mock input dataset
    input_data = {
        "dataset_id": "mock_baseline",
        "test_cases": [
            {
                "query_id": "Q-001",
                "query": "What is the primary attention mechanism in transformer models?",
                "expected_document_ids": ["DOC-101", "DOC-102"]
            },
            {
                "query_id": "Q-002",
                "query": "How is sparse attention defined?",
                "expected_document_ids": ["DOC-201"]
            },
            {
                "query_id": "Q-003",
                "query": "What are the benefits of flash attention?",
                "expected_document_ids": ["DOC-301", "DOC-302", "DOC-303"]
            },
            {
                "query_id": "Q-004",
                "query": "How does multi-query attention differ from multi-head attention?",
                "expected_document_ids": ["DOC-401"]
            },
            {
                "query_id": "Q-005",
                "query": "What is group-query attention?",
                "expected_document_ids": ["DOC-501", "DOC-502"]
            }
        ]
    }

    # 2. Define mock output results
    output_data = {
        "run_id": "run_mock_baseline_001",
        "dataset_id": "mock_baseline",
        "model_id": "mock_model_v1",
        "results": [
            {
                "query_id": "Q-001",
                "generated_answer": "Attention is all you need as described in [DOC-101] and [DOC-102].",
                "retrieved_document_ids": ["DOC-101", "DOC-102", "DOC-999"],
                "cited_document_ids": ["DOC-101", "DOC-102"]
            },
            {
                "query_id": "Q-002",
                "generated_answer": "Sparse attention reduces complexity, see [DOC-201].",
                "retrieved_document_ids": ["DOC-201", "DOC-202"],
                "cited_document_ids": ["DOC-201"]
            },
            {
                "query_id": "Q-003",
                "generated_answer": "Flash attention optimizes GPU memory accesses, reference [DOC-301].",
                "retrieved_document_ids": ["DOC-301", "DOC-999", "DOC-998"],
                "cited_document_ids": ["DOC-301"]
            },
            {
                "query_id": "Q-004",
                "generated_answer": "Multi-query attention uses a single key-value head [DOC-401].",
                "retrieved_document_ids": ["DOC-401", "DOC-402"],
                "cited_document_ids": ["DOC-401"]
            },
            {
                "query_id": "Q-005",
                "generated_answer": "Group-query attention groups query heads, reference [DOC-501].",
                "retrieved_document_ids": ["DOC-501", "DOC-502"],
                "cited_document_ids": ["DOC-501"]
            }
        ]
    }

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated mock input dataset: {input_path}")
    print(f"Generated mock output results: {output_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic evaluation data for testing")
    parser.add_argument("--input-out", type=str, help="Destination path for the mock input dataset JSON")
    parser.add_argument("--output-out", type=str, help="Destination path for the mock output results JSON")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    input_path = Path(args.input_out) if args.input_out else root_dir / "evaluation" / "datasets" / "mock_input.json"
    output_path = Path(args.output_out) if args.output_out else root_dir / "evaluation" / "datasets" / "mock_output.json"
    
    generate_mock_data(input_path, output_path)

if __name__ == "__main__":
    main()
