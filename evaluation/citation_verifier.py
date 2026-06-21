"""
Citation grounding accuracy verifier.
"""
from __future__ import annotations

def verify_citation_grounding(cited_ids: list[str], retrieved_ids: list[str]) -> float:
    """
    Verify if the cited documents are grounded in the retrieved documents.
    
    Returns the grounding ratio: (number of cited documents that were actually retrieved) / (total number of cited documents).
    Returns 1.0 if no documents were cited.
    """
    if not cited_ids:
        return 1.0
        
    cited_set = {c.upper() for c in cited_ids}
    retrieved_set = {r.upper() for r in retrieved_ids}
    
    grounded = cited_set & retrieved_set
    return len(grounded) / len(cited_set)
