# Cloud AI — Business Professional's Cheat Sheet
*Concepts from the AWS AI Practitioner course, with AWS / Azure / GCP service mappings.*

> **Audience:** Business stakeholders, product managers, executives, and non-engineering leads who sponsor, evaluate, or steer AI initiatives.
> **Source:** AWS AI Practitioner course (concepts) + practical additions (multi-cloud service mapping, decision matrices, governance questions).
> **How to use:** Scan top-to-bottom in ~10 minutes, or jump to a section when a specific topic comes up in a meeting.
> **Last updated:** 2026-04-18

---

## Table of Contents
1. [AI vs ML vs Deep Learning vs GenAI](#1-ai-vs-ml-vs-deep-learning-vs-genai)
2. [The ML Lifecycle (7 Phases)](#2-the-ml-lifecycle-7-phases)
3. [Data Types Cheat Sheet](#3-data-types-cheat-sheet)
4. [Learning Types](#4-learning-types)
5. [Foundation Models 101](#5-foundation-models-101)
6. [Key GenAI Concepts in Plain English](#6-key-genai-concepts-in-plain-english)
7. [Customizing Foundation Models — Decision Matrix](#7-customizing-foundation-models--decision-matrix)
8. [Prompt Engineering Quick Guide](#8-prompt-engineering-quick-guide)
9. [Prompt Risks & Misuse](#9-prompt-risks--misuse)
10. [Model Evaluation in Business Terms](#10-model-evaluation-in-business-terms)
11. [When to Use AI (and When Not To)](#11-when-to-use-ai-and-when-not-to)
12. [GenAI Benefits & Challenges](#12-genai-benefits--challenges)
13. [Responsible AI & Governance](#13-responsible-ai--governance)
14. [AWS Service Quick-Map](#14-aws-service-quick-map)
15. [Azure Service Quick-Map](#15-azure-service-quick-map)
16. [GCP Service Quick-Map](#16-gcp-service-quick-map)
17. [Cross-Cloud Equivalents at a Glance](#17-cross-cloud-equivalents-at-a-glance)
18. [Glossary](#18-glossary)
19. [Questions to Ask Before Approving an AI Project](#19-questions-to-ask-before-approving-an-ai-project)

---

## 1. AI vs ML vs Deep Learning vs GenAI

Each layer is a subset of the one above it.

| Term | Plain-English Definition | Business Example |
|---|---|---|
| **Artificial Intelligence (AI)** | Any technique that lets a machine perform tasks normally requiring human intelligence. | A virtual assistant scheduling meetings. |
| **Machine Learning (ML)** | A subset of AI where the system *learns patterns from data* instead of following hand-coded rules. | Predicting which customers will churn next quarter. |
| **Deep Learning (DL)** | A subset of ML using *neural networks* with many layers — inspired by the brain. Excels at images, audio, language. | Detecting defects on a production line from camera images. |
| **Generative AI (GenAI)** | A subset of DL that *creates new content* (text, images, audio, code) rather than just predicting or classifying. | Drafting marketing copy or summarizing 200-page reports. |

> **Rule of thumb:** Use traditional ML for prediction/classification on structured data. Use GenAI for creating, summarizing, or conversing.

---

## 2. The ML Lifecycle (7 Phases)

| # | Phase | What Happens | Business Question Answered | Typical Owner |
|---|---|---|---|---|
| 1 | **Business goal identification** | Define why we're doing this. | "What outcome are we paying for?" | Product / Business |
| 2 | **ML problem framing** | Translate the goal into a prediction or generation task. | "Is this even an ML problem?" | Data Scientist + PM |
| 3 | **Data processing** | Collect, clean, and engineer features. | "Do we have the right data, and is it usable?" | Data Engineering |
| 4 | **Model development** | Train, tune, and evaluate models. | "Does it actually work well enough?" | Data Science / ML |
| 5 | **Model deployment** | Put the model into production (real-time, batch, etc.). | "Can users actually use it?" | MLOps / Engineering |
| 6 | **Model monitoring** | Watch for accuracy drift, latency, cost. | "Is it still working in the wild?" | MLOps + SRE |
| 7 | **Model retraining** | Refresh the model on new data. | "How do we keep it from getting stale?" | MLOps + Data Science |

> **Cost reality:** Phases 3 (data) and 5–7 (deploy + run) usually consume 70–80% of total project effort. Don't underbudget the boring parts.

---

## 3. Data Types Cheat Sheet

| Dimension | Type | What It Looks Like | Best For |
|---|---|---|---|
| **Has labels?** | **Labeled** | Each row has a "correct answer" (e.g., emails tagged spam/not-spam). | Supervised learning — most predictive use cases. |
|  | **Unlabeled** | Just raw inputs, no answers. | Unsupervised learning, GenAI pretraining. |
| **Format** | **Structured** | Rows + columns: spreadsheets, databases, time-series. | Classical ML — fraud, churn, forecasting. |
|  | **Unstructured** | Text, images, audio, video. | Deep learning, GenAI, search. |

> **The dirty secret:** Most enterprise data is *unstructured and unlabeled*. Labeling is expensive — budget for it explicitly.

---

## 4. Learning Types

| Type | What It Does | Use When | Business Example |
|---|---|---|---|
| **Supervised — Classification** | Sorts inputs into categories. | You have labeled examples and discrete outcomes. | Approve / decline a loan application. |
| **Supervised — Regression** | Predicts a number. | You have labeled examples and continuous outcomes. | Forecast next month's revenue. |
| **Unsupervised — Clustering** | Groups similar items together. | You don't know the groupings yet. | Customer segmentation. |
| **Unsupervised — Dimensionality Reduction** | Compresses many features into fewer meaningful ones. | Data is too wide / noisy to model directly. | Pre-processing for visualization or speed. |
| **Reinforcement Learning** | Agent learns by trial and error against a reward. | The right answer is unknown but the goal is measurable. | Robotics, game-playing, dynamic pricing, ad bidding. |

---

## 5. Foundation Models 101

Foundation Models (FMs) are large, pre-trained models you adapt — instead of training from scratch.

| Model Type | What It Generates | Business Use Case | AWS Examples (via Bedrock) |
|---|---|---|---|
| **Large Language Model (LLM)** | Human-like text. | Chatbots, summarization, drafting, Q&A over docs. | Anthropic Claude, Amazon Nova, Meta Llama, Mistral |
| **Diffusion Model** | Images (and increasingly video) from text prompts. | Marketing creatives, product mockups, concept art. | Stability AI, Amazon Nova Canvas |
| **Multimodal Model** | Handles multiple inputs/outputs (text + image + audio). | Visual Q&A, video captioning, doc-with-charts understanding. | Claude (vision), Amazon Nova multimodal |
| **GAN (Generative Adversarial Network)** | Synthetic data via two competing networks. | Synthetic training data, deepfake detection, image enhancement. | Custom training on SageMaker |
| **VAE (Variational Autoencoder)** | Compressed representations + new samples. | Anomaly detection, recommendation systems, data generation. | Custom training on SageMaker |

---

## 6. Key GenAI Concepts in Plain English

| Concept | Plain English |
|---|---|
| **Token** | A chunk of text the model reads — roughly ¾ of a word. *You pay per token*. |
| **Embedding** | A list of numbers that represents the *meaning* of a word, sentence, or image. Lets the computer measure "how similar" two things are. |
| **Vector / Vector Database** | The storage for embeddings. Lets you search by meaning, not just keywords. Backbone of RAG. |
| **Prompt** | The instruction you give the model. Quality of the prompt drives quality of the output. |
| **Context Window** | How much text the model can "see" at once (the prompt + recent history). Larger = more expensive but better memory. |
| **Inference** | Running a trained model to get a prediction or output. |
| **Real-time inference** | Live response in milliseconds (chatbot, fraud check). Higher cost, always-on. |
| **Batch inference** | Process many inputs at once on a schedule (nightly scoring). Cheaper, not interactive. |
| **Hallucination** | When the model confidently makes things up. The single biggest risk in GenAI. |

---

## 7. Customizing Foundation Models — Decision Matrix

You almost never need to train a model from scratch. Pick the *cheapest* option that meets your accuracy bar.

| Technique | What It Does | Cost & Effort | Data Needed | When to Choose |
|---|---|---|---|---|
| **Prompt Engineering** | Improve outputs by writing better instructions. | $ — hours | None | Always start here. Solves most use cases. |
| **Retrieval-Augmented Generation (RAG)** | Feed the model your docs at query time so it answers from your data. | $$ — days/weeks | Your enterprise documents (no labels) | You need answers grounded in private/current data. |
| **Fine-tuning (Instruction / RLHF)** | Adjust model weights with examples of good behavior. | $$$ — weeks | Hundreds–thousands of high-quality labeled examples | Tone, format, or domain language must be consistent. |
| **Continuous Pretraining** | Keep teaching the base model new vocabulary/data. | $$$$ — weeks/months | Large unlabeled domain corpus | Specialized industry (legal, medical, scientific) where vocabulary is unique. |
| **Train From Scratch** | Build a new FM end-to-end. | $$$$$ — months/years, $10M+ | Internet-scale data + GPU farm | Almost never the right answer for an enterprise. |

> **Decision shortcut:** Prompt → RAG → Fine-tune → Continuous pretrain. Stop as soon as the result is good enough.

---

## 8. Prompt Engineering Quick Guide

| Technique | What It Is | Mini Example | Use When |
|---|---|---|---|
| **Zero-shot** | Ask without examples. | "Classify this review as positive or negative: 'Great service!'" | Simple, well-known tasks. |
| **Few-shot (or one-shot)** | Provide a handful of input → output examples in the prompt. | Show 3 review/sentiment pairs, then ask the 4th. | Task is unusual or output format must be precise. |
| **Chain-of-thought (CoT)** | Tell the model to "think step by step" before answering. | "Calculate the discount, then the tax, then the total. Think step by step." | Multi-step reasoning, math, logic puzzles. |

> **Pro tip:** Combine techniques. Few-shot + CoT often beats either alone.

---

## 9. Prompt Risks & Misuse

| Risk | What It Is | Business Impact |
|---|---|---|
| **Prompt Injection** | User sneaks instructions into input to override the system prompt. | Bypass policies, leak data, take unauthorized actions. |
| **Prompt Leaking** | Attacker tricks the model into revealing the hidden system prompt. | IP loss, exposed business logic, easier follow-up attacks. |
| **Poisoning** | Malicious data introduced during training or RAG indexing. | Corrupts outputs at scale; hard to detect. |
| **Jailbreaking** | User crafts prompts that bypass safety guardrails (e.g., "pretend you're..."). | Toxic, illegal, or off-brand outputs. Reputational damage. |
| **Hijacking** | Attacker redirects the model's task (e.g., "ignore previous instructions and..."). | Loss of control over what the AI does. |

> **Mitigation:** Use AWS Bedrock Guardrails, input/output filtering, least-privilege agent permissions, and red-teaming before launch.

---

## 10. Model Evaluation in Business Terms

### Fit problems
| Problem | Plain English | Business Risk |
|---|---|---|
| **Underfitting** | Model is too simple — bad even on training data. | Cost of building with no payoff. |
| **Overfitting** | Memorizes training data, fails on new data. | Looks great in demos, breaks in production. |
| **Balanced** | Generalizes to new data. | The goal. |

### Bias vs Variance
- **Bias** = how far off predictions are from reality on average. High bias → consistently wrong.
- **Variance** = how much predictions jump around. High variance → unstable, sensitive to small data changes.

### GenAI quality metrics (you'll hear these in reviews)
| Metric | Measures | When Used |
|---|---|---|
| **ROUGE** | Overlap with a reference summary. | Summarization. |
| **BLEU** | Overlap with a reference translation. | Translation. |
| **BERTScore** | Semantic similarity (meaning, not just word match). | Summarization, paraphrase, generation quality. |

> **None of these replace human review.** For high-stakes use cases, budget for human evaluation panels.

---

## 11. When to Use AI (and When Not To)

### Good fit
- Rules are too complex or fuzzy to hand-code (e.g., spam, fraud, content moderation).
- Volume is too large for humans (millions of items).
- Patterns exist in data but aren't obvious to humans.
- Personalization at scale is needed.
- Creative or first-draft generation accelerates a knowledge worker.

### Bad fit (anti-patterns)
- A simple rule or lookup table would do the job.
- The cost of a wrong answer is catastrophic *and* you have no human-in-the-loop.
- You don't have the data, and can't get it.
- Regulatory or contractual constraints prohibit black-box decisions.
- You can't define what "success" looks like in measurable terms.

---

## 12. GenAI Benefits & Challenges

| Benefits | Challenges |
|---|---|
| Adapts to many tasks without retraining. | **Hallucinations** — confident but wrong. |
| Real-time, dynamic interactions. | **Bias** in training data carried into outputs. |
| Automates content creation at scale. | **Toxicity** — offensive or harmful outputs. |
| Sparks novel ideas and designs. | **Privacy** — risk of leaking sensitive data. |
| Works with relatively small fine-tuning data. | **Interpretability** — hard to explain why it said X. |
| Personalization for each user. | **Regulatory** — GDPR, HIPAA, EU AI Act exposure. |
| High throughput once deployed. | **Cost** — token + GPU spend can spiral. |

---

## 13. Responsible AI & Governance

### Three distinct functions (often confused)
| Function | Primary Goal |
|---|---|
| **Security** | Confidentiality, integrity, availability of data and systems. |
| **Governance** | Add value and manage risk in business operations. |
| **Compliance** | Adhere to laws, regulations, and standards. |

### Pillars of Responsible AI
- **Transparency** — users know they're interacting with AI.
- **Accountability** — clear ownership of model behavior.
- **Fairness** — bias testing across demographic slices.
- **Privacy** — PII handling, data minimization.
- **Safety** — guardrails, fallbacks, kill switches.
- **Explainability** — ability to justify decisions, especially in regulated domains.

### Governance framework starter (4 steps)
1. **Establish** an AI governance board (legal, compliance, security, business, AI/ML SMEs).
2. **Define** roles, decision rights, and escalation paths.
3. **Implement** policies covering the full lifecycle (data → model → deployment → monitoring).
4. **Audit** regularly — model cards, bias reports, incident reviews.

---

## 14. AWS Service Quick-Map

| Need | AWS Service | One-line What |
|---|---|---|
| Access foundation models via API | **Amazon Bedrock** | Managed catalog of FMs (Claude, Nova, Llama, Mistral, Stability) with one API. |
| Build, train, deploy custom ML models | **Amazon SageMaker AI** | End-to-end ML platform. |
| Pre-built ML models (vision, speech, text) | **Rekognition, Transcribe, Comprehend, Translate, Polly** | Use without ML expertise. |
| Enterprise document search | **Amazon Kendra** | Natural-language search over your docs. |
| Vector storage for RAG | **Amazon OpenSearch (vector engine), S3 Vectors** | Store and search embeddings. |
| Build agents that take actions | **Bedrock Agents / AgentCore** | Orchestrate tools, APIs, multi-step tasks. |
| Connect FMs to your knowledge | **Bedrock Knowledge Bases** | Managed RAG pipeline. |
| Safety guardrails on prompts/outputs | **Bedrock Guardrails** | Block PII, toxicity, off-topic. |
| Bias and explainability checks | **SageMaker Clarify** | Pre-deployment fairness audits. |
| Production model monitoring | **SageMaker Model Monitor** | Drift, data quality, anomaly detection. |
| ML experiment tracking | **SageMaker MLflow** | Version models, params, metrics. |
| Workflow orchestration | **Step Functions, EventBridge, MWAA** | Glue pipelines together. |
| Code assistance for developers | **Amazon Q Developer** | AI pair programmer. |
| Business intelligence Q&A | **Amazon Q Business** | Natural-language access to enterprise data. |

---

## 15. Azure Service Quick-Map

| Need | Azure Service | One-line What |
|---|---|---|
| Access foundation models via API | **Azure OpenAI Service** | Managed access to OpenAI models (GPT-5.x, o-series, embeddings, DALL-E, Sora). |
| Unified AI development & governance hub | **Microsoft Foundry** *(formerly Azure AI Foundry)* | One platform for model catalog, fine-tuning, eval, deployment, agents. |
| Pre-built AI capabilities (vision, speech, language, docs) | **Foundry Tools** *(formerly Azure AI Services)* | Use ready-made AI without training. |
| Enterprise document/vector search | **Azure AI Search** | Vector + semantic + hybrid search for RAG. |
| Build, train, deploy custom ML models | **Azure Machine Learning** | End-to-end MLOps platform. |
| Build agents that take actions | **Foundry Agent Service / Hosted Agents** | Managed runtime for production agents. |
| Connect agents to enterprise data | **Foundry IQ** | Managed knowledge engine over SharePoint, OneLake, ADLS, web. |
| Vector storage for RAG | **Azure Cosmos DB / Azure DocumentDB** | NoSQL with native vector search. |
| Safety guardrails on prompts/outputs | **Azure AI Content Safety** | Block harmful content, jailbreaks, PII. |
| Bias, fairness & explainability | **Responsible AI Dashboard** (in Azure ML) | Pre-deployment fairness audits. |
| Production model monitoring | **Azure ML Model Monitoring** | Drift, data quality, retraining triggers. |
| End-to-end AI app observability | **Foundry Observability Suite** | Evals, tracing, AI red-teaming. |
| Workflow orchestration | **Azure ML Pipelines / Functions / Logic Apps** | Glue ML workflows together. |
| Data governance & lineage | **Microsoft Purview** | Catalog, classify, track training data. |
| LLM API governance & cost control | **AI Gateway** *(via APIM)* | Rate limit, route, track token usage. |
| Code assistance for developers | **GitHub Copilot** | AI pair programmer (Microsoft-owned). |
| Business intelligence Q&A | **Microsoft Copilot for M365 / Fabric** | Natural-language access to enterprise data. |

---

## 16. GCP Service Quick-Map

| Need | GCP Service | One-line What |
|---|---|---|
| Access foundation models via API | **Gemini API / Vertex AI** | Gemini 2.5/3.x models — text, vision, audio, video. |
| Model catalog (1st-party + open + partner) | **Vertex AI Model Garden** | Gemini, Llama, Mistral, Imagen, Veo in one catalog. |
| Build, train, deploy custom ML models | **Vertex AI** | End-to-end ML platform. |
| Pre-built AI capabilities | **Vision AI, Speech-to-Text, Translation, Document AI, Natural Language AI** | Ready-made APIs, no training needed. |
| Enterprise document/vector search | **Vertex AI Search** | Search and grounding over your data. |
| Build agents that take actions | **Vertex AI Agent Engine / Agent Development Kit (ADK)** | Managed agent runtime + open-source SDK. |
| Build search & RAG-based agents | **Vertex AI Agent Builder** | Pre-built RAG agents grounded in your docs. |
| Production-grade RAG pipelines | **Vertex AI RAG Engine** | Managed chunking, embedding, retrieval. |
| Vector storage for RAG | **AlloyDB AI / Cloud Spanner / BigQuery** | Vector search inside operational/analytical DBs. |
| Safety guardrails on prompts/outputs | **Model Armor** | Prompt injection, content filtering, grounding checks. |
| PII detection & redaction | **Cloud DLP / Sensitive Data Protection** | Scan and redact sensitive data. |
| Production model monitoring | **Vertex AI Model Monitoring** | Drift, skew, data quality alerts. |
| Workflow orchestration | **Vertex AI Pipelines / Cloud Composer / Workflows** | ML and general-purpose orchestration. |
| Data governance & lineage | **Dataplex / BigQuery Governance** | Catalog, lineage, quality, classification. |
| Business agent platform | **Google Agentspace** | Enterprise agent gallery + Workspace integration. |
| Code assistance for developers | **Gemini Code Assist** | AI pair programmer. |
| Business intelligence Q&A | **Gemini in BigQuery / Looker** | Natural-language analytics. |

---

## 17. Cross-Cloud Equivalents at a Glance

| Capability | AWS | Azure | GCP |
|---|---|---|---|
| **Managed FM access** | Amazon Bedrock | Azure OpenAI / Microsoft Foundry | Vertex AI / Gemini API |
| **Custom ML platform** | SageMaker AI | Azure Machine Learning | Vertex AI |
| **Pre-built AI APIs** | Rekognition, Comprehend, Transcribe, etc. | Foundry Tools (Vision, Speech, Language) | Vision AI, Speech-to-Text, Document AI |
| **Enterprise search / RAG** | Amazon Kendra + Bedrock Knowledge Bases | Azure AI Search + Foundry IQ | Vertex AI Search + RAG Engine |
| **Vector database** | OpenSearch (vector), S3 Vectors | Cosmos DB, DocumentDB | AlloyDB AI, Spanner, BigQuery |
| **Agent runtime** | Bedrock Agents / AgentCore | Foundry Agent Service | Vertex AI Agent Engine |
| **Safety guardrails** | Bedrock Guardrails | Azure AI Content Safety | Model Armor |
| **Bias / fairness** | SageMaker Clarify | Responsible AI Dashboard | Vertex AI Model Evaluation + Explainable AI |
| **Model monitoring** | SageMaker Model Monitor | Azure ML Model Monitoring | Vertex AI Model Monitoring |
| **Experiment tracking** | SageMaker MLflow | Azure ML Experiments | Vertex AI Experiments |
| **Workflow orchestration** | Step Functions, EventBridge, MWAA | Azure ML Pipelines, Logic Apps | Vertex AI Pipelines, Cloud Composer |
| **Code assistant** | Amazon Q Developer | GitHub Copilot | Gemini Code Assist |
| **Business AI assistant** | Amazon Q Business | Microsoft Copilot (M365 / Fabric) | Gemini in Workspace, Agentspace |

> **For deeper technical comparison**, see [`cross-cloud-ai-comparison.md`](cross-cloud-ai-comparison.md).

---

## 18. Glossary

| Term | Meaning |
|---|---|
| **AI** | Artificial Intelligence. |
| **Agent** | Software that uses an LLM to plan and take actions via tools/APIs. |
| **BERTScore** | Semantic similarity metric for generated text. |
| **BLEU** | Bilingual Evaluation Understudy — translation quality metric. |
| **CoT** | Chain-of-Thought — prompting technique for step-by-step reasoning. |
| **Diffusion model** | Generates images by denoising random noise step-by-step. |
| **Embedding** | Numerical (vector) representation of meaning. |
| **FM** | Foundation Model. |
| **Fine-tuning** | Adjusting an FM's weights with task-specific data. |
| **GAN** | Generative Adversarial Network — generator vs discriminator. |
| **GenAI** | Generative AI. |
| **Hallucination** | Confident but false output from a generative model. |
| **Inference** | Running a model to produce output. |
| **k-NN** | k-Nearest Neighbors — similarity search algorithm. |
| **LLM** | Large Language Model. |
| **ML** | Machine Learning. |
| **MLOps** | DevOps practices applied to ML lifecycle. |
| **Multimodal** | Model handling more than one data type (text + image, etc.). |
| **PII** | Personally Identifiable Information. |
| **Prompt** | Instruction given to a generative model. |
| **RAG** | Retrieval-Augmented Generation — inject your docs at query time. |
| **RLHF** | Reinforcement Learning from Human Feedback. |
| **ROI** | Return on Investment. |
| **ROUGE** | Recall-Oriented Understudy for Gisting Evaluation — summary metric. |
| **SageMaker** | AWS managed ML platform. |
| **Token** | Smallest text chunk a model processes (~¾ of a word). |
| **Transformer** | Neural network architecture behind modern LLMs. |
| **VAE** | Variational Autoencoder — encoder + decoder generative model. |
| **Vector database** | Storage optimized for similarity search over embeddings. |
| **Zero-shot / Few-shot** | Prompting with no / a few examples. |

---

## 19. Questions to Ask Before Approving an AI Project

A 10-question gate for any AI investment proposal.

1. **What's the business outcome in dollars or hours saved?** (If unanswerable, stop.)
2. **What's the cost of a wrong answer, and who absorbs it?** (Customer? Regulator? Brand?)
3. **Do we have the data — labeled, clean, accessible, and lawful to use?**
4. **What's the simpler non-AI baseline, and how much better must AI be to justify the cost?**
5. **What's the evaluation plan?** (Metrics, human review, pre-launch and ongoing.)
6. **What's the fallback** when the model is unavailable, slow, or wrong?
7. **What governance review is needed?** (Privacy, legal, security, compliance, model card.)
8. **What's the run-rate cost?** (Tokens, GPUs, storage, monitoring, retraining cadence.)
9. **Who owns the model in production** — incidents, retraining, deprecation?
10. **What's the kill criteria?** (When do we shut it down or roll back?)

---

*End of cheat sheet. For technical implementation details, see [`aws-ai-mlops-cheatsheet.md`](aws-ai-mlops-cheatsheet.md), [`azure-ai-mlops-cheatsheet.md`](azure-ai-mlops-cheatsheet.md), and [`gcp-ai-mlops-cheatsheet.md`](gcp-ai-mlops-cheatsheet.md). For deeper cross-cloud comparison, see [`cross-cloud-ai-comparison.md`](cross-cloud-ai-comparison.md).*
