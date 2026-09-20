# Error analysis

Two models, same code, same questions: `qwen2.5-coder:32b` (the headline system) and
`qwen2.5-coder:7b` (the first round, kept in `results-7b/`). Both on one A40.

## Held-back test set, 35 questions

| | 32B | 7B |
|---|---|---|
| Fully correct | **11** | 5 |
| Partly correct | 6 | 2 |
| Wrong | 18 | 28 |
| F1 | **0.386** | 0.170 |

## What the guardrails could still say about a failing query

| Final state of the query | 32B | 7B |
|---|---|---|
| Valid, ran, returned something, still wrong | 21 | 13 |
| Empty result, flagged by G7 | 3 | 8 |
| Unparseable after two repairs | **0** | 5 |
| Invented vocabulary after two repairs | **0** | 3 |
| Execution error | **0** | 1 |

**With the 32B, every mechanical failure is gone.** Nothing returned is unparseable, uses
a name that does not exist, or fails to run. All 24 remaining failures are the system
answering a different question from the one that was asked. That is the clearest single
statement of what the guardrails buy: they eliminate the class of error that code can
detect, and they leave the class that needs understanding.

## What the repair loop did

| | 32B | 7B |
|---|---|---|
| Questions needing at least one repair | 59 of 150 | 156 of 265 |
| Repairs that fixed the reported problem | **24 (41%)** | 29 (19%) |
| Queries passing every check at the end | 113 | 138 of 265 |

**Repairs work twice as often with the bigger model**, and this is why the guardrails
finally move the score. A repair is a conversation: the guardrail says exactly what is
wrong, and the model has to act on it. Told `pv:hasProduct does not exist, here are the
properties that do`, the 7B mostly repeated itself; the 32B rewrites the query.

This is the project's most useful finding, and it inverts the conclusion from the first
round. On the 7B, guardrails cost two extra model calls and changed F1 by nothing
(0.170 to 0.170). On the 32B they take 0.304 to **0.386** and add two fully correct
answers. **Guardrails are not a fix for a weak model; they are a multiplier on a model
good enough to use feedback.**

## Why the remaining 24 still fail

Labelled by hand against the ontology's real domains and ranges. The pattern that
dominated the 7B's failures (inventing names, wrong direction) has largely gone; what
is left is harder.

| Cause | Roughly | Example |
|---|---|---|
| Compound questions assembled wrongly | 9 | "average price per supplier, rounded" needs join, filter, group, average, round — one wrong link and the answer set is wrong |
| Wrong entity where a literal was used | 5 | `pv:country "France"` where the graph holds a country IRI. The linker resolves people and products but was never extended to countries and categories |
| Answer shape | 4 | Returning a name where the reference returns the thing itself, or extra columns |
| Aggregation subtleties | 3 | "top 10 % of widths" became `LIMIT 10` |
| Wrong property or direction | 2 | Down from 4 on the 7B |
| Missing inference | 1 | `?x a pv:Agent` returns nothing: instances are typed `Employee` and the store does no RDFS reasoning |

## What to do next, in order of expected value

1. **Extend entity linking beyond people and products** to countries, categories and
   other typed resources. Five failures are literal-versus-IRI mistakes, and the
   machinery already exists.
2. **A domain/range direction guardrail.** The schema card already knows
   `pv:memberOf` runs Agent to Department; the checker could reject the reverse and say so.
3. **A projection check.** A query selecting `?result` while binding only `?supplier`
   is valid SPARQL that always returns nothing. G7 notices the empty result but blames
   the entity IRIs; it could name the real cause.
4. **Materialise the class hierarchy** in the store, or state in the schema card that
   subclass links are not expanded.
