import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import (
    calculate_recall_at_k,
    calculate_reciprocal_rank,
    calculate_mrr,
    calculate_citation_accuracy,
    calculate_average_ttft,
    calculate_throughput,
    calculate_tool_call_accuracy,
    calculate_instruction_diversity,
    calculate_sample_relevance,
    calculate_grammatical_correctness,
    calculate_complexity_score
)

class TestMetrics(unittest.TestCase):
    def test_recall_at_k(self) -> None:
        retrieved = ["doc1", "doc2", "doc3", "doc4"]
        expected = ["doc2", "doc4", "doc5"]
        self.assertAlmostEqual(calculate_recall_at_k(retrieved, expected, 2), 1.0 / 3.0)
        self.assertAlmostEqual(calculate_recall_at_k(retrieved, expected, 4), 2.0 / 3.0)
        
    def test_recall_at_k_empty(self) -> None:
        self.assertEqual(calculate_recall_at_k(["doc1"], [], 5), 0.0)
        self.assertEqual(calculate_recall_at_k([], ["doc1"], 5), 0.0)

    def test_reciprocal_rank(self) -> None:
        self.assertEqual(calculate_reciprocal_rank(["doc1", "doc2"], ["doc1"]), 1.0)
        self.assertEqual(calculate_reciprocal_rank(["doc1", "doc2"], ["doc2"]), 0.5)
        self.assertEqual(calculate_reciprocal_rank(["doc1", "doc2"], ["doc3"]), 0.0)
        self.assertEqual(calculate_reciprocal_rank([], ["doc1"]), 0.0)
        self.assertEqual(calculate_reciprocal_rank(["doc1"], []), 0.0)

    def test_mrr(self) -> None:
        all_retrieved = [
            ["doc1", "doc2"],
            ["doc3", "doc4"],
            ["doc5", "doc6"]
        ]
        all_expected = [
            ["doc1"],
            ["doc4"],
            ["doc7"]
        ]
        self.assertAlmostEqual(calculate_mrr(all_retrieved, all_expected), 0.5)

    def test_mrr_empty(self) -> None:
        self.assertEqual(calculate_mrr([], []), 0.0)

    def test_citation_accuracy(self) -> None:
        self.assertAlmostEqual(calculate_citation_accuracy("This is DOC-101 and DOC-102", ["DOC-101", "DOC-102"]), 1.0)
        self.assertAlmostEqual(calculate_citation_accuracy("This is DOC-101", ["DOC-101", "DOC-102"]), 2.0 / 3.0)
        self.assertAlmostEqual(calculate_citation_accuracy("This is DOC-101 and DOC-102", ["DOC-101"]), 2.0 / 3.0)
        self.assertAlmostEqual(calculate_citation_accuracy("", []), 1.0)
        self.assertAlmostEqual(calculate_citation_accuracy("Some text without docs", []), 1.0)
        self.assertAlmostEqual(calculate_citation_accuracy("", ["DOC-101"]), 0.0)
        self.assertAlmostEqual(calculate_citation_accuracy("Some text without docs", ["DOC-101"]), 0.0)

    def test_serving_metrics(self) -> None:
        self.assertAlmostEqual(calculate_average_ttft([0.1, 0.2, 0.3]), 0.2)
        self.assertEqual(calculate_average_ttft([]), 0.0)
        self.assertAlmostEqual(calculate_throughput(100, 2.5), 40.0)
        self.assertEqual(calculate_throughput(100, 0.0), 0.0)

    def test_tool_call_accuracy(self) -> None:
        self.assertAlmostEqual(calculate_tool_call_accuracy(["calc", "search"], ["calc", "search"]), 1.0)
        self.assertAlmostEqual(calculate_tool_call_accuracy(["calc"], ["calc", "search"]), 2.0 / 3.0)
        self.assertAlmostEqual(calculate_tool_call_accuracy(["calc", "search"], ["calc"]), 2.0 / 3.0)
        self.assertEqual(calculate_tool_call_accuracy([], []), 1.0)
        self.assertEqual(calculate_tool_call_accuracy(["calc"], []), 0.0)
        self.assertEqual(calculate_tool_call_accuracy([], ["calc"]), 0.0)

    def test_instruction_diversity(self) -> None:
        self.assertAlmostEqual(calculate_instruction_diversity(["a", "b", "c"]), 1.0)
        self.assertAlmostEqual(calculate_instruction_diversity(["a", "a", "b"]), 2.0 / 3.0)
        self.assertEqual(calculate_instruction_diversity([]), 1.0)

    def test_dataset_quality_metrics(self) -> None:
        # Test relevance
        self.assertGreater(calculate_sample_relevance("test this", "this is a test output"), 0.0)
        self.assertEqual(calculate_sample_relevance("", "output"), 0.0)
        
        # Test grammatical correctness
        self.assertEqual(calculate_grammatical_correctness("Hello world."), 1.0)
        self.assertLess(calculate_grammatical_correctness("hello world"), 1.0) # lowercase start and missing punctuation
        
        # Test complexity
        self.assertGreater(calculate_complexity_score("If we find the key, then open it."), 0.0)
        self.assertEqual(calculate_complexity_score(""), 0.0)

if __name__ == "__main__":
    unittest.main()
