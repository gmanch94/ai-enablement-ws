# Cross-Cloud AI Tech Stack Comparison — Azure vs AWS vs GCP

> **Audience:** AI Architects making platform decisions or working across clouds
> **Last updated:** 2026-04-17
> **Detail:** See individual cheatsheets for full service descriptions and docs links
> - Azure: `context/azure-ai-mlops-cheatsheet.md`
> - AWS: `context/aws-ai-mlops-cheatsheet.md`
> - GCP: `context/gcp-ai-mlops-cheatsheet.md`

---

## Service-to-Service Mapping

| Concern | Azure (Microsoft Foundry) | AWS | GCP |
|---|---|---|---|
| **Unified AI Platform** | Microsoft Foundry | — | Vertex AI |
| **LLM Model Access** | Azure OpenAI Service | Amazon Bedrock | Gemini API / Vertex AI Model Garden |
| **Native Model Family** | Azure OpenAI (GPT-5.x, o1) | Amazon Nova 2 (Lite/Pro/Sonic/Omni) | Gemini 2.5 Pro/Flash |
| **Model Catalog** | Foundry Model Catalog | SageMaker JumpStart | Vertex AI Model Garden |
| **Model Router** | Model Router (GA) | Bedrock Cross-Region Inference | Vertex AI Model Optimizer (GA) |
| **Enterprise Search / RAG** | Azure AI Search | Amazon Kendra + Bedrock Knowledge Bases | Vertex AI Search + RAG Engine |
| **Vector Store (managed)** | Azure AI Search, Cosmos DB | Amazon S3 Vectors, OpenSearch | AlloyDB AI, Cloud Spanner, Vertex AI |

---

## Agent Services

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Agent Runtime (managed)** | Foundry Agent Service (GA) | Bedrock AgentCore (GA) | Agent Engine (GA) |
| **Agent Builder (no-code)** | Microsoft Foundry portal | Bedrock Flows | Vertex AI Agent Builder |
| **Agent Framework (SDK)** | Microsoft Agent Framework (GA) | Bedrock Agents SDK | Agent Development Kit / ADK (GA) |
| **Agent-to-Agent Protocol** | A2A Tool (Preview) | — | Agent2Agent Protocol (GA) |
| **Agent Memory** | Memory in Foundry Agent Service (Preview) | Bedrock AgentCore Episodic Memory (GA) | — (via AlloyDB / Spanner) |
| **Agent Policy / Governance** | Foundry Control Plane + Entra Agent ID | AgentCore Cedar-based policies (GA) | Model Armor + Cloud IAM |
| **MCP Server** | Foundry MCP Server (Preview) | — | MCP Toolbox for Databases (GA) |
| **Enterprise Data Grounding** | Foundry IQ | Bedrock Knowledge Bases | Vertex AI RAG Engine + Agent Builder |
| **Browser Automation** | Computer Use (Preview) | Nova Act (GA) | — |

---

## ML Platform

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Core MLOps Platform** | Azure Machine Learning | Amazon SageMaker AI | Vertex AI |
| **ML Pipelines** | Azure ML Pipelines | SageMaker Pipelines | Vertex AI Pipelines (Kubeflow) |
| **Feature Store** | Azure ML Managed Feature Store | SageMaker Feature Store | Vertex AI Feature Store |
| **Model Registry** | Azure ML Model Registry | SageMaker Model Registry | Vertex AI Model Registry |
| **Experiment Tracking** | Azure ML Experiments | SageMaker Experiments + MLflow (serverless) | Vertex AI Experiments |
| **Distributed Training** | Azure ML + GPU VMs | SageMaker HyperPod (checkpointless GA) | Vertex AI Training + Cluster Director |
| **Fine-tuning (managed)** | Foundry fine-tuning + Azure ML | SageMaker Serverless Customization (GA) | Vertex AI tuning (Gemini/Imagen/Veo) |
| **Reinforcement Fine-Tuning** | Azure OpenAI RFT (GPT-5) | Bedrock RFT — RLVR + RLAIF (GA) | — |
| **LLM Orchestration** | Prompt Flow ⚠️ (sunset Jan 2027) | Bedrock Flows | Genkit |
| **Notebooks** | Azure ML Compute Instances | SageMaker Studio Notebooks | Vertex AI Workbench |

---

## Data Layer

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Object Storage** | ADLS Gen2 | Amazon S3 | Google Cloud Storage |
| **Vector Storage** | Azure AI Search, Cosmos DB | Amazon S3 Vectors (GA), OpenSearch | AlloyDB AI, Cloud Spanner, Vertex AI |
| **Unified Analytics / Lakehouse** | Microsoft Fabric | AWS Glue + Redshift | BigQuery + Dataflow |
| **In-database ML** | Microsoft Fabric | Redshift ML | BigQuery ML |
| **ETL / Data Pipelines** | Azure Data Factory, Fabric | AWS Glue, MWAA | Dataflow, BigQuery Pipelines |
| **Data Catalog + Governance** | Microsoft Purview | AWS Glue Data Catalog + Lake Formation | Dataplex + BigQuery Universal Catalog |

---

## Compute

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Managed Kubernetes** | AKS | Amazon EKS | GKE |
| **Serverless Containers** | Azure Container Apps | AWS Lambda + Fargate | Cloud Run (+ GPUs GA) |
| **GPU VMs** | NC/ND-series (A100, H100) | EC2 P5 (H100), G6 (L40S) | A4 (B200), A4X (GB200 Blackwell) |
| **Custom AI Chips (Training)** | — | AWS Trainium 2 | Cloud TPU (Ironwood 7th gen) |
| **Custom AI Chips (Inference)** | — | AWS Inferentia 2 | Cloud TPU (Ironwood) |
| **Large Cluster Management** | — | SageMaker HyperPod | Cluster Director (GA) |
| **Optimised Ray** | — | — | RayTurbo on GKE (GA) |
| **On-device / Edge AI** | Foundry Local (Preview) | — | Google Distributed Cloud |

