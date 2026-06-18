# LLM Annotation: relationships between characters

Framework for LLM-assisted annotation of romantic, erotic, conjugal, desirous and queer-coded relationships in late nineteenth- and early twentieth-century novels.

The repository is designed for a reproducible workflow on a corpus of about 400 novels:

1. create a small human ground truth, for instance 10 novels;
2. run the same annotation prompt through several OpenRouter models;
3. benchmark relation detection and closed-category annotation;
4. inspect disagreements and refine the codebook before scaling up.

## What is annotated?

The unit of annotation is **one relationship**: a romantic, sexual, conjugal, desirous, or strongly ambiguous relation between two characters or groups of characters. Ordinary friendship is not annotated unless the text strongly eroticizes, romanticizes, scandalizes, or codes the relation.

Each relation receives five closed variables:

- `relation_type`
- `explicitness`
- `centrality`
- `framing`
- `outcome`

It also receives short evidence, a confidence level, and a brief comment.

`relation_type` describes the gender configuration of the participants (`female_male`, `female_female`, `male_male`, `mixed_or_multi`, `unknown_gender`, `unclear`). It does not encode whether the relation is certainly romantic or sexual.

## Prompt architecture

The codebook is the single source of truth for label definitions. The runner reads `codebook/annotation_grid.md` and injects it into the model context at runtime, after the stable system prompt and before the user prompt.

This keeps the prompts short and avoids maintaining duplicate definitions in several files:

- `prompts/system_prompt.md` gives the general annotation role and decision principles;
- `codebook/annotation_grid.md` defines the annotation unit and all labels;
- `prompts/user_prompt_template.md` supplies the novel metadata and text.

For reproducibility, each output record logs the path and SHA-256 hash of the schema, codebook, system prompt, and user template used for the request.

## Repository layout

```text
codebook/annotation_grid.md              Human-readable annotation grid
schemas/novel_annotation.schema.json     JSON Schema used for structured output
prompts/system_prompt.md                 Stable system prompt
prompts/user_prompt_template.md          User prompt template for a novel
src/annotate_openrouter.py               OpenRouter annotation runner
src/evaluate.py                          Benchmark predictions against gold data
src/validate_jsonl.py                    Pre-flight checks for corpus/gold/predictions
config/models.example.yaml               Example benchmark configuration
data/corpus_sample.jsonl                 Example input corpus format
data/ground_truth_sample.jsonl           Example ground truth format
```

## Installation

```bash
git clone https://github.com/floriancafiero/annotation_literature_relationships.git
cd annotation_literature_relationships
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

## Input format

The corpus is a JSONL file, one novel per line:

```json
{"novel_id":"vivien_1904_femme","title":"Une femme m'apparut","author":"Renée Vivien","year":1904,"text":"Full text or benchmark excerpt..."}
```

For the benchmark on 10 novels, use exactly the same text for all models. If a full novel is too long for some models, prepare a fixed benchmark excerpt or fixed chunked representation before running the comparison. Do not let each model receive a different truncation.

## Configure models

Do not edit the example file directly. Copy it and record the exact model slugs used for the benchmark:

```bash
cp config/models.example.yaml config/models.local.yaml
```

Then edit `config/models.local.yaml`. Keep the same generation parameters across models for the main comparison.

## Pre-flight checks

Before running a paid benchmark, validate the corpus and the gold file:

```bash
python src/validate_jsonl.py \
  --corpus data/corpus_sample.jsonl \
  --gold data/ground_truth_sample.jsonl \
  --schema schemas/novel_annotation.schema.json
```

This catches invalid JSONL, missing `novel_id` / `text`, duplicate novel ids in the corpus, and gold annotations that do not match the schema.

## Run annotation

```bash
python src/annotate_openrouter.py \
  --input data/corpus_sample.jsonl \
  --output runs/predictions.jsonl \
  --models-config config/models.local.yaml \
  --schema schemas/novel_annotation.schema.json \
  --codebook codebook/annotation_grid.md \
  --max-chars 120000
```

By default, the script refuses to silently truncate texts longer than `--max-chars`. Use `--allow-truncate` only for documented experiments where the same fixed truncation is intended for all models.

The script records, for each novel and model: model slug, generation parameters, SHA-256 hash of the input text, schema/codebook/prompt hashes, request body, raw response, parsed JSON annotation, and JSON-schema validation status.

## Reproducibility settings

The default configuration is conservative:

```yaml
temperature: 0
top_p: 1
seed: 42
top_k: 1
```

OpenRouter documents `temperature`, `top_p`, `top_k`, and `seed` as request parameters, but also notes that unsupported parameters may be ignored by some providers or models, for instance `top_k` for OpenAI models. Therefore the repository logs the full request and raw response for every run. Do not rely on a single parameter as a guarantee of bitwise determinism.

## Evaluate against ground truth

```bash
python src/evaluate.py \
  --predictions runs/predictions.jsonl \
  --gold data/ground_truth_sample.jsonl \
  --output runs/evaluation_summary.json
```

The evaluator performs approximate relation matching by normalized character-name overlap, then reports relation detection precision/recall/F1 and per-field accuracy among matched relations.
