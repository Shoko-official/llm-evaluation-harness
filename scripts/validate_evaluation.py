from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"Failed to parse JSON from {path}: {e}")

def validate_input_file(input_path: Path, schema_path: Path) -> dict:
    schema = load_json(schema_path)
    data = load_json(input_path)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        fail(f"Input validation error for {input_path.name}: {e.message}")
    return data

def validate_output_file(output_path: Path, schema_path: Path) -> dict:
    schema = load_json(schema_path)
    data = load_json(output_path)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        fail(f"Output validation error for {output_path.name}: {e.message}")
    return data

def validate_alignment(input_data: dict, output_data: dict) -> None:
    # 1. Dataset ID alignment
    if input_data.get("dataset_id") != output_data.get("dataset_id"):
        fail(
            f"Dataset ID mismatch: input dataset is '{input_data.get('dataset_id')}', "
            f"but output results dataset is '{output_data.get('dataset_id')}'"
        )
    
    # 2. Check query alignment
    if "test_cases" in input_data and "results" in output_data:
        input_queries = {tc["query_id"] for tc in input_data.get("test_cases", [])}
        output_queries = {res["query_id"] for res in output_data.get("results", [])}
        
        missing_queries = input_queries - output_queries
        if missing_queries:
            fail(f"Output is missing results for query IDs: {', '.join(sorted(missing_queries))}")
            
        extra_queries = output_queries - input_queries
        if extra_queries:
            fail(f"Output contains results for unknown query IDs: {', '.join(sorted(extra_queries))}")

def calculate_metrics(input_data: dict, output_data: dict) -> dict[str, float]:
    expected_map = {tc["query_id"]: tc.get("expected_document_ids", []) for tc in input_data.get("test_cases", [])}
    
    all_retrieved = []
    all_expected = []
    
    recalls_5 = []
    recalls_10 = []
    citation_accuracies = []
    citation_groundings = []
    ttfts = []
    throughputs = []
    
    from evaluation.metrics import calculate_recall_at_k, calculate_mrr, calculate_citation_accuracy
    from evaluation.citation_verifier import verify_citation_grounding
    
    for res in output_data.get("results", []):
        q_id = res["query_id"]
        retrieved = res.get("retrieved_document_ids", [])
        expected = expected_map.get(q_id, [])
        cited = res.get("cited_document_ids", [])
        generated = res.get("generated_answer", "")
        
        all_retrieved.append(retrieved)
        all_expected.append(expected)
        
        recalls_5.append(calculate_recall_at_k(retrieved, expected, 5))
        recalls_10.append(calculate_recall_at_k(retrieved, expected, 10))
        
        citation_accuracies.append(calculate_citation_accuracy(generated, cited))
        citation_groundings.append(verify_citation_grounding(cited, retrieved))
        
        if res.get("ttft") is not None:
            ttfts.append(res["ttft"])
        if res.get("throughput") is not None:
            throughputs.append(res["throughput"])
        
    mrr_val = calculate_mrr(all_retrieved, all_expected)
    avg_recall_5 = sum(recalls_5) / len(recalls_5) if recalls_5 else 0.0
    avg_recall_10 = sum(recalls_10) / len(recalls_10) if recalls_10 else 0.0
    avg_citation_accuracy = sum(citation_accuracies) / len(citation_accuracies) if citation_accuracies else 0.0
    avg_citation_grounding = sum(citation_groundings) / len(citation_groundings) if citation_groundings else 0.0
    avg_ttft = sum(ttfts) / len(ttfts) if ttfts else 0.0
    avg_throughput = sum(throughputs) / len(throughputs) if throughputs else 0.0
    
    print("Evaluation Metrics:")
    print(f"  Mean Reciprocal Rank (MRR): {mrr_val:.4f}")
    print(f"  Recall@5: {avg_recall_5:.4f}")
    print(f"  Recall@10: {avg_recall_10:.4f}")
    print(f"  Citation Accuracy: {avg_citation_accuracy:.4f}")
    print(f"  Citation Grounding: {avg_citation_grounding:.4f}")
    print(f"  Average TTFT: {avg_ttft:.4f}s")
    print(f"  Average Throughput: {avg_throughput:.4f} tokens/s")
    
    return {
        "mrr": mrr_val,
        "recall@5": avg_recall_5,
        "recall@10": avg_recall_10,
        "citation_accuracy": avg_citation_accuracy,
        "citation_grounding": avg_citation_grounding,
        "ttft": avg_ttft,
        "throughput": avg_throughput
    }

