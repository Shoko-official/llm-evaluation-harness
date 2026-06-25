#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Try to import yaml, print error if missing
try:
    import yaml
except ImportError:
    print("Error: PyYAML is required to run this script. Please install it using pip.", file=sys.stderr)
    sys.exit(1)

def parse_front_matter(text: str) -> dict | None:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except Exception as e:
        print(f"Warning: Failed to parse YAML front matter: {e}", file=sys.stderr)
        return None

def generate_test_cases(docs_dir: Path) -> list[dict]:
    test_cases = []
    query_counter = 1

    # Search for all markdown files in the specified directory
    for path in sorted(docs_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to read {path.name}: {e}", file=sys.stderr)
            continue

        front_matter = parse_front_matter(text)

        # Determine target document/source ID
        if front_matter and "source_id" in front_matter:
            doc_id = front_matter["source_id"]
        elif front_matter and "claim_id" in front_matter:
            doc_id = front_matter["claim_id"]
        else:
            doc_id = path.stem

        title = front_matter.get("title") if front_matter else None
        
        # 1. Query about the document title/subject
        if title:
            query = f"What is the main topic of the publication '{title}'?"
        else:
            query = f"What is discussed in the document {doc_id}?"
            
        test_cases.append({
            "query_id": f"Q-{query_counter:03d}",
            "query": query,
            "expected_document_ids": [doc_id]
        })
        query_counter += 1

        # 2. Extract headings and formulate questions
        headings = re.findall(r"^##+\s+(.+)$", text, re.MULTILINE)
        for h in headings:
            clean_heading = h.strip()
            # Omit headers that are part of template structure
            if clean_heading.lower() in ("evidence integration", "boundary descriptions", "architecture diagram", "sub-layer components"):
                continue
            if title:
                query = f"What is the role of {clean_heading} in the paper '{title}'?"
            else:
                query = f"What is the role of {clean_heading} in {doc_id}?"
                
            test_cases.append({
                "query_id": f"Q-{query_counter:03d}",
                "query": query,
                "expected_document_ids": [doc_id]
            })
            query_counter += 1

        # 3. Query about review notes if present
        if front_matter and front_matter.get("review_notes"):
            query = f"Summarize the review notes for the source {doc_id}."
            test_cases.append({
                "query_id": f"Q-{query_counter:03d}",
                "query": query,
                "expected_document_ids": [doc_id]
            })
            query_counter += 1

    return test_cases

def main() -> int:
    parser = argparse.ArgumentParser(description="Create evaluation dataset from scientific documents")
    parser.add_argument("--docs-dir", type=str, required=True, help="Directory containing markdown documents/articles")
    parser.add_argument("--output", type=str, required=True, help="Path to write the generated JSON dataset")
    parser.add_argument("--dataset-id", type=str, default="generated_from_docs", help="Dataset identifier")
    
    args = parser.parse_args()
    
    docs_path = Path(args.docs_dir)
    if not docs_path.is_dir():
        print(f"Error: Documents directory not found: {args.docs_dir}", file=sys.stderr)
        return 1
        
    print(f"Scanning documents in {docs_path.resolve()}...")
    test_cases = generate_test_cases(docs_path)
    
    if not test_cases:
        print("Error: No test cases generated from documents.", file=sys.stderr)
        return 1
        
    dataset = {
        "dataset_id": args.dataset_id,
        "test_cases": test_cases
    }
    
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Successfully generated dataset '{args.dataset_id}' with {len(test_cases)} test cases.")
    print(f"Saved dataset file to: {out_path.resolve()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
