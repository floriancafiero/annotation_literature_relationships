# Annotation grid

## Unit of annotation

Annotate one relationship at a time. A relationship is a romantic, erotic, sexual, conjugal, desirous, or strongly ambiguous relation between two characters or groups of characters.

Do not annotate ordinary friendship unless the text strongly romanticizes, eroticizes, scandalizes, pathologizes, or codes it as potentially amorous or sexual.

Each novel may contain zero, one, or several annotated relationships.

## Core principle

We annotate here five dimensions: configuration, explicitness, centrality, framing, and outcome. Scholarly interpretation can then be built from combinations of these variables.

Important distinction: `relation_type` describes the **gender configuration of the characters involved**, not the certainty that the relation is romantic or sexual. Ambiguity is handled symmetrically through `explicitness` and `confidence`. For instance, a possibly romantic friendship between two women should be coded as `female_female` plus `coded` or `weak_inference`, not as a separate asymmetric label such as `same_sex_ambiguous`.

## 1. `relation_type`

One label only.

| Label | Definition |
|---|---|
| `female_male` | Relation between one character identified as female and one character identified as male: romantic, conjugal, sexual, adulterous, desirous, or strongly coded as such. |
| `female_female` | Relation between two characters identified as female: romantic, conjugal, sexual, adulterous, desirous, or strongly coded as such. |
| `male_male` | Relation between two characters identified as male: romantic, conjugal, sexual, adulterous, desirous, or strongly coded as such. |
| `mixed_or_multi` | Triangular, collective, or multi-person configuration that cannot be reduced to a single pair, or that mixes several gender configurations. |
| `unknown_gender` | A relation is present, but the gender of one or more participants cannot be reliably determined. |
| `unclear` | A relation candidate is present, but its relational configuration cannot be reliably determined. |

## 2. `explicitness`

One label only.

| Label | Definition |
|---|---|
| `explicit` | The text names, stages, or directly confesses love, desire, sex, marriage, adultery, kisses, or erotic attachment. |
| `coded` | The relation is suggested through euphemism, fascination, jealousy, intense intimacy, repeated symbolic language, or historical codes. |
| `rumor` | The relation mainly exists as gossip, scandal, accusation, reputation, blackmail, or public suspicion. |
| `weak_inference` | A queer or romantic reading is possible but fragile. Use sparingly. |
| `unclear` | The degree of explicitness cannot be determined. |

## 3. `centrality`

One label only.

| Label | Definition |
|---|---|
| `main` | The relationship is central to the novel, the protagonist's trajectory, or the main plot. |
| `secondary` | The relationship is an important subplot or affects the main characters, but is not the main relation. |
| `episode` | A brief adventure, temptation, encounter, confession, memory, or scene. |
| `milieu` | A background element of a social world: salon, brothel, convent, boarding school, decadent circle, theater, etc. |
| `unclear` | Centrality cannot be determined. |

## 4. `framing`

One dominant label only. If two framings are plausible, choose the dominant one and explain the secondary one in `comment`.

| Label | Definition |
|---|---|
| `positive` | The relation is presented as love, solidarity, attachment, care, mutual recognition, or a livable bond. |
| `neutral_ambivalent` | The relation is neither clearly condemned nor clearly valorized, or the judgment remains mixed. |
| `eroticized_exoticized` | The relation is framed as spectacle, sensual curiosity, voyeuristic scene, exotic setting, or erotic ornament. |
| `decadent_sublime` | The relation is morbid, painful, sacrificial, sacred, aestheticized, feverish, cruel, or sublime, without being reducible to moral condemnation or medical pathology. |
| `redemptive_spiritualized` | The relation is framed as salvation, spiritual refuge, healing, purification, compassion, or quasi-religious rescue. |
| `moralized_pathologized` | The relation is associated with vice, sin, degeneration, illness, hysteria, perversion, crime, or moral decline. |
| `comic_caricatural` | The relation or character is framed as ridiculous, grotesque, satirical, or comic. |
| `predatory_or_corrupting` | The relation is framed as emprise, manipulation, initiation into vice, corruption, coercion, or predation. |
| `unclear` | The dominant framing cannot be determined. |

## 5. `outcome`

One label only.

| Label | Definition |
|---|---|
| `stable_or_open` | The relation continues, remains possible, or is not narratively destroyed. |
| `open_contested` | The ending is suspended, disputed, reopened, or undecidable; rival relations or unresolved attachments remain active. |
| `return_to_norm` | Return to marriage, heterosexuality, family order, social respectability, or normative domesticity. |
| `separation_erasure` | The relation ends through separation, disappearance, forgetting, narrative marginalization, or erasure. |
| `social_disgrace` | The relation leads to scandal, reputational ruin, exclusion, blackmail, or public shame. |
| `illness_madness_decline` | The relation is followed by illness, madness, physical decline, moral degradation, or psychological collapse. |
| `fatal_ending` | The relation is followed by a fatal narrative resolution affecting one or more central characters. |
| `unclear` | Outcome cannot be determined. |

## Evidence

The model must provide 1 to 3 pieces of short evidence. Prefer brief paraphrases with chapter/page/section if available. Avoid long quotations. Evidence should support the closed labels, not offer free interpretation.

## Confidence

| Label | Definition |
|---|---|
| `high` | Several convergent textual cues; little doubt. |
| `medium` | Plausible and supported, but some interpretive ambiguity remains. |
| `low` | Fragile; useful for review but not for conservative statistics. |
| `exclude` | The candidate should probably not be counted as an annotated relationship. |

## Recommended analysis strategy

Run at least two analyses:

1. **Broad**: include `high`, `medium`, and perhaps `low` cases.
2. **Conservative**: include only `high` and `medium`, and exclude `weak_inference` unless manually validated.

Either we choose, either we keep both and use this as robustness check (ablation with all different values could also work, we'll see).
