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
                "cited_document_ids": ["DOC-101", "DOC-102"],
                "ttft": 0.12,
                "throughput": 42.5
            },
            {
                "query_id": "Q-002",
                "generated_answer": "Sparse attention reduces complexity, see [DOC-201].",
                "retrieved_document_ids": ["DOC-201", "DOC-202"],
                "cited_document_ids": ["DOC-201"],
                "ttft": 0.18,
                "throughput": 38.2
            },
            {
                "query_id": "Q-003",
                "generated_answer": "Flash attention optimizes GPU memory accesses, reference [DOC-301].",
                "retrieved_document_ids": ["DOC-301", "DOC-999", "DOC-998"],
                "cited_document_ids": ["DOC-301"],
                "ttft": 0.15,
                "throughput": 41.0
            },
            {
                "query_id": "Q-004",
                "generated_answer": "Multi-query attention uses a single key-value head [DOC-401].",
                "retrieved_document_ids": ["DOC-401", "DOC-402"],
                "cited_document_ids": ["DOC-401"],
                "ttft": 0.22,
                "throughput": 35.6
            },
            {
                "query_id": "Q-005",
                "generated_answer": "Group-query attention groups query heads, reference [DOC-501].",
                "retrieved_document_ids": ["DOC-501", "DOC-502"],
                "cited_document_ids": ["DOC-501"],
                "ttft": 0.14,
                "throughput": 44.1
            }
        ]
    }

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated mock input dataset: {input_path}")
    print(f"Generated mock output results: {output_path}")

def generate_mock_observability_data(input_path: Path, output_path: Path) -> None:
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_data = {
        "dataset_id": "mock_observability_baseline",
        "test_cases": [
            {
                "query_id": "Q-001",
                "expected_span_operations": ["generate_tokens", "is_prompt_safe"],
                "max_expected_latency_ms": 150.0
            },
            {
                "query_id": "Q-002",
                "expected_span_operations": ["hybrid_search", "rerank_chunks", "generate_tokens"],
                "max_expected_latency_ms": 300.0
            },
            {
                "query_id": "Q-003",
                "expected_span_operations": ["generate_tokens", "check_tool_call"],
                "max_expected_latency_ms": 200.0
            }
        ]
    }

    output_data = {
        "run_id": "run_mock_observability_001",
        "dataset_id": "mock_observability_baseline",
        "model_id": "mock_model_v1",
        "results": [
            {
                "query_id": "Q-001",
                "captured_spans": [
                    {
                        "span_id": "8a0f2b3c4d5e6f7a",
                        "trace_id": "0123456789abcdef0123456789abcdef",
                        "parent_span_id": "N/A",
                        "name": "is_prompt_safe",
                        "start_time": "2026-06-22T17:00:00.000Z",
                        "end_time": "2026-06-22T17:00:00.050Z",
                        "duration_ms": 50.0,
                        "service_name": "security",
                        "status": "ok"
                    },
                    {
                        "span_id": "7b1e2c3d4e5f6a7b",
                        "trace_id": "0123456789abcdef0123456789abcdef",
                        "parent_span_id": "8a0f2b3c4d5e6f7a",
                        "name": "generate_tokens",
                        "start_time": "2026-06-22T17:00:00.050Z",
                        "end_time": "2026-06-22T17:00:00.125Z",
                        "duration_ms": 75.0,
                        "service_name": "infer",
                        "status": "ok"
                    }
                ]
            },
            {
                "query_id": "Q-002",
                "captured_spans": [
                    {
                        "span_id": "1a2b3c4d5e6f7a8b",
                        "trace_id": "9876543210fedcba9876543210fedcba",
                        "parent_span_id": "N/A",
                        "name": "hybrid_search",
                        "start_time": "2026-06-22T17:01:00.000Z",
                        "end_time": "2026-06-22T17:01:00.100Z",
                        "duration_ms": 100.0,
                        "service_name": "rag",
                        "status": "ok"
                    },
                    {
                        "span_id": "2b3c4d5e6f7a8b9c",
                        "trace_id": "9876543210fedcba9876543210fedcba",
                        "parent_span_id": "1a2b3c4d5e6f7a8b",
                        "name": "rerank_chunks",
                        "start_time": "2026-06-22T17:01:00.100Z",
                        "end_time": "2026-06-22T17:01:00.150Z",
                        "duration_ms": 50.0,
                        "service_name": "rag",
                        "status": "ok"
                    },
                    {
                        "span_id": "3c4d5e6f7a8b9c0d",
                        "trace_id": "9876543210fedcba9876543210fedcba",
                        "parent_span_id": "2b3c4d5e6f7a8b9c",
                        "name": "generate_tokens",
                        "start_time": "2026-06-22T17:01:00.150Z",
                        "end_time": "2026-06-22T17:01:00.280Z",
                        "duration_ms": 130.0,
                        "service_name": "infer",
                        "status": "ok"
                    }
                ]
            },
            {
                "query_id": "Q-003",
                "captured_spans": [
                    {
                        "span_id": "4d5e6f7a8b9c0d1e",
                        "trace_id": "abcdef0123456789abcdef0123456789",
                        "parent_span_id": "N/A",
                        "name": "generate_tokens",
                        "start_time": "2026-06-22T17:02:00.000Z",
                        "end_time": "2026-06-22T17:02:00.120Z",
                        "duration_ms": 120.0,
                        "service_name": "infer",
                        "status": "ok"
                    },
                    {
                        "span_id": "5e6f7a8b9c0d1e2f",
                        "trace_id": "abcdef0123456789abcdef0123456789",
                        "parent_span_id": "4d5e6f7a8b9c0d1e",
                        "name": "check_tool_call",
                        "start_time": "2026-06-22T17:02:00.120Z",
                        "end_time": "2026-06-22T17:02:00.180Z",
                        "duration_ms": 60.0,
                        "service_name": "security",
                        "status": "ok"
                    }
                ]
            }
        ]
    }

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Generated mock observability input dataset: {input_path}")
    print(f"Generated mock observability output results: {output_path}")