def calculate_observability_metrics(input_data: dict, output_data: dict) -> dict[str, float]:
    expected_map = {
        tc["query_id"]: (tc.get("expected_span_operations", []), tc.get("max_expected_latency_ms", 0.0))
        for tc in input_data.get("test_cases", [])
    }
    
    latency_compliances = []
    operations_matches = []
    
    for res in output_data.get("results", []):
        q_id = res["query_id"]
        captured = res.get("captured_spans", [])
        expected_ops, max_latency = expected_map.get(q_id, ([], 0.0))
        
        # 1. Latency Compliance
        # Find root span (parent_span_id is "N/A" or None) or max duration
        root_spans = [s for s in captured if s.get("parent_span_id") in ("N/A", None, "null")]
        if root_spans:
            latency = root_spans[0].get("duration_ms", 0.0)
        elif captured:
            latency = max(s.get("duration_ms", 0.0) for s in captured)
        else:
            latency = 0.0
            
        latency_compliant = 1.0 if latency <= max_latency else 0.0
        latency_compliances.append(latency_compliant)
        
        # 2. Span Operations Match
        captured_ops = {s.get("name") for s in captured if s.get("name")}
        expected_ops_set = set(expected_ops)
        ops_match = 1.0 if expected_ops_set.issubset(captured_ops) else 0.0
        operations_matches.append(ops_match)
        
    avg_latency_compliance = sum(latency_compliances) / len(latency_compliances) if latency_compliances else 0.0
    avg_operations_match = sum(operations_matches) / len(operations_matches) if operations_matches else 0.0
    
    print("Observability Evaluation Metrics:")
    print(f"  Latency Compliance Rate: {avg_latency_compliance:.4f}")
    print(f"  Span Operations Match Rate: {avg_operations_match:.4f}")
    
    return {
        "latency_compliance": avg_latency_compliance,
        "span_operations_match": avg_operations_match
    }

def calculate_agent_metrics(input_data: dict, output_data: dict) -> dict[str, float]:
    expected_map = {
        tc["query_id"]: tc.get("expected_tools", [])
        for tc in input_data.get("test_cases", [])
    }
    
    successes = []
    tool_accuracies = []
    steps = []
    times = []
    
    from evaluation.metrics import calculate_tool_call_accuracy
    
    for res in output_data.get("results", []):
        q_id = res["query_id"]
        actual_tools = res.get("actual_tools_used", [])
        expected_tools = expected_map.get(q_id, [])
        
        successes.append(1.0 if res.get("task_success") else 0.0)
        tool_accuracies.append(calculate_tool_call_accuracy(actual_tools, expected_tools))
        steps.append(res.get("steps_taken", 0))
        times.append(res.get("execution_time_ms", 0.0))
        
    avg_success = sum(successes) / len(successes) if successes else 0.0
    avg_tool_accuracy = sum(tool_accuracies) / len(tool_accuracies) if tool_accuracies else 0.0
    avg_steps = sum(steps) / len(steps) if steps else 0.0
    avg_time = sum(times) / len(times) if times else 0.0
    
    print("Agent Evaluation Metrics:")
    print(f"  Task Success Rate: {avg_success:.4f}")
    print(f"  Tool Call Accuracy (F1): {avg_tool_accuracy:.4f}")
    print(f"  Average Steps Taken: {avg_steps:.2f}")
    print(f"  Average Execution Time: {avg_time:.2f}ms")
    
    return {
        "task_success_rate": avg_success,
        "tool_call_accuracy": avg_tool_accuracy,
        "average_steps": avg_steps,
        "average_execution_time_ms": avg_time
    }

