# Measurement environment

All numbers in this directory come from one setup. Runs within it are bit-identical.

| | |
|---|---|
| Model | `qwen2.5-coder:7b`, digest `dae161e27b0e`, Apache-2.0 |
| Inference | Ollama 0.12.3 on one NVIDIA A40 (46 GB), CITEC GPU cluster |
| Store | Apache Jena Fuseki 5.1.0 in Docker, local |
| Dataset | CK25 at commit `cb928b2f` (v1.2.0) |
| Scorer | `text2sparql-client` 2.1.0 |
| Temperature | 0 |

**Determinism.** The three runs of each configuration are identical, so the reported
range is zero. That holds *within* this setup only: the same model and code on laptop
CPU produced different answers for 2 of 15 dev questions. Floating-point differences
between CPU and GPU kernels are enough to change a borderline generation, so results
are reproducible on identical hardware, not across hardware.