def generate_mock_agent_data(input_path: Path, output_path: Path) -> None:
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    input_data = {
        "dataset_id": "mock_agent_baseline",
        "test_cases": [
            {
                "query_id": "Q-001",
                "task_instruction": "Calculate the sum of 45 and 90, then multiply by 2.",
                "expected_tools": ["calculator", "calculator"],
                "reference_answer": "270"
            },
            {
                "query_id": "Q-002",
                "task_instruction": "Search for the weather in Paris, then translate the summary to French.",
                "expected_tools": ["web_search", "translator"],
                "reference_answer": "La météo à Paris..."
            }
        ]
    }
    
    output_data = {
        "run_id": "run_mock_agent_001",
        "dataset_id": "mock_agent_baseline",
        "model_id": "mock_agent_model_v1",
        "results": [
            {
                "query_id": "Q-001",
                "actual_tools_used": ["calculator", "calculator"],
                "generated_answer": "The sum is 135 and multiplied by 2 is 270.",
                "steps_taken": 3,
                "task_success": True,
                "tool_call_accuracy": 1.0,
                "execution_time_ms": 1250.0
            },
            {
                "query_id": "Q-002",
                "actual_tools_used": ["web_search", "translator"],
                "generated_answer": "La météo à Paris est ensoleillée.",
                "steps_taken": 4,
                "task_success": True,
                "tool_call_accuracy": 1.0,
                "execution_time_ms": 1850.0
            }
        ]
    }
    
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Generated mock agent input dataset: {input_path}")
    print(f"Generated mock agent output results: {output_path}")

def generate_mock_dataset_quality_data(input_path: Path, output_path: Path) -> None:
    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    input_data = {
        "dataset_id": "mock_dataset_quality_baseline",
        "samples": [
            {
                "sample_id": "S-001",
                "instruction": "Write a python function to check if a number is prime.",
                "input": None,
                "output": "def is_prime(n):\n    if n <= 1: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True"
            },
            {
                "sample_id": "S-002",
                "instruction": "Explain the concept of quantum superposition in simple terms.",
                "input": None,
                "output": "Quantum superposition is the fundamental principle of quantum mechanics where a system can exist in multiple states at the same time."
            }
        ]
    }
    
    output_data = {
        "run_id": "run_mock_quality_001",
        "dataset_id": "mock_dataset_quality_baseline",
        "metrics": {
            "instruction_diversity_score": 1.0,
            "overall_quality_score": 0.85,
            "sample_count": 2
        },
        "sample_scores": [
            {
                "sample_id": "S-001",
                "relevance_score": 0.9,
                "grammatical_correctness": 0.95,
                "complexity_score": 0.7,
                "overall_score": 0.85
            },
            {
                "sample_id": "S-002",
                "relevance_score": 0.85,
                "grammatical_correctness": 0.9,
                "complexity_score": 0.8,
                "overall_score": 0.85
            }
        ]
    }
    
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_data, f, indent=2)
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Generated mock dataset quality input: {input_path}")
    print(f"Generated mock dataset quality output: {output_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic evaluation data for testing")
    parser.add_argument("--input-out", type=str, help="Destination path for the mock input dataset JSON")
    parser.add_argument("--output-out", type=str, help="Destination path for the mock output results JSON")
    parser.add_argument("--observability", action="store_true", help="Generate observability mock dataset")
    parser.add_argument("--agent", action="store_true", help="Generate agent evaluation mock dataset")
    parser.add_argument("--dataset-quality", action="store_true", help="Generate dataset quality mock dataset")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    if args.observability:
        input_path = Path(args.input_out) if args.input_out else root_dir / "evaluation" / "datasets" / "observability_mock_input.json"
        output_path = Path(args.output_out) if args.output_out else root_dir / "evaluation" / "datasets" / "observability_mock_output.json"
        generate_mock_observability_data(input_path, output_path)
    elif args.agent:
        input_path = Path(args.input_out) if args.input_out else root_dir / "evaluation" / "datasets" / "agent_mock_input.json"
        output_path = Path(args.output_out) if args.output_out else root_dir / "evaluation" / "datasets" / "agent_mock_output.json"
        generate_mock_agent_data(input_path, output_path)
    elif args.dataset_quality:
        input_path = Path(args.input_out) if args.input_out else root_dir / "evaluation" / "datasets" / "dataset_quality_mock_input.json"
        output_path = Path(args.output_out) if args.output_out else root_dir / "evaluation" / "datasets" / "dataset_quality_mock_output.json"
        generate_mock_dataset_quality_data(input_path, output_path)
    else:
        input_path = Path(args.input_out) if args.input_out else root_dir / "evaluation" / "datasets" / "mock_input.json"
        output_path = Path(args.output_out) if args.output_out else root_dir / "evaluation" / "datasets" / "mock_output.json"
        generate_mock_data(input_path, output_path)

if __name__ == "__main__":
    main()