---

## Orchestration

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **ML Workflow DAGs** | Azure ML Pipelines | SageMaker Pipelines | Vertex AI Pipelines |
| **Managed Airflow** | — | Amazon MWAA | Cloud Composer |
| **Event-driven Triggers** | Azure Functions, Logic Apps | AWS EventBridge + Lambda | Eventarc + Cloud Functions |
| **API / Model Gateway** | AI Gateway (APIM) | Amazon API Gateway | Apigee |
| **General Workflow Orchestration** | Azure Logic Apps | AWS Step Functions | Cloud Workflows |

---

## Monitoring & Observability

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Platform Monitoring** | Azure Monitor | Amazon CloudWatch | Cloud Monitoring |
| **Distributed Tracing** | Application Insights | AWS X-Ray | Cloud Trace |
| **Log Analytics** | Log Analytics Workspace | CloudWatch Logs Insights | Cloud Logging + Log Analytics |
| **Model Drift Monitoring** | Azure ML Model Monitoring | SageMaker Model Monitor | Vertex AI Model Monitoring |
| **LLM / Agent Observability** | Foundry Observability Suite (GA) | Bedrock Model Evaluation + AgentCore Evals | Vertex AI Dashboards (GA) |
| **Prompt Optimization** | Prompt Optimizer (Preview) | — | — |
| **Agent Monitoring** | Agent Monitoring Dashboard (GA) | — | Vertex AI Dashboards |

---

## Governance & Safety

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Content Filtering / Safety** | Azure AI Content Safety | Amazon Bedrock Guardrails | Model Armor |
| **Agentic Guardrails** | Task Adherence (Preview) | AgentCore Cedar Policies (GA) | Model Armor + Tool Governance |
| **PII Detection** | Microsoft Purview | Amazon Macie | Cloud DLP |
| **Data Lineage / Cataloguing** | Microsoft Purview | AWS Glue + Lake Formation | Dataplex |
| **Responsible AI / Bias** | Responsible AI Dashboard (Azure ML) | SageMaker Clarify | Vertex AI Evaluation |
| **Identity & Access** | Microsoft Entra ID + Entra Agent ID | AWS IAM | Cloud IAM + Workload Identity |
| **Compliance / Policy** | Azure Policy | AWS Config | VPC Service Controls + Security Command Center |
| **Cost Attribution** | Azure Cost Management (tag-based GA) | AWS Cost Explorer + Cost Allocation Tags | BigQuery Cost Explorer (Preview) |

---

## SDK Landscape

| Concern | Azure | AWS | GCP |
|---|---|---|---|
| **Primary AI SDK** | `azure-ai-projects` v2 | `boto3` + `amazon-bedrock-runtime` | `google-cloud-aiplatform` |
| **LLM Inference** | `azure-ai-inference` | `amazon-bedrock-runtime` | `google-generativeai` |
| **Agent Framework SDK** | Microsoft Agent Framework (SK + AutoGen) | `amazon-bedrock-agent-runtime` | `google-adk` |
| **ML Pipelines SDK** | `azure-ai-ml` (SDK v2) | `sagemaker` Python SDK | `kfp` + `google-cloud-aiplatform` |
| **LLM App Framework** | Prompt Flow ⚠️ → Framework Workflows | — | Genkit |
| **Evaluation SDK** | `azure-ai-evaluation` | Bedrock Model Evaluation API | Vertex AI Evaluation SDK |
| **Observability / Tracing** | `azure-monitor-opentelemetry` | AWS X-Ray SDK | `google-cloud-trace` + OpenTelemetry |
| **Auth SDK** | `azure-identity` (DefaultAzureCredential) | `boto3` (IAM roles / instance profile) | `google-auth` (Application Default Credentials) |
| **Infra as Code** | Azure CDK / Bicep / Terraform | AWS CDK / CloudFormation / Terraform | Terraform (Google provider) / Cloud Deploy |
| **Custom Silicon SDK** | — | AWS Neuron SDK | — (TPU via `google-cloud-aiplatform`) |

---

## Key Differentiators (as of April 2026)

| Dimension | Azure Strength | AWS Strength | GCP Strength |
|---|---|---|---|
| **Agent Governance** | Foundry Control Plane + Entra Agent ID — most mature enterprise governance | Cedar-based AgentCore policies — fine-grained policy-as-code | A2A Protocol — best open interoperability standard |
| **Proprietary Models** | GPT-5.x, o1 series (OpenAI partnership) | Nova 2 family (Lite/Pro/Sonic/Omni) | Gemini 2.5 Pro/Flash — top benchmark scores |
| **Custom Silicon** | None | Trainium 2 (training) + Inferentia 2 (inference) | Ironwood TPU 7th gen — inference at scale |
| **Data + AI Integration** | Microsoft Fabric + Purview | AWS Glue + Lake Formation | BigQuery — tightest data-to-AI integration |
| **Agentic Guardrails** | Task Adherence (Preview) — scope guardrails | AgentCore Cedar policies (GA) — most mature | Model Armor — unified safety layer |
| **Open Standards** | Foundry MCP Server | — | A2A Protocol + MCP Toolbox — most open |
| **On-device / Edge AI** | Foundry Local (Preview) | AWS AI Factories (on-prem infra) | Google Distributed Cloud (Gemini on-prem) |
| **Fine-tuning breadth** | RFT on GPT-5, Foundry model catalog | Serverless Customization — SFT/DPO/RLVR/RLAIF | Gemini, Imagen, Veo — multimodal tuning |
