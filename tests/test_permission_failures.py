import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.permissions import filter_accessible_documents
from evaluation.metrics import calculate_recall_at_k, calculate_reciprocal_rank

class TestPermissionFailures(unittest.TestCase):
    def setUp(self) -> None:
        # Standard mock setup
        self.retrieved_ids = ["DOC-101", "DOC-102", "DOC-103", "DOC-104"]
        self.expected_ids = ["DOC-102", "DOC-104"]
        self.document_acl = {
            "DOC-102": ["admin"],       # restricted
            "DOC-104": ["restricted"],  # restricted
        }

    def test_full_permissions(self) -> None:
        # User has all permissions
        user_permissions = ["admin", "restricted"]
        filtered = filter_accessible_documents(self.retrieved_ids, user_permissions, self.document_acl)
        self.assertEqual(filtered, self.retrieved_ids)
        
        recall = calculate_recall_at_k(filtered, self.expected_ids, 4)
        self.assertAlmostEqual(recall, 1.0)

    def test_partial_permissions(self) -> None:
        # User only has admin permission, cannot access DOC-104
        user_permissions = ["admin"]
        filtered = filter_accessible_documents(self.retrieved_ids, user_permissions, self.document_acl)
        self.assertNotIn("DOC-104", filtered)
        self.assertIn("DOC-102", filtered)
        
        # Access check reduces recall because DOC-104 is filtered out
        recall = calculate_recall_at_k(filtered, self.expected_ids, 4)
        self.assertAlmostEqual(recall, 0.5)

    def test_no_permissions(self) -> None:
        # User has no permissions, restricted docs are filtered out
        user_permissions = []
        filtered = filter_accessible_documents(self.retrieved_ids, user_permissions, self.document_acl)
        self.assertNotIn("DOC-102", filtered)
        self.assertNotIn("DOC-104", filtered)
        
        recall = calculate_recall_at_k(filtered, self.expected_ids, 4)
        self.assertAlmostEqual(recall, 0.0)

    def test_public_documents_always_accessible(self) -> None:
        # Public documents (not in ACL) should be accessible even with empty user permissions
        filtered = filter_accessible_documents(["DOC-101", "DOC-103"], [], self.document_acl)
        self.assertEqual(filtered, ["DOC-101", "DOC-103"])

if __name__ == "__main__":
    unittest.main()
