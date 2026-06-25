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

import re

def calculate_citation_accuracy(generated_answer: str, cited_document_ids: list[str]) -> float:
    """
    Calculate citation accuracy (F1 score) based on the overlap between
    document IDs mentioned in the generated answer text and the cited_document_ids list.
    
    Extracts patterns matching DOC-\\w+ from the text.
    """
    if not generated_answer:
        return 1.0 if not cited_document_ids else 0.0
        
    # Extract mentioned document IDs (case-insensitive search)
    mentioned = set(re.findall(r"DOC-\w+", generated_answer.upper()))
    cited = {c.upper() for c in cited_document_ids}
    
    if not mentioned:
        return 1.0 if not cited else 0.0
        
    if not cited:
        return 0.0
        
    intersection = mentioned & cited
    precision = len(intersection) / len(cited)
    recall = len(intersection) / len(mentioned)
    
    if precision + recall == 0:
        return 0.0
        
    return 2.0 * precision * recall / (precision + recall)

def calculate_average_ttft(ttfts: list[float]) -> float:
    """
    Calculate average Time-To-First-Token (TTFT).
    """
    if not ttfts:
        return 0.0
    return sum(ttfts) / len(ttfts)

def calculate_throughput(total_tokens: int, total_duration_seconds: float) -> float:
    """
    Calculate throughput in tokens per second.
    """
    if total_duration_seconds <= 0.0:
        return 0.0
    return total_tokens / total_duration_seconds

def calculate_tool_call_accuracy(actual_tools: list[str], expected_tools: list[str]) -> float:
    """
    Calculate F1 score of actual vs expected tool calls.
    """
    if not expected_tools:
        return 1.0 if not actual_tools else 0.0
    if not actual_tools:
        return 0.0
    
    actual_set = set(actual_tools)
    expected_set = set(expected_tools)
    intersection = actual_set & expected_set
    
    precision = len(intersection) / len(actual_set)
    recall = len(intersection) / len(expected_set)
    
    if precision + recall == 0.0:
        return 0.0
        
    return 2.0 * precision * recall / (precision + recall)

def calculate_instruction_diversity(instructions: list[str]) -> float:
    """
    Calculate instruction diversity ratio (unique instructions / total instructions).
    """
    if not instructions:
        return 1.0
    unique_instructions = set(instructions)
    return len(unique_instructions) / len(instructions)

def calculate_sample_relevance(instruction: str, output: str) -> float:
    """
    Calculate lexical overlap-based relevance score between instruction and output.
    """
    if not instruction or not output:
        return 0.0
    inst_words = set(re.findall(r"\w+", instruction.lower()))
    out_words = set(re.findall(r"\w+", output.lower()))
    if not inst_words:
        return 1.0
    overlap = len(inst_words & out_words)
    return min(1.0, (overlap / len(inst_words)) * 2.0)

def calculate_grammatical_correctness(text: str) -> float:
    """
    Calculate a syntax/format sanity score based on punctuation and repeating words.
    """
    if not text:
        return 0.0
    score = 1.0
    if not text[0].isalnum():
        score -= 0.1
    if text[-1] not in {".", "!", "?", '"', "'", "`"}:
        score -= 0.2
    words = text.split()
    if len(words) > 0:
        repeats = sum(1 for w1, w2 in zip(words, words[1:]) if w1.lower() == w2.lower())
        score -= min(0.4, (repeats / len(words)) * 2.0)
    return max(0.0, score)

def calculate_complexity_score(instruction: str) -> float:
    """
    Calculate instruction complexity based on word count and logical connectors.
    """
    if not instruction:
        return 0.0
    words = instruction.split()
    length_score = min(1.0, len(words) / 30.0)
    
    connectors = {"if", "then", "else", "and", "or", "but", "because", "when", "how", "why"}
    connector_count = sum(1 for w in words if w.lower() in connectors)
    connector_score = min(1.0, connector_count / 5.0)
    
    return 0.6 * length_score + 0.4 * connector_score



