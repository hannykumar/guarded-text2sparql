# Error analysis: A3 on the 35 held-back questions

30 of 35 questions scored below 1.0. Each was labelled by hand against the ontology's
real domains and ranges. Run: `results/A3/test/run1`, `qwen2.5-coder:7b` on an A40.

## What the guardrails could still say about the final query

| Final state | Questions | Meaning |
|---|---|---|
| Valid, executed, non-empty, still wrong | 13 | The guardrails cannot see this. Only the reference answer can |
| Empty result (G7) | 8 | Flagged as suspicious; one repair attempted and failed |
| Unparseable (G2) | 5 | Two repairs failed; returned as best effort |
| Invented vocabulary (G4) | 3 | Two repairs failed; the model would not let go of the name |
| Execution error (G6) | 1 | |

So for **21 of 30 failures the system knew something was wrong**, and for 13 it had no
way to know. That distinction is the point of the guardrails: they convert silent
nonsense into either a valid query or a reported problem.

## Cause of failure

| Cause | Count | Example |
|---|---|---|
| **Wrong entity** (a literal where an IRI belongs, or the wrong IRI) | 6 | `?s pv:country "France"` instead of the `Country` IRI; counting `pv:name "Sensor Switches"` when no such literal exists |
| **Wrong property or class** | 6 | "Network expert" modelled as `pv:Hardware ; pv:name "Network expert"` instead of an `Employee` with `pv:areaOfExpertise` |
| **Aggregation or subquery misuse** | 5 | `AVG(?price)` over prices never joined to the supplier's products |
| **Wrong direction** | 4 | `?department pv:memberOf ?employee`; the property runs `Agent -> Department` |
| **Wrong answer shape** | 4 | `SELECT ?result` while the pattern binds `?supplier`, so the answer is always empty; an ASK that tests the opposite of the question |
| **Unparseable after two repairs** | 3 | `pv:width_mm(?hardware)`, calling a property as a function |
| **Wrong ORDER BY / LIMIT** | 1 | "top 10 % of widths" became `LIMIT 10` |
| **Missing inference** | 1 | `?agent a pv:Agent` returns nothing: instances are typed `Employee`, and the store does no RDFS reasoning |

## What this says

**Entity linking solved the problem it was built for, and exposed the next one.** Where
a question names a person or product, the linker resolves it. But the model still writes
`pv:country "France"` for a country that is an IRI, and no linker was asked to cover
countries and categories. Extending the label index to every typed resource, not only
the ones a mention refers to, is the obvious next step.

**Direction is the model's most systematic mistake.** Four questions used a property
backwards, and the schema card already states every domain and range. A guardrail could
check each triple pattern against them and say "`pv:memberOf` runs Agent to Department,
you have it reversed". That is a deterministic check the code can do and the model
repeatedly cannot, and it is the single most promising addition to G1-G8.

**Four failures were empty answers caused by a variable that is never bound.** A query
selecting `?result` while binding `?supplier` is valid SPARQL, runs fine, and returns
nothing. G7 flags the empty result, but the message says "check the entity IRIs"; it
could instead say "the projected variable ?result appears nowhere in the pattern", which
is again a purely deterministic observation.

**One failure is a modelling mismatch, not a model error.** `?agent a pv:Agent` is
correct RDFS reasoning: `Employee` is a subclass of `Agent`. The store does no
inference, so it returns nothing. Either the store should materialise the hierarchy or
the schema card should say that subclass links are not expanded.
