# guarded-text2sparql

Turns a plain-English question into a SPARQL query over eccenca's **CK25** corporate knowledge graph.
An LLM proposes the query; deterministic guardrails check it before it is returned. Evaluated with the
official [TEXT2SPARQL](https://text2sparql.aksw.org/) challenge client.

> **Status:** early development: data and triple store. Progress: [issues](../../issues).

## Quickstart (so far)

Needs Docker and [uv](https://docs.astral.sh/uv/).

```bash
make data    # download CK25 at a pinned commit (queries.ttl is deleted on arrival)
make store   # start Oxigraph on :7878
make load    # load prod-inst.ttl only
make truth   # all 50 reference queries must return results
make test
```

## Data and credits

This repository does **not** contain the dataset; `scripts/get_data.sh` downloads it.

- **CK25:** Tramp, S. and Pietzsch, R. (eccenca GmbH). *The CK25 Corporate Knowledge Reference Dataset for
  Benchmarking Text 2 SPARQL Question Answering Approaches.* 2025.
  [doi:10.5281/zenodo.16912605](https://doi.org/10.5281/zenodo.16912605),
  [github.com/eccenca/ck25-dataset](https://github.com/eccenca/ck25-dataset), pinned at commit
  `cb928b2f` (v1.2.0). Licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
  No endorsement by eccenca is implied.
- **Scorer:** [text2sparql-client](https://github.com/AKSW/text2sparql-client) 2.1.0, Apache-2.0.

## Licence

Code: [Apache-2.0](LICENSE).
