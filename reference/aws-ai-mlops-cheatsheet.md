# AWS-Native AI Tech Stack — AIEnablement & MLOps Cheat Sheet

> **Audience:** AI Architects, MLOps Engineers, AI Enablement Leads
> **Scope:** AWS 1st-party services + key AWS SDKs used in AIEnablement and MLOps code
> **Last updated:** 2026-07-11 — verified against AWS re:Invent 2025, May 2026 announcements, and AWS Summit New York 2026 (June 16–22, 2026)

---

## Architecture Overview

```mermaid
graph TB
    subgraph DATA["💾 Data Layer"]
        S3[Amazon S3]
        S3V[S3 Vectors]
        GLUE[AWS Glue]
        OSS[OpenSearch Service]
        RS[Amazon Redshift]
    end

    subgraph FOUND["🧠 Foundation & AI Services"]
        BED[Amazon Bedrock]
        NOVA[Amazon Nova 2]
        JST[SageMaker JumpStart]
        KENDRA[Amazon Kendra]
    end

    subgraph AGENTS["🤖 Agent Services"]
        AC[Bedrock AgentCore]
        BA[Bedrock Agents]
        KB[Bedrock Knowledge Bases]
        BF[Bedrock Flows]
        NAct[Nova Act]
    end

    subgraph ML["⚙️ ML Platform"]
        SM[Amazon SageMaker AI]
        HYP[SageMaker HyperPod]
        PIPE[SageMaker Pipelines]
        FS[SageMaker Feature Store]
        MR[SageMaker Model Registry]
        MM[SageMaker Model Monitor]
        CLR[SageMaker Clarify]
        MLF[SageMaker MLflow]
    end

    subgraph COMPUTE["🖥️ Compute"]
        EKS[Amazon EKS]
        BATCH[AWS Batch]
        TRN[Trainium 2]
        INF[Inferentia 2]
        GPU[EC2 P5/G6 - H100/L40S]
    end

    subgraph ORCH["🔄 Orchestration"]
        SF[AWS Step Functions]
        EB[Amazon EventBridge]
        LAM[AWS Lambda]
        MWAA[Amazon MWAA]
    end

    subgraph OBS["📊 Monitoring & Observability"]
        CW[Amazon CloudWatch]
        XR[AWS X-Ray]
        BE[Bedrock Evaluations]
    end

    subgraph GOV["🛡️ Governance & Safety"]
        GRD[Bedrock Guardrails]
        IAM[AWS IAM]
        LF[AWS Lake Formation]
        MAC[Amazon Macie]
        CFG[AWS Config]
    end

    subgraph DEVOPS["🔧 Infra & DevOps"]
        ECR[Amazon ECR]
        CP[AWS CodePipeline]
        CDK[AWS CDK]
    end

    DATA -->|"features / training data"| ML
    FOUND -->|"model access"| ML
    FOUND -->|"model access"| AGENTS
    KB -->|"RAG grounding"| AGENTS
    AGENTS -->|"orchestrates"| ML
    ML -->|"packaged models"| COMPUTE
    ORCH -->|"triggers"| ML
    ORCH -->|"triggers"| AGENTS
    COMPUTE -->|"telemetry"| OBS
    ML -->|"metrics / drift"| OBS
    GOV -. "governs" .-> AGENTS
    GOV -. "governs" .-> ML
    DEVOPS -. "CI/CD" .-> ML
    DEVOPS -. "deploys" .-> COMPUTE
```

---

