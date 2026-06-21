"""
Automated evaluation report generator.
"""
from __future__ import annotations

import argparse
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_evaluation import calculate_metrics

def generate_report(metrics: dict[str, float], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. JSON report
    json_report_path = report_dir / "evaluation_report.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    # 2. Markdown report
    md_report_path = report_dir / "evaluation_report.md"
    md_lines = [
        "# Evaluation Report",
        "",
        "## Summary Metrics",
        "",
        f"- **Mean Reciprocal Rank (MRR)**: {metrics.get('mrr', 0.0):.4f}",
        f"- **Recall@5**: {metrics.get('recall@5', 0.0):.4f}",
        f"- **Recall@10**: {metrics.get('recall@10', 0.0):.4f}",
        f"- **Citation Accuracy**: {metrics.get('citation_accuracy', 0.0):.4f}",
        f"- **Citation Grounding**: {metrics.get('citation_grounding', 0.0):.4f}",
        ""
    ]
    md_report_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Generated evaluation reports at: {json_report_path} and {md_report_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evaluation summaries (JSON/Markdown)")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON dataset")
    parser.add_argument("--output", type=str, required=True, help="Path to output JSON results")
    parser.add_argument("--report-dir", type=str, default="evaluation/reports", help="Directory to save generated reports")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    report_dir = ROOT / args.report_dir
    
    if not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
        
    if not output_path.is_file():
        print(f"Output file not found: {output_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)
    with open(output_path, "r", encoding="utf-8") as f:
        output_data = json.load(f)
        
    metrics = calculate_metrics(input_data, output_data)
    generate_report(metrics, report_dir)

if __name__ == "__main__":
    main()
