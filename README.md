# Annotation LLM Violette

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

The two corrections from the pilot annotation of Renée Vivien's *Une femme m'apparut* are included:

- `framing = decadent_sublime` for morbid, painful, sacred, or aestheticized queer passion that is not simply condemned as vice or pathology;
- `outcome = open_contested` for endings that remain suspended, disputed, or reopened rather than clearly happy, punitive, or heteronormative.

## Repository layout

```text
codebook/annotation_grid.md              Human-readable annotation grid
schemas/novel_annotation.schema.json     JSON Schema used for structured output
prompts/system_prompt.md                 Stable system prompt
prompts/user_prompt_template.md          User prompt template for a novel
src/annotate_openrouter.py               OpenRouter annotation runner
src/evaluate.py                          Benchmark predictions against gold data
config/models.example.yaml               Example benchmark configuration
data/corpus_sample.jsonl                 Example input corpus format
data/ground_truth_sample.jsonl           Example ground truth format
```

## Installation

```bash
git clone https://github.com/floriancafiero/annotation_llm_violette.git
cd annotation_llm_violette
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

For the benchmark on 10 novels, use exactly the same text for all models. If a full novel is too long for some models, prepare a fixed benchmark excerpt or fixed chunked representation before running the comparison.

## Run annotation

```bash
python src/annotate_openrouter.py \
  --input data/corpus_sample.jsonl \
  --output runs/predictions.jsonl \
  --models-config config/models.example.yaml \
  --schema schemas/novel_annotation.schema.json \
  --max-chars 120000
```

The script records, for each novel and model: model slug, generation parameters, SHA-256 hash of the input text, request body, raw response, parsed JSON annotation, and JSON-schema validation status.

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

For a serious paper, manually inspect all unmatched same-sex and ambiguous same-sex relations, because these are likely rare and substantively important.
