#!/usr/bin/env python3
"""
Automated Evaluation Report Generator.
Validates input/output, calculates metrics, writes summaries, and updates paper tables.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_evaluation import validate_input_file, validate_output_file, validate_alignment, calculate_metrics
from scripts.export_to_paper import export_metrics_to_paper


def generate_report(metrics: dict[str, float], report_dir: Path) -> None:
    # Ensure reports directory exists
    report_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write JSON report
    json_path = report_dir / "evaluation_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Generated JSON report: {json_path}")

    # 2. Write MD report
    md_path = report_dir / "evaluation_report.md"
    rows = [
        "# Evaluation Report",
        "",
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

    md_content = "\n".join(rows) + "\n"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"Generated Markdown report: {md_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate evaluation reports and export metrics to paper"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Path to evaluation input JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to evaluation output JSON file",
    )
    parser.add_argument(
        "--input-schema",
        type=str,
        help="Path to input JSON schema",
    )
    parser.add_argument(
        "--output-schema",
        type=str,
        help="Path to output JSON schema",
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        help="Path to save reports directory",
    )
    parser.add_argument(
        "--paper-dir",
        type=str,
        help="Path to paper repository root",
    )

    args = parser.parse_args()

    input_path = (
        Path(args.input)
        if args.input
        else ROOT / "evaluation" / "datasets" / "mock_input.json"
    )
    output_path = (
        Path(args.output)
        if args.output
        else ROOT / "evaluation" / "datasets" / "mock_output.json"
    )

    input_schema_path = (
        Path(args.input_schema)
        if args.input_schema
        else ROOT / "evaluation" / "schemas" / "input.json"
    )
    output_schema_path = (
        Path(args.output_schema)
        if args.output_schema
        else ROOT / "evaluation" / "schemas" / "output.json"
    )

    report_dir_path = (
        Path(args.report_dir)
        if args.report_dir
        else ROOT / "evaluation" / "reports"
    )

    paper_dir_path = (
        Path(args.paper_dir)
        if args.paper_dir
        else ROOT.parent / "modern-llm-systems-paper"
    )

    # 1. Validate
    input_data = validate_input_file(input_path, input_schema_path)
    output_data = validate_output_file(output_path, output_schema_path)

    # 2. Check alignment
    validate_alignment(input_data, output_data)

    # 3. Calculate metrics
    metrics = calculate_metrics(input_data, output_data)

    # 4. Generate reports
    generate_report(metrics, report_dir_path)

    # 5. Export to paper
    export_metrics_to_paper(metrics, paper_dir_path)


if __name__ == "__main__":
    main()
