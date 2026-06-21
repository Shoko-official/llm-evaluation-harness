import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.metrics import calculate_recall_at_k, calculate_reciprocal_rank, calculate_mrr

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

if __name__ == "__main__":
    unittest.main()
