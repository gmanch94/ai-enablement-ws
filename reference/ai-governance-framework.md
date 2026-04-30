# AI Governance Framework

> Architect-grade reference. Synthesizes public sources on AI governance: NIST AI RMF (2023, 2024), EU AI Act (Regulation 2024/1689), GDPR (2018), Harvard Berkman Klein *Principled Artificial Intelligence* (Fjeld et al., 2020), and core academic work on algorithm aversion, interpretability, and fairness. Use it as the substrate for ADRs, threat models, and red-team plans in this workspace.

---

## 1. Why AI Governance

AI algorithms exhibit behaviors driven by two forces — analogous to human nature and nurture:

- **Nature** — the rules and logic programmed by developers
- **Nurture** — the data from which the model learns

When data carries historical biases, the AI inherits them — even when no bias was intentionally programmed. Governance exists to prevent, detect, and correct these failures before they cause harm.

**Business case for governance (risks cascade):**

| Societal Risk | Organizational Risk |
|--------------|---------------------|
| Harms of allocation (biased resource decisions) | Reputational damage, PR backlash |
| Harms of representation (unfavorable group portrayal) | Legal liability, discrimination lawsuits |
| Erosion of public trust | Regulatory penalties and compliance costs |

---

## 2. Risk Taxonomy

### 2.1 Statistical Risks

**Overfitting**
- Complex models (neural nets, gradient boosting) fit historical data too well
- Fail to generalize to real-world conditions outside training distribution
- Consequences: financial losses (trading algorithms), customer churn (poor personalization)
- Mitigation: mandatory stress testing, validation on held-out data, out-of-distribution testing

### 2.2 Social and Ethical Risks

| Risk Category | Example | Root Cause |
|--------------|---------|-----------|
| **Algorithmic bias** | Amazon resume screening (gender bias) | Historical hiring data encoded sexism |
| **Racial discrimination** | COMPAS sentencing (2× false positives for Black defendants) | Proxy variables in historical crime data |
| **Chatbot failure** | Microsoft Tay (racist content in 24 hours) | No content governance; learned from adversarial users |
| **Manipulation** | Facebook emotional contagion experiment | Algorithm optimized engagement over user wellbeing |
| **Market manipulation** | Algorithmic price collusion (DOJ 2018) | ML algorithms self-discovered collusion strategies |
| **Data exploitation** | Targeting teenagers in emotional distress | Optimization without ethical constraints |

### 2.3 Industry Risk Categorization (4-domain pattern)

A common four-domain split widely used by enterprise AI risk programs (variant of NIST AI RMF *MAP* function):

| Category | Sub-risks |
|---------|-----------|
| **Data-related** | Training data quality, learning limitations, distribution shift |
| **AI attacks** | Data poisoning, adversarial inputs, model extraction, backdoor embedding |
| **Testing & Trust** | Bias detection, explainability gaps, calibration failures |
| **Compliance** | Internal policy violations, regulatory non-compliance |

> **Key principle:** Risk profile is context-dependent. Cloud-deployed models face higher attack risk. Internal models face higher compliance risk. No universal risk ranking — see NIST AI RMF *MAP* and *MEASURE* functions for the structured assessment workflow.

---

## 3. Three Pillars of AI Governance

### Pillar 1 — Controls (Human in the Loop)

**What:** Give users meaningful ability to override or influence algorithmic decisions.

**Why:** User trust requires perceived agency. Without any control, users reject systems even when they perform well.

**Research finding (Dietvorst, Simmons, Massey 2018, *Management Science* — "Overcoming Algorithm Aversion: People Will Use Imperfect Algorithms If They Can (Even Slightly) Modify Them"):**
- Users with **no control over algorithm output**: low usage, prefer human judgment
- Users allowed even **minor adjustments** to algorithm output: significantly higher usage and trust
- Beyond a threshold, additional override latitude does not produce proportionally more trust
- **Practical conclusion:** Designing in even small override affordances raises adoption substantially. Whether unconstrained overrides degrade overall accuracy is a separate question — see Dietvorst, Simmons, Massey (2015), *Algorithm Aversion: People Erroneously Avoid Algorithms After Seeing Them Err*, JEP General 144(1), for evidence that humans tend to under-use algorithms even when those algorithms outperform human judgment.

