"""
Export evaluation metrics to paper markdown tables.
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

def export_metrics_to_paper(metrics: dict[str, float], paper_dir: Path) -> None:
    evaluation_md_path = paper_dir / "sections" / "evaluation.md"
    if not evaluation_md_path.is_file():
        print(f"Paper evaluation file not found at {evaluation_md_path}", file=sys.stderr)
        return
        
    table_lines = [
        "## Evaluation Results",
        "",
        "| Metric | Value |",
        "| :--- | :--- |",
        f"| Mean Reciprocal Rank (MRR) | {metrics.get('mrr', 0.0):.4f} |",
        f"| Recall@5 | {metrics.get('recall@5', 0.0):.4f} |",
        f"| Recall@10 | {metrics.get('recall@10', 0.0):.4f} |",
        f"| Citation Accuracy | {metrics.get('citation_accuracy', 0.0):.4f} |",
        f"| Citation Grounding | {metrics.get('citation_grounding', 0.0):.4f} |",
        ""
    ]
    
    content = evaluation_md_path.read_text(encoding="utf-8")
    
    if "## Evaluation Results" in content:
        parts = content.split("## Evaluation Results")
        content = parts[0] + "\n".join(table_lines)
    else:
        content = content.strip() + "\n\n" + "\n".join(table_lines)
        
    evaluation_md_path.write_text(content, encoding="utf-8")
    print(f"Successfully exported evaluation metrics to {evaluation_md_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Export evaluation metrics to paper")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON dataset")
    parser.add_argument("--output", type=str, required=True, help="Path to output JSON results")
    parser.add_argument("--paper-dir", type=str, default="../modern-llm-systems-paper", help="Path to paper repo directory")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    paper_dir = ROOT / args.paper_dir
    
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
    export_metrics_to_paper(metrics, paper_dir)

if __name__ == "__main__":
    main()
