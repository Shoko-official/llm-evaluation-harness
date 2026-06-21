import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.citation_verifier import verify_citation_grounding

class TestCitationVerifier(unittest.TestCase):
    def test_all_grounded(self) -> None:
        cited = ["DOC-101", "DOC-102"]
        retrieved = ["DOC-101", "DOC-102", "DOC-103"]
        self.assertAlmostEqual(verify_citation_grounding(cited, retrieved), 1.0)

    def test_partially_grounded(self) -> None:
        cited = ["DOC-101", "DOC-102"]
        retrieved = ["DOC-101", "DOC-103"]
        self.assertAlmostEqual(verify_citation_grounding(cited, retrieved), 0.5)

    def test_none_grounded(self) -> None:
        cited = ["DOC-101", "DOC-102"]
        retrieved = ["DOC-103", "DOC-104"]
        self.assertAlmostEqual(verify_citation_grounding(cited, retrieved), 0.0)

    def test_empty_citations(self) -> None:
        cited = []
        retrieved = ["DOC-101"]
        self.assertAlmostEqual(verify_citation_grounding(cited, retrieved), 1.0)

    def test_case_insensitivity(self) -> None:
        cited = ["doc-101", "DOC-102"]
        retrieved = ["DOC-101", "doc-102"]
        self.assertAlmostEqual(verify_citation_grounding(cited, retrieved), 1.0)

if __name__ == "__main__":
    unittest.main()