**Design principle — "Just enough control":**
> Give users the ability to flag problems and overrule clearly wrong decisions — but don't hand full control back to humans who may make worse decisions than the algorithm.

**Implementation examples:**

| Context | Control Mechanism |
|---------|------------------|
| Social media newsfeed | User flags posts as false or offensive |
| Loan approval | Applicant can request human review |
| HR recommendation | Hiring manager can override with documented rationale |
| Medical diagnosis | Physician required to confirm or override AI recommendation |

**Caution:** Facebook 2015 mixer controls experiment — user satisfaction increased, but engagement dropped significantly. The algorithm better understood what engaged users than the users themselves.

---

### Pillar 2 — Transparency (Calibrated)

**What:** Provide users with meaningful, understandable information about how algorithmic decisions are made.

**Why:** Transparency builds trust — but the type and amount of transparency matter critically.

**Research finding (Kizilcec 2016, CHI — "How Much Information? Effects of Transparency on Trust in an Algorithmic Interface"):**

| Transparency Level | Trust Outcome |
|-------------------|--------------|
| No explanation | Low trust |
| Limited explanation (key factors) | High trust |
| Detailed explanation (full formulas) | Low trust (too complex to process) |

**What NOT to do — Technical Transparency (revealing source code):**
- Does not protect users' interests
- Exposes proprietary IP
- Creates adversarial vulnerability (hackers can identify weaknesses)
- Average user cannot evaluate source code anyway
- **Rejected by:** CFTC (2015 flash crash ruling), NYC automated decisions bill (2017)

**Calibrated Transparency — The Right Approach:**

Answer these questions for affected users:

1. **Was an algorithm used** to make this decision?
2. **What data** was used as input?
3. **What variables** were considered?
4. **What were the most important factors** in this specific decision?

#### Global vs. Local Interpretability

| Type | Scope | Example |
|------|-------|---------|
| **Global** | Model-level: what factors drive decisions overall | "Loan approvals driven primarily by income (40%), credit history (30%), debt ratio (20%)" |
| **Local** | Decision-level: why this specific decision was made | "Your application was denied primarily due to debt-to-income ratio of 0.45, above the 0.40 threshold" |

**Tools for Interpretable ML:**
- **SHAP** (Shapley Additive Explanations): computes each feature's contribution to a prediction
- **LIME** (Local Interpretable Model-Agnostic Explanations): local linear approximation for similar instances
- **Surrogate decision trees**: simpler interpretable model that mimics complex model
- **Variational autoencoders**: distills data to interpretable intermediate features

**Commercial implementations:** Microsoft InterpretML, IBM Explainable AI 360, Google Model Cards, Microsoft Datasheets for Datasets

---

### Pillar 3 — Audits (Risk-Based)

**What:** Systematic, structured review of ML models before deployment and on an ongoing basis.

**Why:** Even well-intentioned models contain hidden biases, overfitting, or failure modes that can only be discovered through adversarial testing.

**Audit process:**

#### Step 1: Model Inventory
Create a complete catalog of all ML models in production:

| Field | Description |
|-------|-------------|
| Use case | What decision does this model make? |
| Developer | Who built it? |
| Business owner | Which team/individual is accountable? |
| Risk rating | Social and financial impact if model fails |

#### Step 2: Risk-Based Prioritization

Not all models require a full audit. Prioritize based on:
- Decisions affecting people's lives, employment, finance, or legal status
- High-volume automated decisions with limited human review
- Models using sensitive data or proxy variables

#### Step 3: Audit Scope (Three Areas)

**Inputs:**
- Training data quality and completeness
- Bias detection in training data
- Representativeness of minority populations

**Model:**
- Benchmark against alternative models
- Statistical tests for overfitting and fit quality
- Model transparency and interpretability
- Stress testing against simulated out-of-distribution data

