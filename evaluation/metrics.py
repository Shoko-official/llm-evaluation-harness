"""
Retrieval metrics for evaluation.
"""
from __future__ import annotations

def calculate_recall_at_k(retrieved_ids: list[str], expected_ids: list[str], k: int) -> float:
    """
    Calculate recall at k.
    
    Recall@k = (number of relevant documents in top k retrieved) / (total number of relevant documents)
    """
    if not expected_ids:
        return 0.0
    retrieved_at_k = retrieved_ids[:k]
    relevant_retrieved = len(set(retrieved_at_k) & set(expected_ids))
    return relevant_retrieved / len(expected_ids)
