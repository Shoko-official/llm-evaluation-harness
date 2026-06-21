#!/usr/bin/env python3
"""
Export evaluation metrics to the paper's markdown tables.
"""
from __future__ import annotations

import sys
from pathlib import Path


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
