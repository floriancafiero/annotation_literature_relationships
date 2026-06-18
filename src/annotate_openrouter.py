#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

import jsonschema
import requests
import yaml
from tqdm import tqdm

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(read_text(path))


def read_jsonl(path: str | Path) -> Iterable[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc


def append_jsonl(path: str | Path, record: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_system_context(system_prompt: str, codebook: str) -> str:
    return (
        system_prompt.strip()
        + "\n\nBEGIN CODEBOOK\n"
        + codebook.strip()
        + "\nEND CODEBOOK\n"
    )


def format_prompt(template: str, novel: Dict[str, Any], max_chars: int, allow_truncate: bool) -> tuple[str, bool]:
    text = novel.get("text", "")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Novel {novel.get('novel_id')} has empty or missing text")
    truncated = False
    if len(text) > max_chars:
        if not allow_truncate:
            raise ValueError(
                f"Novel {novel.get('novel_id')} has {len(text)} characters, above --max-chars={max_chars}. "
                "Use --allow-truncate only when fixed truncation is intended and documented."
            )
        text = text[:max_chars]
        truncated = True
    return template.format(
        novel_id=novel.get("novel_id", ""),
        title=novel.get("title", ""),
        author=novel.get("author", ""),
        year=novel.get("year", ""),
        text=text,
    ), truncated


def build_request(
    model: str,
    system_context: str,
    user_prompt: str,
    schema: Dict[str, Any],
    params: Dict[str, Any],
    use_json_schema: bool,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_context},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": params.get("temperature", 0),
        "top_p": params.get("top_p", 1),
        "seed": params.get("seed", 42),
        "max_tokens": params.get("max_tokens", 4096),
        "frequency_penalty": params.get("frequency_penalty", 0),
        "presence_penalty": params.get("presence_penalty", 0),
    }
    if params.get("top_k") is not None:
        body["top_k"] = params["top_k"]
    if use_json_schema:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "novel_relationship_annotation",
                "strict": True,
                "schema": schema,
            },
        }
    else:
        body["response_format"] = {"type": "json_object"}
    return body


def call_openrouter(api_key: str, body: Dict[str, Any], app_cfg: Dict[str, Any], timeout: int, retries: int) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if app_cfg.get("http_referer"):
        headers["HTTP-Referer"] = app_cfg["http_referer"]
    if app_cfg.get("title"):
        headers["X-OpenRouter-Title"] = app_cfg["title"]

    last_error: str | None = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # noqa: BLE001
            last_error = repr(exc)
            if attempt >= retries:
                break
            time.sleep(2**attempt)
    raise RuntimeError(f"OpenRouter request failed after {retries + 1} attempts: {last_error}")


def extract_content(response: Dict[str, Any]) -> str:
    return response["choices"][0]["message"]["content"]


def parse_model_json(content: str) -> tuple[Dict[str, Any] | None, str | None]:
    try:
        return json.loads(content), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def validate_annotation(annotation: Dict[str, Any] | None, schema: Dict[str, Any]) -> str | None:
    if annotation is None:
        return "no parsed annotation"
    try:
        jsonschema.validate(annotation, schema)
        return None
    except jsonschema.ValidationError as exc:
        return exc.message


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--models-config", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--codebook", default="codebook/annotation_grid.md")
    parser.add_argument("--system-prompt", default="prompts/system_prompt.md")
    parser.add_argument("--user-template", default="prompts/user_prompt_template.md")
    parser.add_argument("--max-chars", type=int, default=120000)
    parser.add_argument("--allow-truncate", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--no-json-schema", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Missing OPENROUTER_API_KEY", file=sys.stderr)
        sys.exit(1)

    config = yaml.safe_load(read_text(args.models_config))
    models: List[str] = config.get("models", [])
    params: Dict[str, Any] = config.get("parameters", {})
    app_cfg: Dict[str, Any] = config.get("openrouter", {})
    if not models:
        raise ValueError("No models found in config")

    schema = read_json(args.schema)
    system_prompt = read_text(args.system_prompt)
    codebook = read_text(args.codebook)
    user_template = read_text(args.user_template)
    system_context = build_system_context(system_prompt, codebook)
    novels = list(read_jsonl(args.input))
    if args.limit is not None:
        novels = novels[: args.limit]

    schema_sha256 = sha256_text(json.dumps(schema, ensure_ascii=False, sort_keys=True))
    codebook_sha256 = sha256_text(codebook)
    system_prompt_sha256 = sha256_text(system_prompt)
    user_template_sha256 = sha256_text(user_template)

    for novel in tqdm(novels, desc="novels"):
        user_prompt, truncated = format_prompt(novel, args.max_chars, args.allow_truncate)
        for model in models:
            request_body = build_request(
                model=model,
                system_context=system_context,
                user_prompt=user_prompt,
                schema=schema,
                params=params,
                use_json_schema=not args.no_json_schema,
            )
            record: Dict[str, Any] = {
                "novel_id": novel.get("novel_id"),
                "title": novel.get("title"),
                "author": novel.get("author"),
                "year": novel.get("year"),
                "model": model,
                "started_at_utc": dt.datetime.utcnow().isoformat() + "Z",
                "input_sha256": sha256_text(novel.get("text", "")),
                "input_num_chars": len(novel.get("text", "")),
                "truncated": truncated,
                "parameters": params,
                "schema_path": args.schema,
                "schema_sha256": schema_sha256,
                "codebook_path": args.codebook,
                "codebook_sha256": codebook_sha256,
                "system_prompt_path": args.system_prompt,
                "system_prompt_sha256": system_prompt_sha256,
                "user_template_path": args.user_template,
                "user_template_sha256": user_template_sha256,
                "request": request_body,
            }
            try:
                raw_response = call_openrouter(api_key, request_body, app_cfg, args.timeout, args.retries)
                content = extract_content(raw_response)
                annotation, parse_error = parse_model_json(content)
                validation_error = validate_annotation(annotation, schema)
                record.update(
                    {
                        "raw_response": raw_response,
                        "raw_content": content,
                        "annotation": annotation,
                        "parse_error": parse_error,
                        "validation_error": validation_error,
                        "ok": parse_error is None and validation_error is None,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                record.update({"ok": False, "runtime_error": repr(exc)})
            record["finished_at_utc"] = dt.datetime.utcnow().isoformat() + "Z"
            append_jsonl(args.output, record)


if __name__ == "__main__":
    main()
