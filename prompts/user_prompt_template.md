Annotate the following novel using the provided codebook and JSON schema.

Use this workflow internally:
1. Identify candidate relations.
2. Exclude ordinary social relations that do not meet the codebook definition.
3. Annotate each retained relation with exactly one label for each closed field.
4. Use the evidence and comment fields to make the annotation auditable.
5. If no relation qualifies, return an empty `relations` array.

Order relations by narrative importance, with the most central relations first. Use relation identifiers `R1`, `R2`, `R3`, and so on.

Novel metadata:
- novel_id: {novel_id}
- title: {title}
- author: {author}
- year: {year}

Novel text:

```text
{text}
```