**Outputs:**
- Sample of decisions with explanations
- Outlier analysis (extreme inputs → extreme outputs)
- Fairness metric evaluation
- Comparison of outcomes across demographic groups

#### Step 4: Three Lines of Defense

```
Model Developer  →  Data Science QA  →  Data Science Auditor
   (builds)            (tests)              (validates, high-stakes only)
```

Analogous to software engineering: developers → QA testers → security auditors. Separation of concerns prevents groupthink and catches errors across the pipeline.

---

## 4. Algorithmic Bias — Prevention and Response

### 4.1 Sources of Bias

| Source | Mechanism | Example |
|--------|-----------|---------|
| **Historical bias in data** | Past human decisions encoded prejudice | Gender bias in historical hiring → algorithm learns gender = negative signal |
| **Sparse minority representation** | Less training data for minority groups → less accurate models | Facial recognition less accurate for darker skin tones |
| **Proxy variables** | Neutral-seeming variables encode protected class | Zip code strongly correlated with race; name patterns encode ethnicity |
| **Inferential privacy violation** | Sensitive attributes inferred without being asked | Algorithm predicts sexual orientation from Facebook profile photos |

### 4.2 Types of Harm (AI Now Institute)

**Harms of Allocation:** Bias in distributing scarce resources
- Loan approvals, job applications, bail/sentencing decisions
- Systematic disadvantage for protected groups in obtaining valued resources

**Harms of Representation:** Bias in how groups are portrayed or treated
- Airport screening systems over-flagging minorities
- Translation systems imposing gendered stereotypes

### 4.3 Organizational Response Checklist

- [ ] **Deep and diverse training data** — ensure sufficient examples across all demographic groups
- [ ] **Audit for proxy variables** — test whether neutral variables (zip code, name, time patterns) encode protected class attributes
- [ ] **Select appropriate fairness function** — individual vs. group fairness trade-offs must be made explicitly
- [ ] **Test and evaluate before deployment** — use bias detection tools to assess discriminatory impacts
- [ ] **Monitor after deployment** — models drift; re-audit regularly
- [ ] **Build diverse teams** — people who have experienced discrimination are far more likely to flag issues in design

> **Critical insight:** Individual fairness and group fairness are mathematically incompatible. No algorithm can simultaneously satisfy both. Governance requires explicit, documented choices about which fairness definition to prioritize.

### 4.4 Fairness Definitions (Choose Explicitly)

| Definition | What it Means | Limitation |
|------------|--------------|-----------|
| **Individual fairness** | Similar individuals receive similar outcomes | Can mask group-level disparate impact |
| **Group/demographic parity** | Equal outcomes across groups | Can require different treatment of similar individuals |
| **Equalized odds** | Equal true positive and false positive rates across groups | Mathematically incompatible with demographic parity |
| **Calibration** | Predicted probabilities match actual outcomes across groups | Different from equal error rates |

---

## 5. Manipulation — Prevention

### 5.1 Forms of Algorithmic Manipulation

| Form | Example | Test |
|------|---------|------|
| **Emotional manipulation** | Facebook emotional contagion experiment | Would users consent if they knew? |
| **Exploitation** | Airlines separating families to force upgrades | Targets vulnerability to extract involuntary agreement |
| **Market manipulation** | Algorithmic collusion on pricing | Antitrust/competition law applies |
| **Deception** | Undisclosed chatbots, hidden algorithmic curation | Users assume human interaction |

### 5.2 Belmont Report Principles (Applied to AI)

Developed for academic research on human subjects; adopted as AI ethics foundation:

| Principle | Definition | AI Application |
|-----------|-----------|----------------|
| **Informed consent** | Users understand what they're getting into | Disclose when algorithms make decisions affecting users |
| **Beneficence** | Do not harm | Don't expose users to serious psychological, financial, or physical harm |
| **Justice** | Non-exploitative, applied fairly | Don't target vulnerable populations; don't exploit emotional states |
| **Dedicated review** | Independent oversight before deployment | Center of Excellence / AI ethics committee |

