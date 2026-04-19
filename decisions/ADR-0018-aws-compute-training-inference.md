# ADR-0018: AWS — Compute: Training & Inference

**Date:** 2026-04-19
**Status:** Proposed
**Domain:** [mlops] [infra]
**Author:** AI Architect
**Supersedes:** N/A
**Superseded by:** N/A

---

## Context

AI workloads on AWS span a wide compute spectrum: large-scale distributed foundation model training, cost-efficient production inference, custom model serving with autoscaling, and batch inference jobs. AWS provides both general-purpose GPU instances and custom ML silicon (Trainium, Inferentia). A decision is needed on which compute surface is canonical for each AI workload type.

## Decision

We will use:
- **SageMaker HyperPod** for large-scale distributed training — self-healing clusters, checkpointless training, and elastic auto-scaling
- **AWS Trainium 2 + Neuron SDK** for cost-efficient custom silicon training at scale (alternative to NVIDIA H100 for supported frameworks)
- **AWS Inferentia 2 + Neuron SDK** for high-throughput, low-cost production LLM inference (alternative to GPU-based serving)
- **Amazon EKS** for custom model serving infrastructure requiring full orchestration control
- **EC2 P5 (H100) / G6 (L40S) instances** for workloads requiring NVIDIA silicon specifically (custom CUDA kernels, frameworks not yet Neuron-compatible)
- **AWS Batch** for distributed training jobs and large-scale batch inference without persistent cluster management

## Rationale

1. **SageMaker HyperPod reduces training downtime by 80%+** — checkpointless training (automatic resume on node failure without explicit checkpoint code) and self-healing clusters eliminate the primary cost driver in large-scale training: wasted GPU-hours on failed jobs.
2. **Trainium 2 / Inferentia 2 for cost efficiency** — AWS custom silicon provides significantly lower cost per token at production inference scale compared to equivalent NVIDIA GPU instances. Neuron SDK supports PyTorch and JAX. Commit to Neuron SDK early if targeting Trainium/Inferentia at scale.
3. **EKS for custom serving control** — multi-model serving, canary deployments, and KEDA-based autoscaling require Kubernetes-level control. SageMaker managed endpoints are the first choice for single-model REST serving; EKS is the fallback for complex serving topologies.
4. **EC2 P5/G6 for NVIDIA-specific needs** — custom CUDA kernels, Triton kernels, or frameworks not yet Neuron-compiled require NVIDIA hardware. Do not default to P5/G6 when Inferentia 2 can serve the same workload at lower cost.

## Consequences

### Positive
- HyperPod self-healing eliminates the primary reliability risk in large-scale training jobs
- Trainium 2 / Inferentia 2 provide 30–50% cost reduction over equivalent NVIDIA GPU serving for Neuron-compatible models
- AWS Batch provides managed job queues and spot instance integration without persistent cluster management cost

### Negative / Trade-offs
- Trainium / Inferentia requires Neuron SDK compilation — not all models or custom ops are Neuron-compatible; validate model compatibility early in the project
- SageMaker HyperPod cluster setup has a longer lead time than standard SageMaker training jobs — not suitable for ad-hoc small training runs
- EC2 P5 H100 instances have long reservation lead times and high on-demand pricing — use spot instances for training and reserved capacity for production inference

### Risks
- [RISK: MED] Neuron SDK version compatibility — Neuron SDK updates can break compiled model artifacts; pin Neuron SDK version and recompile on upgrades
- [RISK: MED] HyperPod cluster scaling events can cause brief training disruptions — test elastic scaling behaviour before production large-scale runs
- [RISK: LOW] EKS node group GPU driver management — automate NVIDIA/Neuron driver version via node group launch templates; driver mismatches cause silent inference errors

## Alternatives Considered

| Option | Why Rejected |
|--------|--------------|
| Raw EC2 GPU instances without SageMaker | High ops burden for health checks, scaling, and job scheduling; use SageMaker HyperPod or AWS Batch instead |
| AWS Fargate | No GPU support; compute-limited for ML inference; use for non-GPU ML microservices only |
| EC2 P5 as default (NVIDIA only) | Default to Inferentia 2 for inference and Trainium 2 for training first; P5 reserved for NVIDIA-specific workloads |
| On-premises GPU clusters | Inconsistent with cloud-first direction; no managed scaling or HyperPod resilience features |

## Implementation Notes

1. HyperPod: provision via SageMaker console or CDK; use `sagemaker.hyperpod` SDK for cluster management; enable automatic node recovery in cluster policy
2. Neuron SDK: compile models with `torch_neuronx.trace()` for Trainium / `torch.neuron.trace()` for Inferentia; store compiled artifacts in S3 with version tags
3. EKS model serving: use NVIDIA Triton Inference Server (GPU) or AWS Neuron serving container (Inferentia); configure KEDA `ScaledObject` on SQS queue depth or custom CloudWatch metric
4. AWS Batch: define compute environments with spot fleet on P5/G6 or Trainium; configure retry strategy (3 retries, exponential backoff) for spot interruption
5. Cost optimisation: use Spot instances for training (60–70% savings); Reserved instances for production inference with predictable load

## Review Checklist

- [ ] Aligns with architecture principles in CLAUDE.md
- [ ] No undocumented PII exposure
- [ ] Observability plan defined
- [ ] Fallback/degradation path exists
- [ ] Cost impact estimated
- [ ] Reviewed by at least one peer
