import sys
import unittest
import tempfile
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_mock_data import generate_mock_data
from scripts.validate_evaluation import validate_input_file, validate_output_file, validate_alignment, calculate_metrics
from scripts.generate_report import generate_report
from scripts.export_to_paper import export_metrics_to_paper

class TestEndToEndFlow(unittest.TestCase):
    def test_e2e_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Paths
            input_file = tmp_path / "input.json"
            output_file = tmp_path / "output.json"
            input_schema = ROOT / "evaluation" / "schemas" / "input.json"
            output_schema = ROOT / "evaluation" / "schemas" / "output.json"
            
            # 1. Generate data
            generate_mock_data(input_file, output_file)
            self.assertTrue(input_file.is_file())
            self.assertTrue(output_file.is_file())
            
            # 2. Validate schemas & load
            input_data = validate_input_file(input_file, input_schema)
            output_data = validate_output_file(output_file, output_schema)
            self.assertIsNotNone(input_data)
            self.assertIsNotNone(output_data)
            
            # 3. Check alignment
            validate_alignment(input_data, output_data)
            
            # 4. Calculate metrics
            metrics = calculate_metrics(input_data, output_data)
            self.assertIn("mrr", metrics)
            self.assertIn("recall@5", metrics)
            self.assertIn("recall@10", metrics)
            self.assertIn("citation_accuracy", metrics)
            self.assertIn("citation_grounding", metrics)
            
            # 5. Generate report
            report_dir = tmp_path / "reports"
            generate_report(metrics, report_dir)
            self.assertTrue((report_dir / "evaluation_report.json").is_file())
            self.assertTrue((report_dir / "evaluation_report.md").is_file())
            
            # 6. Export to paper
            paper_dir = tmp_path / "paper"
            sections_dir = paper_dir / "sections"
            sections_dir.mkdir(parents=True)
            evaluation_md = sections_dir / "evaluation.md"
            evaluation_md.write_text("Mock paper section.", encoding="utf-8")
            
            export_metrics_to_paper(metrics, paper_dir)
            updated_content = evaluation_md.read_text(encoding="utf-8")
            self.assertIn("## Evaluation Results", updated_content)

if __name__ == "__main__":
    unittest.main()