### 5.3 Governance Test for Manipulation

Before deploying an AI system, ask:
> *"If users fully understood how this system works and what it's optimizing for, would they still choose to use it?"*

If the answer is no — or uncertain — re-evaluate the system's objectives.

---

## 6. Data Protection

### 6.1 Privacy Lifecycle — Five Stages

Governance must address **all five stages**, not just collection:

| Stage | Key Risk | Governance Action |
|-------|---------|------------------|
| **1. Collection** | Collecting more than necessary | Data minimization; purpose specification |
| **2. Aggregation/Analysis** | Revealing sensitive attributes through combination | Feature engineering audit; inferential risk assessment |
| **3. Storage** | Data breach exposes large sensitive dataset | Encryption, access controls, retention limits |
| **4. Use** | Data used beyond original consent context | Contextual integrity review; purpose limitation enforcement |
| **5. Distribution** | Third-party data broker misuse | Contractual data use restrictions; vendor audits |

> **Contextual integrity principle** (Helen Nissenbaum): Users expect data to flow in ways appropriate to the context in which it was shared. Medical data shared with a doctor should not flow to advertisers — even if technically permitted in fine-print consent. Governance must ask: "Is this data use consistent with the norms of the context in which it was collected?" If not, re-obtain consent or don't use it.

### 6.2 Novel Risks from AI/ML

- **Scale:** ML requires massive datasets → more data from more people
- **Inferential privacy violations:** Algorithms infer sensitive attributes (sexual orientation, health status) without explicitly asking
- **Data transfer:** Model updates require moving personal data across networks → federated learning as mitigation

### 6.3 Legal Framework Comparison

| Dimension | US Approach | EU GDPR Approach |
|-----------|------------|-----------------|
| **Foundation** | Market-based, user choice | Human rights-based |
| **Opt-in/out** | Opt-out default | Opt-in required |
| **Purpose specification** | Not required | Required before collection |
| **Data brokers** | Gray area | Explicitly regulated |
| **Automated processing** | No specific rules | Additional rules apply |
| **Substantive rights** | Limited | Correction, erasure, portability, explanation |
| **Scope** | Sectoral (healthcare, finance, children) | Comprehensive, all sectors |
| **Geographic reach** | US entities | Any data about EU citizens, anywhere |

**Trend:** World is converging toward EU-style approach. California CCPA, China data laws, Japan, South America all moving in this direction. Multinational firms should implement highest-standard approach globally.

### 6.4 Technical Privacy Solutions

| Technique | How It Works | Trade-off |
|-----------|-------------|-----------|
| **Federated learning** | Model trains locally on each device; only model updates (not raw data) sent centrally | Slower convergence; higher communication cost |
| **Differential privacy** | Mathematically calibrated noise added to datasets; statistical queries produce equivalent results but individual identification prevented | More noise = less accuracy; tunable trade-off |
| **Privacy by Design** | Privacy considerations incorporated at every development stage, not bolted on at end | Requires discipline across entire development lifecycle |

**Implementations:** Apple (differential privacy for iPhone data), Uber (rider data queries), US Census 2020 (differential privacy for national dataset)

### 6.5 Operational Governance: Privacy by Design

Formally incorporated into EU GDPR. Framework:

1. **Proactive not reactive** — anticipate and prevent privacy risks before they occur
2. **Privacy as default** — default settings should automatically protect privacy
3. **Privacy embedded into design** — not an add-on; integral to system architecture
4. **Full functionality** — privacy and functionality are not zero-sum
5. **End-to-end security** — lifecycle protection from collection to destruction
6. **Visibility and transparency** — all practices publicly documented
7. **User-centric** — strong privacy rights for individual users

---

## 7. Explainability and the Law

### 7.1 Legal Explainability Requirements

