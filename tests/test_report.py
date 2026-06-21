import sys
import unittest
import tempfile
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_report import generate_report

class TestReportGenerator(unittest.TestCase):
    def test_generate_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            metrics = {
                "mrr": 0.8,
                "recall@5": 0.9,
                "recall@10": 0.95,
                "citation_accuracy": 0.85,
                "citation_grounding": 0.92
            }
            
            generate_report(metrics, tmp_path)
            
            json_report = tmp_path / "evaluation_report.json"
            md_report = tmp_path / "evaluation_report.md"
            
            self.assertTrue(json_report.is_file())
            self.assertTrue(md_report.is_file())
            
            with open(json_report, "r", encoding="utf-8") as f:
                loaded_metrics = json.load(f)
                
            self.assertEqual(loaded_metrics["mrr"], 0.8)
            self.assertEqual(loaded_metrics["recall@5"], 0.9)
            
            md_content = md_report.read_text(encoding="utf-8")
            self.assertIn("# Evaluation Report", md_content)
            self.assertIn("Mean Reciprocal Rank (MRR)", md_content)

if __name__ == "__main__":
    unittest.main()
