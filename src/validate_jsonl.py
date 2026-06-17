#!/usr/bin/env python3
"""Validate corpus, gold, and prediction JSONL files for the annotation workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

import jsonschema


def read_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path: str | Path) -> Iterable[tuple[int, Dict[str, Any]]]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}: line {line_number} is not a JSON object")
            yield line_number, record


def validate_corpus(path: str | Path) -> int:
    count = 0
    ids: set[str] = set()
    for line_number, record in read_jsonl(path):
        count += 1
        novel_id = record.get("novel_id")
        text = record.get("text")
        if not isinstance(novel_id, str) or not novel_id.strip():
            raise ValueError(f"{path}: line {line_number}: missing non-empty novel_id")
        if novel_id in ids:
            raise ValueError(f"{path}: line {line_number}: duplicate novel_id {novel_id!r}")
        ids.add(novel_id)
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"{path}: line {line_number}: missing non-empty text")
    return count


def validate_annotation_file(path: str | Path, schema: Dict[str, Any], *, prediction_mode: bool = False) -> int:
    count = 0
    for line_number, record in read_jsonl(path):
        count += 1
        annotation = record.get("annotation") if prediction_mode else record
        if prediction_mode and annotation is None:
            # Failed prediction records are allowed but should expose an error flag.
            if record.get("ok") is not False:
                raise ValueError(f"{path}: line {line_number}: missing annotation without ok=false")
            continue
        try:
            jsonschema.validate(annotation, schema)
        except jsonschema.ValidationError as exc:
            raise ValueError(f"{path}: line {line_number}: schema validation failed: {exc.message}") from exc
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default="schemas/novel_annotation.schema.json")
    parser.add_argument("--corpus", help="Corpus JSONL to check")
    parser.add_argument("--gold", help="Gold annotation JSONL to validate against the schema")
    parser.add_argument("--predictions", help="Prediction JSONL to validate when annotations are present")
    args = parser.parse_args()

    schema = read_json(args.schema)
    if args.corpus:
        n = validate_corpus(args.corpus)
        print(f"OK corpus: {args.corpus} ({n} records)")
    if args.gold:
        n = validate_annotation_file(args.gold, schema, prediction_mode=False)
        print(f"OK gold: {args.gold} ({n} records)")
    if args.predictions:
        n = validate_annotation_file(args.predictions, schema, prediction_mode=True)
        print(f"OK predictions: {args.predictions} ({n} records)")


if __name__ == "__main__":
    main()