| Law / Regulation | Jurisdiction | Requirement | Status |
|-----------------|-------------|-------------|--------|
| Equal Credit Opportunity Act (ECOA) | US | Adverse action notice with "principal reasons" for credit denial | In force since 1974 |
| Fair Credit Reporting Act (FCRA) | US | Consumer access to credit reports used in decisions | In force since 1970 |
| GDPR Article 22 | EU | Right to explanation for fully automated consequential decisions | In force since 2018 |
| California CCPA | US (California) | Consumer rights around data collection and use | In force since 2020 |
| Algorithmic Accountability Act | US (Federal) | Formal bias audits for high-risk automated decision systems | Proposed; not yet passed |
| EU AI Act (Regulation 2024/1689) | EU | Risk-tiered AI regulation; prohibited practices, high-risk system requirements, GPAI model obligations | **In force August 2024**; prohibited practices from Feb 2025; high-risk compliance from Aug 2026 |

**Case law:** Houston teachers fired by black-box test score algorithm — US federal appeals court ruled absence of explanation violated **constitutional Due Process rights**. Algorithm use was discontinued.

### 7.2 When Explainability is Non-Negotiable

| Domain | Reason |
|--------|--------|
| HR decisions (hiring, promotion, termination) | EEOC guidelines require documented decision rationale |
| Financial lending | Credit law requires adverse action explanation; GDPR applies to automated decisions |
| Criminal justice (bail, sentencing, parole) | Constitutional due process; high stakes for individual liberty |
| Autonomous vehicles | Accident investigation requires reconstructing decision sequence |
| Healthcare | Physicians must understand and justify treatment decisions to patients |

### 7.3 Explainability vs. Accuracy Trade-off

| Model Type | Explainability | Predictive Power |
|-----------|---------------|-----------------|
| Business rules | High | Low |
| Linear/logistic regression | High | Medium |
| Decision trees | Medium-high | Medium |
| Random forests | Low | High |
| Neural networks / deep learning | Very low | Very high |

**Key decision:** In regulated, high-stakes domains (HR, healthcare, lending), **a less accurate but explainable model may be legally and ethically required** over a more accurate black-box model.

---

## 8. AI Ethics Principles

### 8.1 Eight Common Principles (Harvard 2020 — 36 Frameworks Analyzed)

Analyzed frameworks from Microsoft, Telefonica, Tencent, standards bodies, and governments worldwide. Principles are converging globally:

| Principle | What It Means |
|-----------|--------------|
| **Privacy** | Protect personal data throughout the AI lifecycle |
| **Accountability** | Clear ownership of AI outcomes; someone is responsible |
| **Safety & Security** | Systems do not cause unintended harm; robust against attacks |
| **Transparency & Explainability** | Decisions can be understood and explained |
| **Fairness & Non-discrimination** | Outcomes are equitable across groups |
| **Human Control** | Humans can override, correct, or shut down AI systems |
| **Professional Responsibility** | Ethical/legal concerns infused throughout org and process |
| **Promotion of Human Values** | AI ultimately serves human flourishing |

### 8.2 Making Principles Operational

Principles are only valuable if they are **pervasively applied** across the organization, not checked as a box once at deployment.

**Implementation steps:**
1. Connect AI ethics principles to broader organizational values
2. If you define yourself as customer-centric — demonstrate it in every AI initiative
3. If you've made a public commitment to racial justice — ensure AI systems reflect it
4. Build **concentrated expertise** (ethics committee, legal counsel) AND **diffuse responsibility** (every team member asks ethical questions)
5. Ethics committee/Center of Excellence should review major AI implementations but cannot replace individual responsibility

---

## 9. Governance Operating Model

### 9.1 Governance Structure

```
Board / Executive Oversight
         │
    AI Governance Committee
    (Ethics + Legal + Risk + Business)
         │
    ┌────┴────┐
    │         │
AI Center    Model Risk
of Excellence  Management
    │
    ├── Model Developers
    ├── Data Science QA
    └── Data Science Auditors (high-stakes)
```

### 9.2 Model Risk Management Process

```
Idea → Design → Development → QA Testing → Risk Assessment → Deployment → Monitoring
  ↑                                              │
  └──────────────────────────────────────────────┘
                  Continuous feedback loop
```

