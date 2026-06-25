import json
import sys
import unittest
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_evaluation import (
    validate_alignment,
    calculate_metrics,
    calculate_agent_metrics,
    calculate_dataset_quality_metrics
)

class TestEvaluationSchemas(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas_dir = ROOT / "evaluation" / "schemas"

        with open(self.schemas_dir / "input.json", "r", encoding="utf-8") as f:
            self.input_schema = json.load(f)

        with open(self.schemas_dir / "output.json", "r", encoding="utf-8") as f:
            self.output_schema = json.load(f)

        with open(self.schemas_dir / "observability_input.json", "r", encoding="utf-8") as f:
            self.obs_input_schema = json.load(f)

        with open(self.schemas_dir / "observability_output.json", "r", encoding="utf-8") as f:
            self.obs_output_schema = json.load(f)

        with open(self.schemas_dir / "agent_input.json", "r", encoding="utf-8") as f:
            self.agent_input_schema = json.load(f)

        with open(self.schemas_dir / "agent_output.json", "r", encoding="utf-8") as f:
            self.agent_output_schema = json.load(f)

        with open(self.schemas_dir / "dataset_quality_input.json", "r", encoding="utf-8") as f:
            self.dq_input_schema = json.load(f)

        with open(self.schemas_dir / "dataset_quality_output.json", "r", encoding="utf-8") as f:
            self.dq_output_schema = json.load(f)

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

    def test_mock_generator(self) -> None:
        import tempfile
        from scripts.generate_mock_data import generate_mock_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_file = tmp_path / "input.json"
            output_file = tmp_path / "output.json"
            
            generate_mock_data(input_file, output_file)
            
            # Read and validate
            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)
                
            validate(instance=input_data, schema=self.input_schema)
            validate(instance=output_data, schema=self.output_schema)
            # Alignment check should pass without SystemExit
            validate_alignment(input_data, output_data)

    def test_baseline_datasets(self) -> None:
        input_file = ROOT / "evaluation" / "datasets" / "mock_input.json"
        output_file = ROOT / "evaluation" / "datasets" / "mock_output.json"
        
        self.assertTrue(input_file.is_file(), "Baseline input dataset is missing")
        self.assertTrue(output_file.is_file(), "Baseline output dataset is missing")
        
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
        with open(output_file, "r", encoding="utf-8") as f:
            output_data = json.load(f)
            
        validate(instance=input_data, schema=self.input_schema)
        validate(instance=output_data, schema=self.output_schema)
        # Alignment check should pass without SystemExit
        validate_alignment(input_data, output_data)

    def test_calculate_metrics(self) -> None:
        input_data = {
            "dataset_id": "DS-001",
            "test_cases": [
                {"query_id": "Q-001", "query": "q1", "expected_document_ids": ["DOC-1", "DOC-2"]},
                {"query_id": "Q-002", "query": "q2", "expected_document_ids": ["DOC-3"]}
            ]
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "DS-001",
            "model_id": "MODEL-X",
            "results": [
                {"query_id": "Q-001", "generated_answer": "ans1", "retrieved_document_ids": ["DOC-5", "DOC-1"], "cited_document_ids": [], "ttft": 0.1, "throughput": 40.0},
                {"query_id": "Q-002", "generated_answer": "ans2", "retrieved_document_ids": ["DOC-3"], "cited_document_ids": [], "ttft": 0.2, "throughput": 20.0}
            ]
        }
        
        metrics = calculate_metrics(input_data, output_data)
        self.assertAlmostEqual(metrics["mrr"], 0.75)
        self.assertAlmostEqual(metrics["recall@5"], 0.75)
        self.assertAlmostEqual(metrics["recall@10"], 0.75)
        self.assertAlmostEqual(metrics["citation_accuracy"], 1.0)
        self.assertAlmostEqual(metrics["citation_grounding"], 1.0)
        self.assertAlmostEqual(metrics["ttft"], 0.15)
        self.assertAlmostEqual(metrics["throughput"], 30.0)

    def test_valid_observability_input(self) -> None:
        valid_input = {
            "dataset_id": "OBS-DS-001",
            "test_cases": [
                {
                    "query_id": "Q-001",
                    "expected_span_operations": ["generate_tokens", "is_prompt_safe"],
                    "max_expected_latency_ms": 150.0
                }
            ]
        }
        validate(instance=valid_input, schema=self.obs_input_schema)

    def test_valid_observability_output(self) -> None:
        valid_output = {
            "run_id": "RUN-001",
            "dataset_id": "OBS-DS-001",
            "model_id": "MODEL-XYZ",
            "results": [
                {
                    "query_id": "Q-001",
                    "captured_spans": [
                        {
                            "span_id": "8a0f2b3c4d5e6f7a",
                            "trace_id": "0123456789abcdef0123456789abcdef",
                            "parent_span_id": "N/A",
                            "name": "is_prompt_safe",
                            "start_time": "2026-06-22T17:00:00.000Z",
                            "end_time": "2026-06-22T17:00:00.050Z",
                            "duration_ms": 50.0,
                            "service_name": "security",
                            "status": "ok"
                        }
                    ]
                }
            ]
        }
        validate(instance=valid_output, schema=self.obs_output_schema)

    def test_observability_mock_generator(self) -> None:
        import tempfile
        from scripts.generate_mock_data import generate_mock_observability_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_file = tmp_path / "observability_input.json"
            output_file = tmp_path / "observability_output.json"
            
            generate_mock_observability_data(input_file, output_file)
            
            # Read and validate
            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)
                
            validate(instance=input_data, schema=self.obs_input_schema)
            validate(instance=output_data, schema=self.obs_output_schema)
            validate_alignment(input_data, output_data)

    def test_calculate_observability_metrics(self) -> None:
        from scripts.validate_evaluation import calculate_observability_metrics
        input_data = {
            "dataset_id": "OBS-DS-001",
            "test_cases": [
                {
                    "query_id": "Q-001",
                    "expected_span_operations": ["generate_tokens", "is_prompt_safe"],
                    "max_expected_latency_ms": 150.0
                },
                {
                    "query_id": "Q-002",
                    "expected_span_operations": ["hybrid_search"],
                    "max_expected_latency_ms": 100.0
                }
            ]
        }
        output_data = {
            "run_id": "RUN-001",
            "dataset_id": "OBS-DS-001",
            "model_id": "MODEL-XYZ",
            "results": [
                {
                    "query_id": "Q-001",
                    "captured_spans": [
                        {
                            "span_id": "8a0f2b3c4d5e6f7a",
                            "trace_id": "0123456789abcdef0123456789abcdef",
                            "parent_span_id": "N/A",
                            "name": "is_prompt_safe",
                            "start_time": "2026-06-22T17:00:00.000Z",
                            "end_time": "2026-06-22T17:00:00.050Z",
                            "duration_ms": 50.0,
                            "service_name": "security",
                            "status": "ok"
                        },
                        {
                            "span_id": "7b1e2c3d4e5f6a7b",
                            "trace_id": "0123456789abcdef0123456789abcdef",
                            "parent_span_id": "8a0f2b3c4d5e6f7a",
                            "name": "generate_tokens",
                            "start_time": "2026-06-22T17:00:00.050Z",
                            "end_time": "2026-06-22T17:00:00.125Z",
                            "duration_ms": 75.0,
                            "service_name": "infer",
                            "status": "ok"
                        }
                    ]
                },
                {
                    "query_id": "Q-002",
                    "captured_spans": [
                        {
                            "span_id": "1a2b3c4d5e6f7a8b",
                            "trace_id": "9876543210fedcba9876543210fedcba",
                            "parent_span_id": "N/A",
                            "name": "hybrid_search",
                            "start_time": "2026-06-22T17:01:00.000Z",
                            "end_time": "2026-06-22T17:01:00.120Z",
                            "duration_ms": 120.0,
                            "service_name": "rag",
                            "status": "ok"
                        }
                    ]
                }
            ]
        }
        
        metrics = calculate_observability_metrics(input_data, output_data)
        # Q-001: latency 50.0 <= 150.0 (compliant), spans match (compliant)
        # Q-002: latency 120.0 > 100.0 (non-compliant), spans match (compliant)
        self.assertAlmostEqual(metrics["latency_compliance"], 0.5)
        self.assertAlmostEqual(metrics["span_operations_match"], 1.0)

    def test_agent_mock_generator(self) -> None:
        import tempfile
        from scripts.generate_mock_data import generate_mock_agent_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_file = tmp_path / "agent_input.json"
            output_file = tmp_path / "agent_output.json"
            
            generate_mock_agent_data(input_file, output_file)
            
            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)
                
            validate(instance=input_data, schema=self.agent_input_schema)
            validate(instance=output_data, schema=self.agent_output_schema)
            validate_alignment(input_data, output_data)

    def test_dataset_quality_mock_generator(self) -> None:
        import tempfile
        from scripts.generate_mock_data import generate_mock_dataset_quality_data
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            input_file = tmp_path / "dq_input.json"
            output_file = tmp_path / "dq_output.json"
            
            generate_mock_dataset_quality_data(input_file, output_file)
            
            with open(input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
            with open(output_file, "r", encoding="utf-8") as f:
                output_data = json.load(f)
                
            validate(instance=input_data, schema=self.dq_input_schema)
            validate(instance=output_data, schema=self.dq_output_schema)
            validate_alignment(input_data, output_data)

    def test_calculate_agent_metrics(self) -> None:
        input_data = {
            "dataset_id": "mock_agent_baseline",
            "test_cases": [
                {
                    "query_id": "Q-001",
                    "task_instruction": "Calculate the sum of 45 and 90, then multiply by 2.",
                    "expected_tools": ["calculator", "calculator"],
                    "reference_answer": "270"
                }
            ]
        }
        output_data = {
            "run_id": "run_mock_agent_001",
            "dataset_id": "mock_agent_baseline",
            "model_id": "mock_agent_model_v1",
            "results": [
                {
                    "query_id": "Q-001",
                    "actual_tools_used": ["calculator", "calculator"],
                    "generated_answer": "The sum is 135 and multiplied by 2 is 270.",
                    "steps_taken": 3,
                    "task_success": True,
                    "tool_call_accuracy": 1.0,
                    "execution_time_ms": 1250.0
                }
            ]
        }
        metrics = calculate_agent_metrics(input_data, output_data)
        self.assertAlmostEqual(metrics["task_success_rate"], 1.0)
        self.assertAlmostEqual(metrics["tool_call_accuracy"], 1.0)
        self.assertAlmostEqual(metrics["average_steps"], 3.0)
        self.assertAlmostEqual(metrics["average_execution_time_ms"], 1250.0)

    def test_calculate_dataset_quality_metrics(self) -> None:
        input_data = {
            "dataset_id": "mock_dataset_quality_baseline",
            "samples": [
                {
                    "sample_id": "S-001",
                    "instruction": "Write a python function to check if a number is prime.",
                    "input": None,
                    "output": "def is_prime(n):\n    if n <= 1: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True"
                }
            ]
        }
        output_data = {
            "run_id": "run_mock_quality_001",
            "dataset_id": "mock_dataset_quality_baseline",
            "metrics": {
                "instruction_diversity_score": 1.0,
                "overall_quality_score": 0.85,
                "sample_count": 1
            },
            "sample_scores": [
                {
                    "sample_id": "S-001",
                    "relevance_score": 0.9,
                    "grammatical_correctness": 0.95,
                    "complexity_score": 0.7,
                    "overall_score": 0.85
                }
            ]
        }
        metrics = calculate_dataset_quality_metrics(input_data, output_data)
        self.assertAlmostEqual(metrics["instruction_diversity_score"], 1.0)
        self.assertAlmostEqual(metrics["overall_quality_score"], 0.85)
        self.assertEqual(metrics["sample_count"], 1)


