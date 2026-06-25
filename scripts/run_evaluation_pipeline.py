#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def load_json(path: Path) -> dict:
    if not path.is_file():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse JSON from {path}: {e}", file=sys.stderr)
        sys.exit(1)

def main() -> int:
    parser = argparse.ArgumentParser(description="Run evaluation pipeline, injecting latency metrics from benchmark simulation")
    parser.add_argument("--input", type=str, default="evaluation/datasets/generated_input.json", help="Path to input dataset JSON")
    parser.add_argument("--scaling-report", type=str, default="../llm-inference-benchmark/results/concurrency_scaling_report.json", help="Path to scaling report JSON")
    parser.add_argument("--output", type=str, default="evaluation/datasets/generated_output.json", help="Path to write evaluation output JSON")
    parser.add_argument("--concurrency", type=int, default=4, help="Target concurrency level from scaling report to inject metrics from")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    scaling_report_path = Path(args.scaling_report)
    output_path = Path(args.output)
    
    # 1. Load input dataset
    print(f"Loading input dataset from: {input_path}")
    input_data = load_json(input_path)
    
    # 2. Load scaling report and find target concurrency metrics
    print(f"Loading scaling report from: {scaling_report_path}")
    scaling_data = load_json(scaling_report_path)
    
    model_id = scaling_data.get("model_id", "mock-model-v1")
    concurrency_runs = scaling_data.get("concurrency_runs", [])
    
    target_run = None
    for run in concurrency_runs:
        if run.get("concurrency") == args.concurrency:
            target_run = run
            break
            
    if not target_run:
        print(f"Warning: Concurrency level {args.concurrency} not found in scaling report. Using first available run.", file=sys.stderr)
        if concurrency_runs:
            target_run = concurrency_runs[0]
            print(f"Selected concurrency level: {target_run.get('concurrency')}")
        else:
            print("Error: No concurrency runs found in scaling report.", file=sys.stderr)
            return 1
            
    # Extract mean throughput and TTFT (in milliseconds)
    mean_throughput = target_run.get("throughput_tokens_per_sec", 40.0)
    mean_ttft_ms = target_run.get("mean_ttft_ms", 150.0)
    # Convert TTFT to seconds for the evaluation harness
    mean_ttft_sec = mean_ttft_ms / 1000.0
    
    print(f"Using metrics for Concurrency {target_run.get('concurrency')}:")
    print(f"  Throughput: {mean_throughput:.2f} tok/s")
    print(f"  TTFT: {mean_ttft_sec:.4f}s ({mean_ttft_ms:.2f}ms)")
    
    # 3. Generate mock results with realistic RAG noise (MRR ~0.85, Recall ~0.90)
    # Seed for reproducibility
    random.seed(42)
    
    results = []
    for tc in input_data.get("test_cases", []):
        q_id = tc["query_id"]
        expected_docs = tc.get("expected_document_ids", [])
        
        # Decide retrieval status
        rand_val = random.random()
        retrieved_docs = []
        cited_docs = []
        
        # We simulate 3 main retrieval outcomes:
        # 1. Expected doc retrieved first (80% chance) -> MRR = 1.0, Recall = 1.0
        # 2. Expected doc retrieved second (10% chance) -> MRR = 0.5, Recall = 1.0
        # 3. Expected doc not retrieved (10% chance) -> MRR = 0.0, Recall = 0.0
        
        if expected_docs:
            primary_doc = expected_docs[0]
            if rand_val < 0.80:
                retrieved_docs = [primary_doc, "doc-noise-999"]
                cited_docs = [primary_doc]
                answer = f"According to the document [{primary_doc}], this contains self-attention or related mechanisms."
            elif rand_val < 0.90:
                retrieved_docs = ["doc-noise-111", primary_doc, "doc-noise-999"]
                cited_docs = [primary_doc]
                answer = f"The publication has been reviewed. Refer to [{primary_doc}] for details."
            else:
                retrieved_docs = ["doc-noise-111", "doc-noise-222"]
                cited_docs = []
                answer = "The required document was not found in the current index."
        else:
            retrieved_docs = ["doc-noise-111"]
            cited_docs = []
            answer = "No document is referenced."
            
        # Add random noise to individual TTFT and Throughput
        ttft_noise = random.uniform(-0.02, 0.02)
        throughput_noise = random.uniform(-5.0, 5.0)
        
        ttft = max(0.01, mean_ttft_sec + ttft_noise)
        throughput = max(1.0, mean_throughput + throughput_noise)
        
        results.append({
            "query_id": q_id,
            "generated_answer": answer,
            "retrieved_document_ids": retrieved_docs,
            "cited_document_ids": cited_docs,
            "ttft": round(ttft, 4),
            "throughput": round(throughput, 2)
        })
        
    output_data = {
        "run_id": f"run_pipeline_c{target_run.get('concurrency')}",
        "dataset_id": input_data.get("dataset_id", "generated_from_docs"),
        "model_id": model_id,
        "results": results
    }
    
    # 4. Save to output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Successfully generated evaluation output. Saved {len(results)} results to {output_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
