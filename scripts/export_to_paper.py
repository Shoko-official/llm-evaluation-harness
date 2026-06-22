#!/usr/bin/env python3
"""
Export evaluation metrics to the paper's markdown tables.
"""
from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def export_metrics_to_paper(metrics: dict[str, float], paper_dir: Path) -> None:
    eval_file = paper_dir / "sections" / "evaluation.md"
    if not eval_file.is_file():
        print(f"Warning: Paper evaluation file not found at {eval_file}.")
        return

    # Build markdown table
    rows = [
        "| Metric | Value |",
        "|---|---|",
        f"| Mean Reciprocal Rank (MRR) | {metrics.get('mrr', 0.0):.4f} |",
        f"| Recall@5 | {metrics.get('recall@5', 0.0):.4f} |",
        f"| Recall@10 | {metrics.get('recall@10', 0.0):.4f} |",
        f"| Citation Accuracy | {metrics.get('citation_accuracy', 0.0):.4f} |",
        f"| Citation Grounding | {metrics.get('citation_grounding', 0.0):.4f} |",
    ]

    if "ttft" in metrics:
        rows.append(f"| Average TTFT | {metrics['ttft']:.4f}s |")
    if "throughput" in metrics:
        rows.append(f"| Average Throughput | {metrics['throughput']:.4f} tokens/s |")

    table_content = "\n".join(rows)

    content = eval_file.read_text(encoding="utf-8")
    start_tag = "<!-- EVAL_METRICS_START -->"
    end_tag = "<!-- EVAL_METRICS_END -->"

    if start_tag in content and end_tag in content:
        # Replace content between placeholders
        start_idx = content.find(start_tag) + len(start_tag)
        end_idx = content.find(end_tag)
        new_content = content[:start_idx] + "\n" + table_content + "\n" + content[end_idx:]
    elif "## Evaluation Results" in content:
        # Replace existing results section
        parts = content.split("## Evaluation Results")
        new_content = parts[0] + "## Evaluation Results\n\n" + table_content + "\n"
    else:
        # Append to the end of the file
        new_content = content.rstrip() + "\n\n## Evaluation Results\n\n" + table_content + "\n"

    eval_file.write_text(new_content, encoding="utf-8")
    print(f"Successfully exported evaluation metrics to {eval_file}")


def export_scaling_to_paper(scaling_report: Path, paper_dir: Path) -> None:
    eval_file = paper_dir / "sections" / "evaluation.md"
    if not eval_file.is_file():
        print(f"Warning: Paper evaluation file not found at {eval_file}.")
        return
    if not scaling_report.is_file():
        print(f"Warning: Scaling report not found at {scaling_report}.")
        return

    try:
        with open(scaling_report, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error parsing scaling report: {e}")
        return

    runs = data.get("concurrency_runs", [])
    if not runs:
        print("Warning: No concurrency runs found in scaling report.")
        return

    rows = [
        "| Concurrency | Throughput (tok/s) | Mean Latency (ms) | Mean TTFT (ms) |",
        "|---|---|---|---|",
    ]
    for r in runs:
        rows.append(
            f"| {r.get('concurrency')} | {r.get('throughput_tokens_per_sec', 0.0):.2f} | "
            f"{r.get('mean_latency_ms', 0.0):.2f} | {r.get('mean_ttft_ms', 0.0):.2f} |"
        )

    table_content = "\n".join(rows)

    content = eval_file.read_text(encoding="utf-8")
    start_tag = "<!-- BENCHMARK_SCALING_START -->"
    end_tag = "<!-- BENCHMARK_SCALING_END -->"

    if start_tag in content and end_tag in content:
        start_idx = content.find(start_tag) + len(start_tag)
        end_idx = content.find(end_tag)
        new_content = content[:start_idx] + "\n" + table_content + "\n" + content[end_idx:]
        eval_file.write_text(new_content, encoding="utf-8")
        print(f"Successfully exported benchmark scaling metrics to {eval_file}")
    else:
        print("Warning: Scaling placeholders not found in paper evaluation section.")


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Export metrics to paper")
    parser.add_argument("--scaling-report", type=str, help="Path to scaling report JSON")
    parser.add_argument("--paper-dir", type=str, help="Path to paper repository root")
    parser.add_argument("--metrics-json", type=str, help="Path to evaluation report JSON")

    args = parser.parse_args()

    paper_path = Path(args.paper_dir) if args.paper_dir else ROOT.parent / "modern-llm-systems-paper"

    if args.metrics_json:
        metrics_path = Path(args.metrics_json)
        if metrics_path.is_file():
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics = json.load(f)
            export_metrics_to_paper(metrics, paper_path)

    if args.scaling_report:
        export_scaling_to_paper(Path(args.scaling_report), paper_path)