### 9.3 Governance Checklist by AI System Risk Level

| Risk Level | Examples | Governance Requirements |
|-----------|---------|------------------------|
| **Low** | Internal efficiency tools, content recommendations | Standard QA; document use case and data sources |
| **Medium** | Customer personalization, fraud detection | Bias testing; fairness audit; interpretability documentation |
| **High** | HR decisions, credit decisions, healthcare, criminal justice | Full audit (inputs + model + outputs); legal review; explainability required; ongoing monitoring |

### 9.4 Model Card Template (Google Standard)

For each deployed ML model, document:

1. **Model details:** Architecture, training approach, version
2. **Intended use:** What it's for; what it's NOT for
3. **Factors:** Relevant demographic, environmental, instrumentation factors
4. **Metrics:** Evaluation metrics and their thresholds
5. **Evaluation data:** How test data was collected; diversity
6. **Training data:** What was used and why
7. **Quantitative analyses:** Disaggregated results by subgroup
8. **Ethical considerations:** Sensitive use cases; risks
9. **Caveats and recommendations:** Limitations; monitoring requirements

---

## 10. Regulatory Landscape

### 10.1 Existing Regulation

- **EU GDPR** (2018): Comprehensive data protection; right to explanation for automated decisions; applies globally for EU citizen data
- **CCPA** (California, 2020): Consumer data rights; opt-out of sale of personal information
- **ECOA/FCRA** (US, 1970s): Credit reporting explainability; adverse action notices
- **EEOC guidelines** (US): Employment decisions must be documented and non-discriminatory
- **EU AI Act** (in force August 2024): Risk-tiered regulation — see 10.4 for full detail

### 10.2 Active / Proposed Regulation

- **Algorithmic Accountability Act** (proposed US federal): Bias audits for high-risk automated decision systems — not yet passed
- **Disparate impact doctrine**: US law prohibiting facially neutral practices with discriminatory effect (limited current application to AI)
- **NIST AI Risk Management Framework** (AI RMF 1.0, 2023; 2.0, 2024): Voluntary US framework; four functions — **GOVERN, MAP, MEASURE, MANAGE**. Widely adopted; aligns with ISO/IEC 42001 and EU AI Act. The de facto US enterprise governance standard. Profiles available for specific sectors (finance, healthcare, generative AI)

### 10.3 Voluntary Standards

| Standard | Issuer | Scope |
|----------|--------|-------|
| **NIST AI RMF** | US NIST | Voluntary; four-function lifecycle framework; sector profiles available |
| **ISO/IEC 42001** | ISO | International AI management system standard; maps to NIST AI RMF and EU AI Act |
| **Model Cards** | Google | Standardized per-model documentation |
| **Datasheets for Datasets** | Microsoft | Standardized dataset provenance documentation |

### 10.4 EU AI Act — Risk Tiers and Obligations

**In force:** August 1, 2024. **Enforcement timeline:**

| Milestone | Date |
|-----------|------|
| Prohibited practices banned | February 2, 2025 |
| GPAI model obligations | August 2, 2025 |
| High-risk system compliance required | August 2, 2026 |
| Full enforcement | August 2, 2027 |
| Fines | €7.5M–€35M or 1–7% global annual turnover |

**Four risk tiers:**

| Tier | Examples | Obligations |
|------|---------|-------------|
| **Unacceptable (Prohibited)** | Social scoring, predictive policing, real-time biometric ID in public | Banned outright (Feb 2025) |
| **High-risk** | HR decisions, credit, healthcare, education, law enforcement, critical infrastructure | Risk management system, data governance, human oversight, bias testing, conformity assessment, public registration |
| **Limited risk** | Chatbots, deepfakes, emotion inference (outside prohibited scope) | Transparency/disclosure obligations |
| **Minimal risk** | Spam filters, AI in games | No specific obligations |

