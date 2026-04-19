# ADR-0027: GCP — Compute: Training & Inference

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on GCP span a wide compute spectrum: Gemini-scale model inference, frontier model training, production serving with autoscaling, serverless GPU inference, and distributed ML workloads requiring Ray. GCP provides unique silicon options (Ironwood TPU) alongside NVIDIA GPU instances. A decision is needed on which GCP compute surface is canonical for each AI workload type.

## Decision

We will use:
- **Ironwood TPU (7th gen, GA Q2 2025)** for high-throughput Gemini-scale inference requiring cost-efficient custom silicon
- **A4 / A4X VMs** (NVIDIA Blackwell B200/GB200) for frontier model training and high-performance inference workloads requiring NVIDIA silicon
- **GKE + GKE Inference Gateway** (GA) for production model serving — intelligent load balancing, auto-scaling, and GPU utilisation optimisation
- **Cloud Run + GPUs** (GA) for serverless GPU inference — scale-to-zero, low-ops event-driven model serving
- **Cluster Director** (GA) for large-scale distributed training across thousands of GPU/TPU accelerators
- **RayTurbo on GKE** (GA) for distributed ML workloads (training, tuning, batch inference) requiring Ray

Agent workloads use Agent Engine (see ADR-0023) — no separate compute decision needed.

## Rationale

1. **Ironwood TPU for Gemini-scale inference** — purpose-built for large-scale model serving, Ironwood provides higher throughput and lower cost per token than GPU alternatives for Gemini-family models. The 7th generation is optimised for the inference workloads that constitute the majority of AI compute cost in production.
2. **A4/A4X for NVIDIA-specific needs** — custom CUDA kernels, NVIDIA-specific frameworks (TensorRT, cuBLAS), or frontier model training requiring B200/GB200 Blackwell capabilities require A4/A4X instances. Do not default to GPU when TPU covers the workload.
3. **GKE Inference Gateway for production serving control** — topology-aware routing across models, request-level GPU utilisation optimisation, and scale-to-zero for idle models make GKE Inference Gateway the correct production serving tier for teams requiring full orchestration control.
4. **Cloud Run + GPUs for low-ops inference** — scale-to-zero economics and zero cluster management for event-driven or intermittent inference workloads. Default to Cloud Run + GPUs before escalating to GKE Inference Gateway.
5. **RayTurbo for distributed ML** — 4.5× faster data processing and 50% fewer nodes for serving versus standard Ray make RayTurbo on GKE the choice for Ray-based distributed workloads at GCP scale.

## Consequences

### Positive
- Cloud Run + GPUs (scale-to-zero) eliminates idle GPU cost for intermittent inference workloads — significant cost reduction vs always-on GKE GPU nodes
- GKE Inference Gateway's topology-aware routing maximises GPU utilisation across heterogeneous node pools
- Cluster Director simplifies thousand-node training cluster management with Slurm support for HPC-familiar teams

### Negative / Trade-offs
- Ironwood TPU requires Google's serving frameworks (JAX, PyTorch/XLA) — not all model architectures compile cleanly to TPU; validate compatibility before committing to TPU-based serving
- A4/A4X VM availability is constrained in some regions — reserve capacity well in advance for planned large training runs
- Cloud Run + GPUs has a memory limit per container (currently 32GB) — large models (>20B parameters) may not fit; escalate to GKE for large model serving

### Risks
- [RISK: MED] TPU compilation errors surface late in the model serving pipeline — validate TPU compatibility during model development, not at deployment time
- [RISK: MED] Cluster Director for large-scale training is GA but relatively new — test failure recovery and topology-aware scheduling thoroughly before running multi-week training jobs
- [RISK: LOW] RayTurbo is GKE-managed Ray — pin Ray version in the RayCluster spec; Ray version upgrades can break distributed training code

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Standard Cloud Run (no GPU) | No GPU support; use for CPU-only inference microservices; GPU is required for LLM serving |
| Raw GCE GPU VMs without GKE | High ops burden for health checks, scaling, and job scheduling; use GKE Inference Gateway or Cloud Run + GPUs instead |
| Cloud Batch for training | Viable for simple job queues; less ML-native than GKE + Cluster Director for large-scale distributed training |
| Standard Ray on GKE (not RayTurbo) | 4.5× slower data processing; use RayTurbo specifically on GKE for ML workloads |

## Implementation Notes

1. Cloud Run + GPUs: `gcloud run deploy --gpu=1 --gpu-type=nvidia-l4 --no-cpu-throttling` — specify `--concurrency=1` for single-inference-at-a-time models
2. GKE Inference Gateway: deploy `InferencePool` and `InferenceModel` resources via Kubernetes CRDs; configure `targetPortalMetricsSpec` for custom autoscaling metrics
3. RayTurbo: create `RayCluster` CR with `rayVersion: turbo`; use `ray.init(address="ray://[cluster-head]:10001")` from training code
4. Cluster Director: provision via GCP console or Terraform (`google_cluster_director_cluster` resource); configure topology-aware job scheduling for GPU interconnect locality
5. A4/A4X: request quota 3–4 weeks in advance; use committed use discounts for sustained training workloads

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
