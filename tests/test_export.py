import sys
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_to_paper import export_metrics_to_paper

class TestExport(unittest.TestCase):
    def test_export_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            sections_dir = tmp_path / "sections"
            sections_dir.mkdir(parents=True)
            
            evaluation_md = sections_dir / "evaluation.md"
            evaluation_md.write_text("Existing draft content.", encoding="utf-8")
            
            metrics = {
                "mrr": 0.8,
                "recall@5": 0.9,
                "recall@10": 0.95,
                "citation_accuracy": 0.85,
                "citation_grounding": 0.92
            }
            
            export_metrics_to_paper(metrics, tmp_path)
            
            updated_content = evaluation_md.read_text(encoding="utf-8")
            self.assertIn("## Evaluation Results", updated_content)
            self.assertIn("| Mean Reciprocal Rank (MRR) | 0.8000 |", updated_content)
            self.assertIn("| Recall@5 | 0.9000 |", updated_content)
            self.assertIn("| Recall@10 | 0.9500 |", updated_content)
            self.assertIn("| Citation Accuracy | 0.8500 |", updated_content)
            self.assertIn("| Citation Grounding | 0.9200 |", updated_content)

if __name__ == "__main__":
    unittest.main()