## 1. Foundation & AI Services

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon Bedrock** | Managed access to foundation models — Amazon Nova, Claude, Llama, Mistral, Titan, Cohere, Stable Diffusion, OpenAI GPT, xAI Grok 4.3, + 18 open-weight models added Jun 2026 (Mistral Large 3, Gemma 3, NVIDIA Nemotron) — with enterprise security | LLM inference, embeddings, fine-tuning, RAG; Reserved/Priority/Flex service tiers; supports Converse, Invoke, OpenAI-compatible Responses and Chat Completions APIs | [docs](https://docs.aws.amazon.com/bedrock/) |
| **xAI Grok 4.3 on Bedrock** *(GA — Jun 2026)* | Grok 4.3 via a new Bedrock inference engine tuned for price/performance — tool calling, structured output, response streaming | Frontier reasoning + agentic workflows inside AWS trust boundary; more model choice for enterprise pipelines | [docs](https://aws.amazon.com/about-aws/whats-new/2026/06/grok-amazon-bedrock/) |
| **Amazon Nova 2** | Amazon's own model family — Lite, Pro (1M context, extended thinking), Sonic (speech-to-speech), Omni (multimodal I/O) | Cost-optimised inference with native AWS integration; Nova Forge for custom frontier models ($100K/yr) | [docs](https://docs.aws.amazon.com/nova/) |
| **Amazon Nova Act** *(GA)* | Browser automation agent — 90%+ task reliability, deploys to AgentCore with zero infra config | Automate web-based workflows in agentic pipelines; integrates natively with AgentCore Runtime | [docs](https://docs.aws.amazon.com/nova/) |
| **SageMaker JumpStart** | Model hub — pre-trained foundation models, fine-tuning templates, one-click deployment | Discover and deploy open models (Llama, Falcon, etc.); starting point for model evaluation and PoC | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) |
| **Amazon Kendra** | Managed enterprise search with ML-powered relevance ranking | Enterprise RAG — index internal documents, SharePoint, S3 with intelligent retrieval | [docs](https://docs.aws.amazon.com/kendra/) |
| **OpenAI Models on Amazon Bedrock** *(Limited Preview)* | GPT-5.5, GPT-5.4 via Bedrock — same IAM, PrivateLink, Guardrails, CloudTrail controls as native models | Access frontier OpenAI models without leaving AWS trust boundary; applies toward existing AWS cloud commitments | [docs](https://aws.amazon.com/bedrock/openai/) |
| **Amazon Bedrock Data Automation (BDA)** *(GA)* | Intelligent document processing — extract structured data from PDFs, images, financial docs; supports EN/PT/FR/IT/ES/DE | Automate data ingestion pipelines for RAG and feature engineering; replaces custom OCR/extraction stacks | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html) |

---

## 2. Agent Services

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon Bedrock AgentCore** *(GA)* | Production agent infrastructure — Cedar-based policy controls, episodic memory, continuous quality evaluations, bidirectional streaming; Payments capability (Preview) via Coinbase/Stripe wallets with session-level spending limits | Deploy and govern production agents; enforce what agents can/cannot do before any tool call; enable agents to autonomously pay for APIs and MCP services | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) |
| **Bedrock AgentCore Harness** *(GA — Jun 2026)* | Managed infrastructure + orchestration layer — go from agent idea to production-grade agent in minutes | Standardised runtime for hosting/orchestrating agents without wiring infra by hand | [docs](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available-go-from-idea-to-production-grade-agent-in-minutes/) |
| **Web Search on Bedrock AgentCore** *(GA — Jun 2026)* | Fully managed web-search tool — grounds agents in current, cited web knowledge with zero data egress from the customer's AWS boundary | Add live web grounding to agents without building/operating a search integration | [docs](https://aws.amazon.com/blogs/aws/announcing-web-search-on-amazon-bedrock-agentcore-ground-your-ai-agents-in-current-accurate-web-knowledge/) |
| **Amazon Bedrock Managed Knowledge Base** *(GA — Jun 2026)* | Fully managed enterprise RAG — native data connectors, Smart Parsing (automatic multi-format prep), Agentic Retriever for multi-step queries, integrated with AgentCore Gateway | Build RAG pipelines focused on outcomes, not infra; evolution of Bedrock Knowledge Bases | [docs](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-managed-knowledge-base-for-faster-more-accurate-enterprise-ai-applications/) |
| **Amazon Bedrock Agents** | Build conversational agents with tool use, multi-step reasoning, and memory | RAG + action execution; connect agents to APIs, Lambda functions, and knowledge bases | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) |
| **Amazon Bedrock Knowledge Bases** | Managed RAG — automatic chunking, embedding, vector storage, and retrieval | Ground agents in enterprise data without building custom RAG pipelines; supports S3, Confluence, SharePoint; supports 1-hour prompt cache TTL for long-running multi-turn agent workflows | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) |
| **Amazon Bedrock Flows** | Visual no-code builder for agent workflows — chain prompts, tools, and conditions as DAGs | Build and iterate on agent logic without code; deploy flows as managed endpoints | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html) |
| **Amazon Bedrock Responses API** *(GA)* | Server-side tool use within Bedrock — web search, code execution, database updates run inside AWS security boundary | Use in agentic pipelines where tool calls must stay server-side; integrates with Converse API | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) |
| **Amazon Bedrock Guardrails** *(GA)* | Content filtering — PII redaction, topic blocking, grounding checks, hallucination detection, code safety | Apply safety layers to all LLM I/O in a pipeline; Guardrails for Code extends to code comments and variables | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) |
| **Codex on Amazon Bedrock** *(Limited Preview)* | OpenAI coding agent inside AWS — authenticate with AWS credentials, run via Codex CLI, desktop app, or VS Code extension | AI-assisted coding within enterprise AWS boundary; usage applies toward cloud commitments | [docs](https://aws.amazon.com/about-aws/whats-new/2026/04/bedrock-openai-models-codex-managed-agents/) |
| **Bedrock Managed Agents powered by OpenAI** *(Limited Preview)* | Deploy production-ready OpenAI-powered agents on Bedrock infrastructure with AWS security controls | Fast path to OpenAI agent capabilities with IAM, PrivateLink, Guardrails governance | [docs](https://aws.amazon.com/bedrock/openai/) |
| **Amazon WorkSpaces for AI Agents** *(Preview)* | Isolated secure compute environments (desktop/browser) for AI agents to operate in | Sandbox for agents running UI automation, web browsing, and desktop workflows | [docs](https://aws.amazon.com/about-aws/whats-new/2026/05/workspaces-ai-agents/) |
| **AWS Security Agent** *(GA)* | Autonomous on-demand penetration testing frontier agent — compresses pen testing from weeks to hours; runs persistently without human oversight | Integrate security testing into MLOps pipelines; detect vulnerabilities in AI workload infrastructure | [docs](https://aws.amazon.com/blogs/machine-learning/aws-launches-frontier-agents-for-security-testing-and-cloud-operations/) |
| **AWS DevOps Agent** *(GA; release mgmt Preview — Jun 2026)* | Autonomous DevOps operations frontier agent — 3–5x faster incident resolution, runs continuously hours to days; release-management capability (Preview) assesses code changes before production | AI-driven SRE and incident response; reduce ops burden on AI platform teams | [docs](https://aws.amazon.com/blogs/machine-learning/aws-launches-frontier-agents-for-security-testing-and-cloud-operations/) |

---

## 3. ML Platform

> ⚠️ **SageMaker AI** was rebranded from "Amazon SageMaker" at re:Invent 2024 — now the unified brand for all SageMaker services.

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon SageMaker AI** | Core MLOps platform — Unified Studio (integrated workspace: EMR, Glue, Athena, Redshift, Bedrock, SageMaker AI in one UI), experiments, training, model registry, managed endpoints, batch transform; real-time endpoints now expose an OpenAI-compatible API (invoke via OpenAI SDK / LangChain / Strands by changing only the endpoint URL — Jun 2026) [M]; MLflow integration streams benchmark + inference-optimization results in real time [M] | End-to-end ML lifecycle from data prep to production serving; PrivateLink support for VPC isolation | [docs](https://docs.aws.amazon.com/sagemaker/) |
| **SageMaker HyperPod** *(GA — enhanced)* | Managed distributed training cluster — checkpointless training (80%+ downtime reduction), elastic auto-scaling | Large-scale foundation model training and fine-tuning; self-healing clusters reduce ops burden | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html) |
| **SageMaker Serverless Customization** *(GA — agent-guided workflow Jun 2026)* | UI-driven fine-tuning — SFT, DPO, RLVR, RLAIF — without managing compute; new agent-guided natural-language workflow generates synthetic data + handles eval, cutting cycles months→days | Fine-tune Nova, Llama, DeepSeek in a few clicks; no capacity planning or instance management | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-fine-tune.html) |
| **SageMaker Pipelines** | Reusable MLOps workflow DAGs — data prep → train → evaluate → register → deploy | Automated retraining pipelines with CI/CD integration; YAML-based pipeline definitions | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html) |
| **SageMaker Feature Store** | Centralised online + offline feature storage with point-in-time correctness | Feature sharing across teams; consistent feature serving for training and inference | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html) |
| **SageMaker Model Registry** | Versioned model store with approval workflows and metadata | Govern model promotion from dev → staging → prod; track lineage per model version | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html) |
| **SageMaker Model Monitor** | Production model health — data drift, model drift, bias drift | Detect degradation post-deployment; auto-trigger retraining on threshold breach | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) |
| **SageMaker Clarify** | Bias detection, explainability, and feature attribution — pre/post-deployment | Responsible AI auditing; SHAP-based explanations for model decisions | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-explainability.html) |
| **SageMaker MLflow** *(Serverless GA)* | Managed MLflow 3.4 with AI tracing — 2-min instance creation, no infra management | Experiment tracking, run comparison, model versioning with zero ops overhead | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/mlflow.html) |
| **Reinforcement Fine-Tuning** *(Bedrock — GA)* | RLVR (rule-based) and RLAIF (AI-judge) fine-tuning — avg 66% accuracy gain over base models | Specialise foundation models on domain-specific tasks with automated reward evaluation | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-rlhf.html) |