**Eight prohibited practices (Unacceptable Risk tier):**
1. Subliminal or deceptive manipulation causing harm
2. Exploitation of vulnerabilities (age, disability, socioeconomic)
3. Social scoring by governments or public authorities
4. Predictive policing based solely on profiling
5. Real-time remote biometric identification in public spaces (narrow law enforcement exceptions)
6. Biometric categorization inferring race, politics, religion, sexual orientation
7. Emotion recognition in workplaces or educational institutions
8. Scraping facial images from internet/CCTV to build recognition databases

**GPAI models** (foundation models like GPT/Claude/Gemini): Subject to transparency, copyright compliance, and technical documentation requirements. Systemic-risk threshold: training compute > 10^25 FLOPs triggers additional obligations (adversarial testing, incident reporting, cybersecurity measures).

### 10.5 Strategic Regulatory Posture

**Proactive approach (recommended):**
- Don't wait for regulation — implement governance now to win consumer trust
- Get ahead of legal requirements on explainability and bias auditing
- Regulatory compliance will only become more demanding; build the capability early

**Race to the top:**
- Multinational firms facing strictest rules in any jurisdiction increasingly implement highest standard globally
- Single global governance standard is more efficient than jurisdiction-by-jurisdiction compliance

---

## Key References (public sources)

- Hosanagar, K.: *A Human's Guide to Machine Intelligence* (Viking, 2019)
- Fjeld, J., Achten, N., Hilligoss, H., Nagy, A., Srikumar, M.: *Principled Artificial Intelligence: Mapping Consensus in Ethical and Rights-Based Approaches to Principles for AI* (Berkman Klein Center, Harvard, 2020)
- Dietvorst, B. J., Simmons, J. P., Massey, C.: *Overcoming Algorithm Aversion: People Will Use Imperfect Algorithms If They Can (Even Slightly) Modify Them*, Management Science 64(3) (2018)
- Kizilcec, R. F.: *How Much Information? Effects of Transparency on Trust in an Algorithmic Interface*, CHI (2016)
- AI Now Institute: *AI Now Report* (annual)
- Cavoukian, A.: *Privacy by Design — The 7 Foundational Principles* (Ontario Privacy Commissioner, 2009)
- Zuboff, S.: *The Age of Surveillance Capitalism* (PublicAffairs, 2019)
- EU: *General Data Protection Regulation* (GDPR, Regulation 2016/679, in force 2018)
- EU: *AI Act* (Regulation 2024/1689, in force August 2024)
- NIST: *AI Risk Management Framework* (AI RMF 1.0, 2023; subsequent updates including Generative AI Profile, 2024)
- ISO/IEC 42001: *Information technology — Artificial intelligence — Management system* (2023)
- Nissenbaum, H.: *Privacy as Contextual Integrity*, Washington Law Review 79(1) (2004)
- Lundberg, S. M., Lee, S.-I.: *A Unified Approach to Interpreting Model Predictions* (SHAP), NeurIPS (2017)
- Ribeiro, M. T., Singh, S., Guestrin, C.: *"Why Should I Trust You?": Explaining the Predictions of Any Classifier* (LIME), KDD (2016)

---

## Companion skills + artifacts

| Pair with | Why |
|---|---|
| `/threat-model` skill | Apply §2 Risk Taxonomy + §10.4 EU AI Act tiering to a specific system |
| `/red-team` skill | Operationalize §4 Bias Prevention + §5 Manipulation governance test |
| `/eval-design` skill | Build the metric design referenced in §3 Pillar 3 (Audits) and §9.4 Model Cards |
| `/model-card` skill | Implement the §9.4 Google Model Cards template |
| `governance-playbook-general.html` (templates/governance/) | Pre-deployment risk-tier playbook — operationalizes this framework |
| `bias-audit-general.html` + `bias-audit-hr.html` (templates/governance/) | Audit templates for §4.3 organizational response checklist |
| `genai-risk-checklist.html` (templates/governance/) | Pre-deployment GenAI-specific risk checklist |
| `ai-hr-governance-framework.md` (reference/) | Sector-specific complement (employment law: EEOC 4/5ths, GDPR Art. 22, NYC LL 144) |
