# ADR-0009: Azure — Compute: Training & Inference

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on Azure span a wide compute spectrum: large-scale distributed training on GPU clusters, production online model serving with autoscaling, low-ops inference APIs, and edge/developer scenarios. A single compute tier is insufficient. A decision is needed on which Azure compute surface is canonical for each workload type.

## Decision

We will use:
- **Azure Kubernetes Service (AKS)** for production model serving requiring full orchestration control (multi-model, canary, custom autoscaling)
- **Azure Container Apps (ACA)** for low-ops inference APIs and event-driven serving (scale-to-zero, sidecar patterns)
- **Azure Batch + NC/ND-series GPU VMs** for distributed training workloads requiring full GPU control (A100, H100)
- **Foundry Local** (Preview) for on-device and edge inference, and for developer testing without cloud round-trips

Foundry Agent Service / Hosted Agents (see ADR-0005) handles agent compute — no separate compute decision needed for agent workloads.

## Rationale

1. **AKS for production serving control** — multi-model inference clusters, canary deployments, and custom HPA policies require Kubernetes-level control. Azure ML Managed Endpoints (built on AKS) is the first choice for single-model serving; raw AKS is used when Managed Endpoints constraints are binding.
2. **ACA for low-ops APIs** — scale-to-zero economics, minimal DevOps overhead, and sidecar-based model serving (e.g., local embedding sidecar) make ACA the right tier for inference APIs without SLA requirements demanding AKS-level control.
3. **Azure Batch + GPU VMs for training** — training workloads requiring full GPU control (DeepSpeed, PyTorch FSDP, custom CUDA kernels) are best run on NC/ND-series VMs via Azure Batch. HyperPod equivalent on Azure is AML compute clusters.
4. **Foundry Local for edge** — Microsoft's on-device execution runtime for Foundry models addresses offline and edge scenarios without cloud dependency.

## Consequences

### Positive
- Clear compute tier selection criteria prevents over-engineering (AKS for APIs that should run on ACA)
- ACA's scale-to-zero eliminates idle GPU/CPU cost for intermittent inference workloads
- AML compute clusters integrate directly with Azure ML training jobs and pipeline steps

### Negative / Trade-offs
- AKS adds significant operational complexity — only use when Managed Endpoints or ACA constraints force it
- Azure Batch GPU quotas require pre-approval for A100/H100 SKUs — plan quota requests 2–4 weeks in advance
- Foundry Local is Preview — do not use in production pipelines; developer and edge PoC use only

### Risks
- [RISK: MED] GPU VM quota limits can block training jobs — submit quota increase requests before project kick-off, not when blocked
- [RISK: LOW] ACA has a 4 vCPU / 8 GiB memory ceiling per container — verify inference model fits within ACA limits before choosing it over AKS

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Azure Container Instances (ACI) | No autoscaling, no GPU support at scale; suitable only for one-off batch jobs |
| Raw VM Scale Sets | High ops burden — health checks, rolling updates, and autoscaling all custom; use AKS or ACA instead |
| Azure Spring Apps | Java-ecosystem service; not applicable to ML inference workloads |
| Azure ML Managed Endpoints only | Managed Endpoints are the first choice for single-model REST serving; raw AKS is the fallback for multi-model or custom autoscaling needs |

## Implementation Notes

1. Default inference API choice: Azure ML Managed Online Endpoint → ACA → AKS (escalate only when lower tier is insufficient)
2. Use NC A100 v4 or ND H100 v5 series for training; request quota 3 weeks before project start
3. ACA: use `--scale-rule-http` with appropriate concurrency limits; add KEDA scaling rules for queue-based inference
4. For AKS model serving: use NVIDIA Triton Inference Server or TorchServe as the model runtime; KEDA for autoscaling on custom metrics
5. Foundry Local: use for developer inner loop testing and edge PoC; do not expose to production traffic

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
