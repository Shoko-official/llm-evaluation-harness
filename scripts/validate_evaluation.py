from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

def fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)

def load_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"Failed to parse JSON from {path}: {e}")

def validate_input_file(input_path: Path, schema_path: Path) -> dict:
    schema = load_json(schema_path)
    data = load_json(input_path)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        fail(f"Input validation error for {input_path.name}: {e.message}")
    return data

def validate_output_file(output_path: Path, schema_path: Path) -> dict:
    schema = load_json(schema_path)
    data = load_json(output_path)
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        fail(f"Output validation error for {output_path.name}: {e.message}")
    return data

def validate_alignment(input_data: dict, output_data: dict) -> None:
    # 1. Dataset ID alignment
    if input_data.get("dataset_id") != output_data.get("dataset_id"):
        fail(
            f"Dataset ID mismatch: input dataset is '{input_data.get('dataset_id')}', "
            f"but output results dataset is '{output_data.get('dataset_id')}'"
        )
    
    # 2. Check query alignment
    input_queries = {tc["query_id"] for tc in input_data.get("test_cases", [])}
    output_queries = {res["query_id"] for res in output_data.get("results", [])}
    
    missing_queries = input_queries - output_queries
    if missing_queries:
        fail(f"Output is missing results for query IDs: {', '.join(sorted(missing_queries))}")
        
    extra_queries = output_queries - input_queries
    if extra_queries:
        fail(f"Output contains results for unknown query IDs: {', '.join(sorted(extra_queries))}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Validate evaluation inputs and outputs against schemas")
    parser.add_argument("--input", type=str, help="Path to the evaluation input JSON dataset file")
    parser.add_argument("--output", type=str, help="Path to the evaluation output JSON results file")
    parser.add_argument("--input-schema", type=str, help="Path to the input JSON schema")
    parser.add_argument("--output-schema", type=str, help="Path to the output JSON schema")
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    
    input_schema_path = Path(args.input_schema) if args.input_schema else root_dir / "evaluation" / "schemas" / "input.json"
    output_schema_path = Path(args.output_schema) if args.output_schema else root_dir / "evaluation" / "schemas" / "output.json"
    
    input_data = None
    output_data = None
    
    if args.input:
        input_data = validate_input_file(Path(args.input), input_schema_path)
        print(f"Successfully validated input file: {args.input}")
        
    if args.output:
        output_data = validate_output_file(Path(args.output), output_schema_path)
        print(f"Successfully validated output file: {args.output}")
        
    if input_data and output_data:
        validate_alignment(input_data, output_data)
        print("Input and output alignment validation successful.")

if __name__ == "__main__":
    main()