---

## 4. Data Layer

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon S3** | Object storage — unlimited scale, lifecycle policies, event triggers | Training datasets, model artifacts, checkpoint storage, feature snapshots | [docs](https://docs.aws.amazon.com/s3/) |
| **Amazon S3 Vectors** *(GA)* | Native vector storage in S3 — 2B vectors per index, ~100ms query latency, 14 regions | Cost-efficient vector store for RAG — no separate vector DB needed for many use cases | [docs](https://docs.aws.amazon.com/s3/latest/userguide/vectors.html) |
| **Amazon S3 annotations** *(GA — Jun 2026)* | Attach up to 1GB of rich, mutable, queryable context directly to S3 objects — purpose-built for AI agents and autonomous workflows | Discover/understand/act on data at scale without a separate metadata system | [docs](https://aws.amazon.com/blogs/aws/amazon-s3-annotations-attach-rich-queryable-context-directly-to-your-objects/) |
| **Amazon OpenSearch Service** | Managed search + vector search with k-NN and hybrid retrieval | RAG pipelines — chunk, embed, index, and retrieve at low latency; replaces Elasticsearch | [docs](https://docs.aws.amazon.com/opensearch-service/) |
| **AWS Glue** | Serverless ETL — data cataloguing, transformation, quality checks | Build training data pipelines; data cataloguing for feature discovery and governance | [docs](https://docs.aws.amazon.com/glue/) |
| **Amazon Redshift** | Cloud data warehouse with ML-native capabilities (Redshift ML via SageMaker) | Large-scale feature engineering; in-warehouse model training via SQL | [docs](https://docs.aws.amazon.com/redshift/) |
| **Amazon DynamoDB** | Serverless NoSQL — single-digit ms latency at any scale | Online feature serving, agent session state, low-latency metadata stores | [docs](https://docs.aws.amazon.com/dynamodb/) |

---

## 5. Compute

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon EKS** | Managed Kubernetes — production container orchestration | Scalable model serving, multi-model inference clusters, MLOps tooling deployments | [docs](https://docs.aws.amazon.com/eks/) |
| **AWS Trainium 2** | Amazon's custom ML training chip — optimised for large model training | Distributed training at lower cost than GPU alternatives; Neuron SDK for framework support | [docs](https://aws.amazon.com/machine-learning/trainium/) |
| **AWS Inferentia 2** | Amazon's custom inference chip — high throughput, low cost per token | Production inference for latency-sensitive LLM serving at scale | [docs](https://aws.amazon.com/machine-learning/inferentia/) |
| **EC2 P5 / G6 instances** | NVIDIA H100 (P5) and L40S (G6) GPU instances | Custom training and high-performance inference workloads requiring full GPU control | [docs](https://aws.amazon.com/ec2/instance-types/p5/) |
| **EC2 G7 instances** *(Jun 2026)* | NVIDIA RTX PRO 4500 Blackwell Server Edition GPUs + 6th-gen Intel Xeon — AWS is first major cloud to offer these; up to 4.6x AI inference and 2.1x graphics vs G6 | Cost-effective GPU inference and graphics workloads at the mid-tier | [docs](https://aws.amazon.com/blogs/aws/announcing-amazon-ec2-g7-instances-accelerated-by-nvidia-rtx-pro-4500-blackwell-server-edition-gpus/) |
| **AWS Batch** | Managed batch compute — job queues, auto-scaling, spot integration | Large-scale batch inference, distributed training jobs, hyperparameter sweeps | [docs](https://docs.aws.amazon.com/batch/) |

---

## 6. Orchestration

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **AWS Step Functions** | Serverless workflow orchestration — visual state machines, error handling, parallel execution | MLOps pipelines outside SageMaker; multi-service AI workflows across Bedrock, Lambda, and data services | [docs](https://docs.aws.amazon.com/step-functions/) |
| **Amazon EventBridge** | Serverless event bus — route events between AWS services and SaaS | Trigger retraining on data arrival, alert on model drift events, chain AI pipeline stages | [docs](https://docs.aws.amazon.com/eventbridge/) |
| **AWS Lambda** | Serverless compute — event-driven, sub-second invocation | Lightweight inference endpoints, agent tool handlers, preprocessing transforms | [docs](https://docs.aws.amazon.com/lambda/) |
| **Amazon MWAA** | Managed Apache Airflow — complex DAG orchestration | Complex ML pipelines with external dependencies; teams already invested in Airflow | [docs](https://docs.aws.amazon.com/mwaa/) |

---

## 7. Monitoring & Observability

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon CloudWatch** | Platform-wide metrics, logs, alarms, dashboards | Endpoint SLA tracking, training job health, token usage metrics, cost alerts | [docs](https://docs.aws.amazon.com/cloudwatch/) |
| **AWS X-Ray** | Distributed tracing — request flow across services, latency analysis | Trace LLM app requests end-to-end across Lambda, Bedrock, and SageMaker endpoints | [docs](https://docs.aws.amazon.com/xray/) |
| **Amazon Bedrock Model Evaluation** | Automated and human evaluation of LLM outputs — quality, toxicity, accuracy | Run evals before deployment; continuous quality scoring via AgentCore evaluations | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-evaluation.html) |
| **SageMaker Model Monitor** | Production model health — data drift, prediction drift, bias drift | Post-deployment monitoring with automated alerts and retraining triggers | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html) |

---

## 8. Governance & Safety

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Bedrock AgentCore Policy Controls** *(GA)* | Cedar-based policy enforcement with natural language authoring — controls what agents can do before any tool call | Fine-grained agent governance; define allowlists of permitted actions per agent role | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) |
| **AWS Lake Formation** | Data lake governance — fine-grained access control, data cataloguing, column/row-level security | Govern access to training data and feature stores; enforce data policies across ML teams | [docs](https://docs.aws.amazon.com/lake-formation/) |
| **Amazon Macie** | ML-powered PII detection and data security for S3 | Scan training datasets for sensitive data; flag PII before it enters model training | [docs](https://docs.aws.amazon.com/macie/) |
| **AWS IAM** | Identity and access management — roles, policies, service principals | Least-privilege access for ML workloads; role-based access to models, endpoints, and data | [docs](https://docs.aws.amazon.com/iam/) |
| **AWS Config** | Continuous compliance monitoring and resource configuration history | Enforce guardrails on ML infra (approved instance types, encryption, tagging) | [docs](https://docs.aws.amazon.com/config/) |
| **Amazon SageMaker Clarify** | Bias detection, fairness analysis, and model explainability | Responsible AI auditing pre/post-deployment; SHAP explanations for model decisions | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-model-explainability.html) |

---

## 9. Infra & DevOps

| Service | Purpose | Key MLOps / AIEnablement Use | Docs |
|---|---|---|---|
| **Amazon ECR** | Private Docker registry — container image storage and lifecycle management | Store training environment images, model serving containers, SageMaker custom containers | [docs](https://docs.aws.amazon.com/ecr/) |
| **AWS CodePipeline / CodeBuild** | Managed CI/CD — automated build, test, and deploy pipelines | MLOps pipelines — trigger SageMaker pipeline runs on code or data changes | [docs](https://docs.aws.amazon.com/codepipeline/) |
| **AWS CDK** | Infrastructure as code in Python/TypeScript — L2/L3 constructs for AWS services | Define and version ML infrastructure (endpoints, pipelines, IAM roles) as code | [docs](https://docs.aws.amazon.com/cdk/) |
| **AWS CloudFormation** | Declarative infrastructure as code — YAML/JSON templates | Deploy reproducible ML environments; stack-based infra lifecycle management | [docs](https://docs.aws.amazon.com/cloudformation/) |
| **Agent Toolkit for AWS** *(GA)* | Production-ready suite of tools + guidance for AI coding agents building on AWS — fewer errors, lower token cost, enterprise security; successor to AWS Labs MCP servers/plugins/skills | Standard integration layer for AI coding agents building on AWS; replaces ad-hoc MCP server setups | [docs](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) |
| **AWS MCP Server** *(GA)* | Managed remote MCP server — gives AI agents and coding assistants authenticated access to all AWS services via a small fixed tool set; part of Agent Toolkit for AWS | Expose all AWS service capabilities to any MCP-compatible AI agent or assistant | [docs](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-mcp-server/) |

---

## 10. SDKs & Developer Tools

### Model Access & Agents

| SDK | Languages | Purpose | Key Use | Status | Docs |
|---|---|---|---|---|---|
| **boto3** | Python | Primary AWS SDK — low-level client for all AWS services | Call Bedrock, SageMaker, S3, and all AWS AI services | **GA** — Python 3.9 EOL April 2026; requires Python 3.10+ | [docs](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) |
| **amazon-bedrock-runtime** | Python, Java, .NET, JS/TS | High-level Bedrock client — InvokeModel, Converse API, streaming | LLM inference, streaming responses, multi-turn conversations | **GA** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html) |
| **amazon-bedrock-agent-runtime** | Python, Java, .NET, JS/TS | Invoke Bedrock Agents and Knowledge Bases programmatically | Run agents, retrieve from knowledge bases, manage agent sessions | **GA** | [docs](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html) |

### ML Platform

| SDK | Languages | Purpose | Key Use | Status | Docs |
|---|---|---|---|---|---|
| **sagemaker** (Python SDK) | Python | High-level SageMaker SDK — training, tuning, deployment, pipelines | Author training jobs, deploy endpoints, build and run SageMaker Pipelines | **GA** | [docs](https://sagemaker.readthedocs.io/) |
| **MLflow** *(via SageMaker serverless)* | Python | Experiment tracking, model registry, serving | Track runs, compare experiments, register models — serverless managed by AWS | **GA** | [docs](https://docs.aws.amazon.com/sagemaker/latest/dg/mlflow.html) |

### Infra & Auth

| SDK | Languages | Purpose | Key Use | Status | Docs |
|---|---|---|---|---|---|
| **AWS CDK** | Python, TypeScript | Infrastructure as code with high-level constructs | Define ML infra (endpoints, pipelines, IAM, VPC) as versioned code | **GA** | [docs](https://docs.aws.amazon.com/cdk/api/v2/) |
| **AWS Neuron SDK** | Python | Compile and optimise models for Trainium / Inferentia chips | Deploy cost-efficient inference on Inferentia 2; distributed training on Trainium 2 | **GA** | [docs](https://awsdocs-neuron.readthedocs-hosted.com/) |

---

## Quick Reference: Concern → Service Mapping

| Architectural Concern | Primary Services |
|---|---|
| LLM access & model selection | Amazon Bedrock, SageMaker JumpStart |
| Amazon's own models | Amazon Nova 2 (Lite/Pro/Sonic/Omni) |
| OpenAI model access on AWS | OpenAI Models on Amazon Bedrock (Limited Preview) |
| xAI model access on AWS | xAI Grok 4.3 on Bedrock (GA) |
| Agent runtime / orchestration harness | Bedrock AgentCore Harness (GA) |
| Agent web grounding | Web Search on Bedrock AgentCore (GA) |
| Object-level context for agents | Amazon S3 annotations (GA) |
| Mid-tier GPU inference | EC2 G7 (Blackwell RTX PRO 4500) |
| Agent building & orchestration | Bedrock AgentCore, Bedrock Agents, Bedrock Flows |
| Agent memory & state | Bedrock AgentCore (episodic memory) |
| Agent payments / API purchasing | Bedrock AgentCore Payments (Preview) |
| Agent compute sandboxing | Amazon WorkSpaces for AI Agents (Preview) |
| Enterprise data grounding (RAG) | Bedrock Knowledge Bases, Amazon Kendra, OpenSearch |
| Vector store | Amazon S3 Vectors, Amazon OpenSearch |
| Training & experimentation | SageMaker AI, SageMaker HyperPod, EC2 P5/G6 |
| Custom silicon training | AWS Trainium 2 + Neuron SDK |
| Custom silicon inference | AWS Inferentia 2 + Neuron SDK |
| Fine-tuning (no-infra) | SageMaker Serverless Customization, Bedrock RFT |
| Feature management | SageMaker Feature Store |
| MLOps pipelines | SageMaker Pipelines, AWS Step Functions |
| Experiment tracking | SageMaker MLflow (serverless) |
| Model registry & promotion | SageMaker Model Registry |
| Model serving (online) | SageMaker Managed Endpoints, EKS |
| Model serving (batch) | SageMaker Batch Transform, AWS Batch |
| Data pipelines | AWS Glue, Amazon EventBridge, MWAA |
| Monitoring & drift detection | SageMaker Model Monitor, CloudWatch |
| LLM quality & safety evals | Bedrock Model Evaluation, AgentCore Evaluations |
| Content safety & guardrails | Amazon Bedrock Guardrails |
| Bias & explainability | SageMaker Clarify |
| Agent policy enforcement | Bedrock AgentCore Policy Controls (Cedar) |
| Data governance & PII | AWS Lake Formation, Amazon Macie |
| Identity & access | AWS IAM |
| Document intelligence / extraction | Amazon Bedrock Data Automation (BDA) |
| AI-assisted coding in AWS | Codex on Amazon Bedrock (Limited Preview) |
| Automated security testing | AWS Security Agent |
| AI-driven incident response | AWS DevOps Agent |
| MCP server (AWS services) | AWS MCP Server (Agent Toolkit for AWS) |
| CI/CD for ML | AWS CodePipeline, CodeBuild, GitHub Actions |
| Infra as code | AWS CDK, CloudFormation |
| **SDK: Model inference** | `boto3` + `amazon-bedrock-runtime` |
| **SDK: Agent invocation** | `amazon-bedrock-agent-runtime` |
| **SDK: ML pipelines & training** | `sagemaker` Python SDK |
| **SDK: Custom silicon** | AWS Neuron SDK |
| **SDK: Infra as code** | AWS CDK |
