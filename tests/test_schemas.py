import json
import sys
import unittest
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_evaluation import validate_alignment

class TestEvaluationSchemas(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas_dir = ROOT / "evaluation" / "schemas"

        with open(self.schemas_dir / "input.json", "r", encoding="utf-8") as f:
            self.input_schema = json.load(f)

        with open(self.schemas_dir / "output.json", "r", encoding="utf-8") as f:
            self.output_schema = json.load(f)

    def test_valid_input(self) -> None:
        valid_input = {
            "dataset_id": "DS-001",
            "test_cases": [
                {
                    "query_id": "Q-001",
                    "query": "What is the primary core architecture?",
                    "expected_document_ids": ["DOC-101", "DOC-102"]
                }
            ]
        }
        validate(instance=valid_input, schema=self.input_schema)

    def test_invalid_input_missing_required(self) -> None:
        invalid_input = {
            "dataset_id": "DS-001"
            # test_cases missing
        }
        with self.assertRaises(ValidationError):
            validate(instance=invalid_input, schema=self.input_schema)

    def test_invalid_input_extra_property(self) -> None:
        invalid_input = {
            "dataset_id": "DS-001",
            "test_cases": [],
            "extra_field": "not allowed"
        }
        with self.assertRaises(ValidationError):
            validate(instance=invalid_input, schema=self.input_schema)

    def test_valid_output(self) -> None:
        valid_output = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-XYZ",
            "results": [
                {
                    "query_id": "Q-001",
                    "generated_answer": "Neutral placeholder answer text.",
                    "retrieved_document_ids": ["DOC-101", "DOC-102"],
                    "cited_document_ids": ["DOC-101"]
                }
            ]
        }
        validate(instance=valid_output, schema=self.output_schema)

    def test_invalid_output_missing_required(self) -> None:
        invalid_output = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-XYZ"
            # results missing
        }
        with self.assertRaises(ValidationError):
            validate(instance=invalid_output, schema=self.output_schema)

    def test_alignment_pass(self) -> None:
        input_data = {
            "dataset_id": "DS-001",
            "test_cases": [
                {"query_id": "Q-001", "query": "q1", "expected_document_ids": ["DOC-1"]},
                {"query_id": "Q-002", "query": "q2", "expected_document_ids": ["DOC-2"]}
            ]
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-X",
            "results": [
                {"query_id": "Q-001", "generated_answer": "ans1", "retrieved_document_ids": [], "cited_document_ids": []},
                {"query_id": "Q-002", "generated_answer": "ans2", "retrieved_document_ids": [], "cited_document_ids": []}
            ]
        }
        # Should not raise any error
        validate_alignment(input_data, output_data)

    def test_alignment_mismatch_dataset_id(self) -> None:
        input_data = {
            "dataset_id": "DS-001",
            "test_cases": []
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "DS-002",
            "model_id": "MODEL-X",
            "results": []
        }
        with self.assertRaises(SystemExit):
            validate_alignment(input_data, output_data)

    def test_alignment_missing_query(self) -> None:
        input_data = {
            "dataset_id": "DS-001",
            "test_cases": [
                {"query_id": "Q-001", "query": "q1", "expected_document_ids": ["DOC-1"]},
                {"query_id": "Q-002", "query": "q2", "expected_document_ids": ["DOC-2"]}
            ]
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-X",
            "results": [
                {"query_id": "Q-001", "generated_answer": "ans1", "retrieved_document_ids": [], "cited_document_ids": []}
            ]
        }
        with self.assertRaises(SystemExit):
            validate_alignment(input_data, output_data)

    def test_alignment_extra_query(self) -> None:
        input_data = {
            "dataset_id": "DS-001",
            "test_cases": [
                {"query_id": "Q-001", "query": "q1", "expected_document_ids": ["DOC-1"]}
            ]
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-X",
            "results": [
                {"query_id": "Q-001", "generated_answer": "ans1", "retrieved_document_ids": [], "cited_document_ids": []},
                {"query_id": "Q-002", "generated_answer": "ans2", "retrieved_document_ids": [], "cited_document_ids": []}
            ]
        }
        with self.assertRaises(SystemExit):
            validate_alignment(input_data, output_data)
