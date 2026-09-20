# Measurement environment

Two models, everything else identical. Runs within one setup are bit-identical, so each
configuration was run once with the 32B (the 7B round ran three times each and every
repeat matched exactly).

| | |
|---|---|
| Headline model | `qwen2.5-coder:32b`, Apache-2.0 |
| Comparison model | `qwen2.5-coder:7b`, digest `dae161e27b0e`, Apache-2.0 (results in `results-7b/`) |
| Inference | Ollama 0.12.3 on one NVIDIA A40 (46 GB), CITEC GPU cluster, Bielefeld |
| Speed | 32B: 24.8 tokens/s, median 9.9 s per question. 7B: 92 tokens/s, median 4.2 s |
| Store | Apache Jena Fuseki 5.1.0 in Docker, on the laptop, reached over an SSH tunnel |
| Dataset | CK25 at commit `cb928b2f` (v1.2.0) |
| Scorer | `text2sparql-client` 2.1.0 |
| Temperature | 0 |

The pipeline, the triple store and all scoring ran on a laptop; only inference ran on the
cluster, reached through an SSH tunnel. Nothing was left on the cluster afterwards.

**Determinism.** Repeats on fixed hardware are identical. That does *not* hold across
hardware: the same model and code on laptop CPU answered 2 of 15 dev questions
differently from the A40. Floating-point differences between CPU and GPU kernels are
enough to change a borderline generation, so results reproduce on identical hardware,
not across hardware.