def calculate_dataset_quality_metrics(input_data: dict, output_data: dict) -> dict[str, float]:
    input_samples = {s["sample_id"] for s in input_data.get("samples", [])}
    output_samples = {s["sample_id"] for s in output_data.get("sample_scores", [])}
    
    missing_samples = input_samples - output_samples
    if missing_samples:
        fail(f"Output quality scores are missing for sample IDs: {', '.join(sorted(missing_samples))}")
        
    extra_samples = output_samples - input_samples
    if extra_samples:
        fail(f"Output quality scores contain unknown sample IDs: {', '.join(sorted(extra_samples))}")
        
    metrics = output_data.get("metrics", {})
    diversity = metrics.get("instruction_diversity_score", 0.0)
    overall_quality = metrics.get("overall_quality_score", 0.0)
    
    print("Dataset Quality Evaluation Metrics:")
    print(f"  Instruction Diversity Score: {diversity:.4f}")
    print(f"  Overall Dataset Quality Score: {overall_quality:.4f}")
    print(f"  Sample Count: {metrics.get('sample_count', 0)}")
    
    return {
        "instruction_diversity_score": diversity,
        "overall_quality_score": overall_quality,
        "sample_count": metrics.get("sample_count", 0)
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Validate evaluation inputs and outputs against schemas")
    parser.add_argument("--input", type=str, help="Path to the evaluation input JSON dataset file")
    parser.add_argument("--output", type=str, help="Path to the evaluation output JSON results file")
    parser.add_argument("--input-schema", type=str, help="Path to the input JSON schema")
    parser.add_argument("--output-schema", type=str, help="Path to the output JSON schema")
    parser.add_argument("--observability", action="store_true", help="Run validation for observability dataset")
    parser.add_argument("--agent", action="store_true", help="Run validation for agent evaluation dataset")
    parser.add_argument("--dataset-quality", action="store_true", help="Run validation for synthetic dataset quality")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    if args.input_schema:
        input_schema_path = Path(args.input_schema)
    else:
        if args.observability:
            input_schema_path = root_dir / "evaluation" / "schemas" / "observability_input.json"
        elif args.agent:
            input_schema_path = root_dir / "evaluation" / "schemas" / "agent_input.json"
        elif args.dataset_quality:
            input_schema_path = root_dir / "evaluation" / "schemas" / "dataset_quality_input.json"
        else:
            input_schema_path = root_dir / "evaluation" / "schemas" / "input.json"

    if args.output_schema:
        output_schema_path = Path(args.output_schema)
    else:
        if args.observability:
            output_schema_path = root_dir / "evaluation" / "schemas" / "observability_output.json"
        elif args.agent:
            output_schema_path = root_dir / "evaluation" / "schemas" / "agent_output.json"
        elif args.dataset_quality:
            output_schema_path = root_dir / "evaluation" / "schemas" / "dataset_quality_output.json"
        else:
            output_schema_path = root_dir / "evaluation" / "schemas" / "output.json"
            
    input_data = None
    output_data = None
    
    if args.input:
        input_data = validate_input_file(Path(args.input), input_schema_path)
        print(f"Successfully validated input file: {args.input}")
        
    if args.output:
        output_data = validate_output_file(Path(args.output), output_schema_path)
        print(f"Successfully validated output file: {args.output}")
        
    if input_data and output_data:
        validate_alignment(input_data, output_data)
        print("Input and output alignment validation successful.")
        if args.observability:
            calculate_observability_metrics(input_data, output_data)
        elif args.agent:
            calculate_agent_metrics(input_data, output_data)
        elif args.dataset_quality:
            calculate_dataset_quality_metrics(input_data, output_data)
        else:
            calculate_metrics(input_data, output_data)

if __name__ == "__main__":
    main()
