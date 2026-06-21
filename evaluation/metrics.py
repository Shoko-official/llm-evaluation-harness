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

def calculate_reciprocal_rank(retrieved_ids: list[str], expected_ids: list[str]) -> float:
    """
    Calculate reciprocal rank for a single query.
    
    Reciprocal Rank = 1 / rank of the first relevant document in retrieved_ids.
    Returns 0.0 if no relevant document is found or expected_ids is empty.
    """
    if not expected_ids:
        return 0.0
    for rank_idx, doc_id in enumerate(retrieved_ids):
        if doc_id in expected_ids:
            return 1.0 / (rank_idx + 1)
    return 0.0

def calculate_mrr(all_retrieved_ids: list[list[str]], all_expected_ids: list[list[str]]) -> float:
    """
    Calculate mean reciprocal rank (MRR) across multiple queries.
    """
    if not all_retrieved_ids:
        return 0.0
    rrs = [
        calculate_reciprocal_rank(ret_ids, exp_ids)
        for ret_ids, exp_ids in zip(all_retrieved_ids, all_expected_ids)
    ]
    return sum(rrs) / len(rrs)
