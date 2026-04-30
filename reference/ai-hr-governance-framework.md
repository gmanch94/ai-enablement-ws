# AI Governance Framework for HR

> Architect-grade reference for AI used in employment decisions (hiring, performance, promotion, attrition, compensation). Companion to the general `ai-governance-framework.md` — adds employment-law-specific obligations (EEOC 4/5ths, GDPR Art. 22, NYC LL 144, IL AIVIA, BIPA, ADEA/ADA/Title VII).

---

## 1. Why HR AI Demands Specialized Governance

HR AI is inherently high-stakes. Unlike product recommendation or logistics optimization, HR AI decisions affect employment — people's livelihoods, professional trajectories, and economic security. This creates:

- **Legal exposure**: Discriminatory employment decisions violate federal and state law regardless of whether they were made by humans or algorithms
- **Trust risk**: Employees who distrust HR AI tools disengage and leave; the tool meant to solve attrition worsens it
- **Irreversibility**: Candidates rejected, employees fired, or promotions denied based on biased AI create harms that are difficult to remedy
- **Power asymmetry**: Employees typically cannot see, challenge, or opt out of AI used to evaluate them

**Governance principle**: The fact that a machine made the decision does not transfer moral or legal responsibility away from the organization. The organization is accountable for the decisions made by its AI systems.

---

## 2. Risk Taxonomy for HR AI

### Tier 1 — Unacceptable Risk

Uses of AI that should not proceed regardless of technical capability:
- Fully automated termination decisions with no human review
- Predictive policing of employee misconduct without behavioral evidence
- Emotional state inference from biometric data to make employment decisions
- AI video interview analysis as the sole determinant of hiring eligibility

### Tier 2 — High Risk (Mandatory Governance)

AI that directly informs consequential employment decisions:
- Candidate screening and scoring for hiring
- Attrition risk scoring that informs employment-protection decisions
- Performance evaluation scoring or ranking
- Compensation and promotion decision support
- Skills gap identification for performance improvement plans

**Required governance**: Bias audit before deployment, human review before decision execution, explanation capability, employee notification, appeal mechanism.

### Tier 3 — Medium Risk (Standard Governance)

AI that informs HR planning without directly triggering individual decisions:
- Workforce planning models (aggregate headcount forecasting)
- Engagement sentiment analysis at aggregate/team level
- Internal career path recommendations (opt-in, non-consequential)
- Job description language optimization
- Learning and development recommendations

**Required governance**: Data privacy compliance, periodic bias monitoring, transparency with employees about use.

### Tier 4 — Low Risk

Administrative automation with no discriminatory potential:
- Interview scheduling
- Benefits enrollment assistance
- HR policy FAQ chatbots
- Payroll processing automation

**Required governance**: Standard IT security and data protection.

---

## 3. Three Governance Pillars

### Pillar 1: Controls

**Pre-deployment controls**:
- Mandatory bias audit for Tier 1–2 systems
- Legal review against applicable regulations (EEOC, GDPR, state law)
- Data quality assessment (representation, accuracy, recency)
- Proxy variable analysis (identify features correlated with protected attributes)
- Fairness metric selection and documentation
- Disparate impact testing against 4/5ths rule (EEOC standard)

**Deployment controls**:
- Human-in-the-loop checkpoints for all Tier 2 decisions
- Score thresholds — model output is advisory, not deterministic
- Override logging — track all cases where human overrides AI recommendation (signals for model drift or systematic error)
- Access controls — limit who can see individual-level AI scores

**Post-deployment controls**:
- Quarterly performance monitoring (accuracy, bias drift, false positive/negative rates)
- Trigger for re-audit: major workforce composition change, economic shock, regulatory update
- Incident reporting process for identified bias or errors
- Version control and audit trail for all model changes

### Pillar 2: Transparency

**Internal transparency** (within the organization):
- Document all deployed HR AI systems in a central AI inventory
- HR leaders and legal counsel must understand what AI systems are in use and for what decisions
- Line managers who act on AI outputs must understand what the output means and what it does not mean
- HR operations staff must understand limitations: confidence intervals, error rates, conditions under which the model degrades

**External transparency** (to employees and candidates):
- Disclose to candidates that AI is used in screening (required by GDPR; emerging US practice)
- Disclose to employees that AI is used in performance evaluation or attrition risk assessment
- Do not represent AI outputs as objective facts — they are probabilistic estimates with documented error rates
- Provide explanations: candidates/employees can request the factors that contributed to an AI decision

**Regulatory transparency**:
- NYC Local Law 144: publish results of annual independent bias audit for AI hiring tools
- GDPR Article 22: provide meaningful explanation of logic for automated decisions affecting EU employees/candidates
- Illinois AI Video Interview Act: written disclosure + consent before video AI; destruction of recordings on request

### Pillar 3: Audits

**Bias audit (pre-deployment)**:
- Test model performance across all protected groups (race, gender, age, disability, national origin)
- Measure: accuracy by group, false positive rate by group, false negative rate by group, disparate impact ratio
- Fail criteria: disparate impact ratio < 0.80 for any protected group (EEOC 4/5ths rule)
- Document: which fairness metric was chosen and why; residual risk accepted

**Ongoing audits (post-deployment)**:
- Frequency: monthly for Tier 2 high-volume tools; quarterly for Tier 3
- Monitor for model drift (accuracy degrading as population shifts)
- Monitor for bias emergence (disparate impact ratios trending down over time)
- Compare model recommendations vs. actual human decisions — persistent disagreement indicates either model error or human bias

**Independent audits**:
- For tools covered by NYC Local Law 144: annual independent third-party audit
- For GDPR-covered systems: Data Protection Impact Assessment (DPIA) required for high-risk processing
- For EEOC-regulated employers: periodic validation study per Uniform Guidelines on Employee Selection Procedures

---

## 4. Bias Sources and Prevention

### Source 1: Training Data Bias

Historical HR decisions encode historical discrimination. A model trained on 10 years of performance ratings inherits rater biases, promotion disparities, and demographic skew in the historical workforce.

**Prevention**:
- Audit historical labels (ratings, promotion decisions, hire/no-hire) for demographic disparities before training
- Consider time-windowing: train on recent data only to reduce legacy bias
- Use algorithmic debiasing on labels where disparities are documented
- Consider synthetic data augmentation for underrepresented groups

### Source 2: Data Adequacy Bias

Underrepresented groups generate less training data → model accuracy is lower for those groups → errors concentrate on groups already disadvantaged.

**Prevention**:
- Set minimum representation thresholds before training
- Report performance metrics disaggregated by demographic group
- Use stratified sampling to ensure training set representation
- Flag predictions for individuals from underrepresented groups for mandatory human review

### Source 3: Proxy Variable Bias

Features correlated with protected attributes produce discriminatory outcomes even when the protected attribute is excluded.

**Common HR proxies**:
- Name → gender, ethnicity
- Employment gaps → pregnancy, disability, caretaking
- Years since graduation → age
- Zip code / neighborhood → race
- School prestige → socioeconomic status
- Keywords ("women's chess club") → gender

**Prevention**:
- Run correlation analysis between all features and protected attributes
- Remove high-correlation features or apply causal scrubbing
- Test residual proxy effects post-removal

### Source 4: Advertising/Reach Bias

Optimization algorithms for job advertising route ads based on engagement signals that correlate with demographic characteristics. No explicit instruction needed — the optimization naturally learns who responds and narrows the pool.

**Example**: STEM job ads shown less to women because historical STEM applicant engagement data is male-skewed → self-reinforcing cycle.

**Prevention**:
- Set demographic reach constraints in job advertising platforms
- Monitor ad audience composition; require demographic balance in ad delivery
- Audit application pipeline: compare ad impressions by demographic vs. applications received

---

## 5. Fairness Definitions and Trade-Offs

### The Incompatibility Problem

The Northpoint/ProPublica COMPAS analysis demonstrated that multiple fairness definitions are **mathematically incompatible** when group base rates differ:

| Definition | What It Means | Who Benefits |
|------------|--------------|-------------|
| Calibration | Risk scores accurately predict outcomes within each group | System users (predictive validity) |
| Equal false positive rate | Error of over-flagging is equal across groups | People over-predicted as risky |
| Equal false negative rate | Error of under-flagging is equal across groups | People under-predicted as risky |
| Demographic parity | Equal selection rate across groups | Groups with lower natural selection rates |

These definitions cannot simultaneously be satisfied (Chouldechova incompatibility theorem, 2017) except when base rates are equal across groups. Choosing one is a value judgment, not a technical choice.

### Blackstone's Ratio Framing

"Better that ten guilty persons escape than one innocent suffer." — Blackstone's Commentaries

Applied to HR AI: better to miss ten flight risk predictions than falsely flag one loyal employee and damage the employment relationship through unnecessary intervention. Or vice versa. This is a moral choice the organization must make explicitly — not delegate to the algorithm.

### Recommended Defaults for HR AI

| HR Application | Recommended Fairness Metric | Rationale |
|---------------|---------------------------|-----------|
| Hiring screening | Equal opportunity (equal TPR) | Missing qualified candidates from disadvantaged groups is primary harm |
| Attrition prediction | Calibration + FPR parity | Both missing flight risks and false alarms have similar costs |
| Performance rating | Demographic parity | Equal distribution of high ratings across groups |
| Promotion prediction | Equal opportunity (equal TPR) | Equal chance of identifying promotable candidates across groups |

---

## 6. Data Protection Law

### GDPR (EU)

Applies to any EU employee or candidate data regardless of where the employer is headquartered.

Key provisions:
- **Article 5**: Data minimization, purpose limitation, accuracy, storage limitation
- **Article 13/14**: Transparency — inform individuals about AI-based processing before collection
- **Article 22**: Right not to be subject to solely automated decisions with significant effects; right to human review; right to explanation
- **Article 25**: Privacy by design and by default — build data protection into system design
- **Article 35**: Data Protection Impact Assessment (DPIA) required for systematic employee monitoring

**"Right to be forgotten" (Article 17)**: Employees can request deletion of their personal data. Systems must be architected to make deletion technically feasible — not all legacy HR systems support this.

### US Federal Law

No federal equivalent to GDPR, but sector-specific obligations:
- **EEOC Uniform Guidelines**: AI hiring tools are "selection procedures" subject to adverse impact analysis
- **Title VII, ADEA, ADA**: Discriminatory outcomes from AI are actionable regardless of discriminatory intent
- **FCRA**: If third-party AI provides candidate assessments used for hiring, may trigger FCRA consumer report obligations

### State Law

| Law | Jurisdiction | Key Requirement |
|-----|-------------|----------------|
| CCPA/CPRA | California | Right to know, delete, opt-out; employee data partially covered from 2023 |
| Illinois BIPA | Illinois | Biometric data (fingerprints, facial geometry) requires written consent |
| Illinois AI Video Interview Act | Illinois | Disclosure + consent for AI video analysis; cannot be sole factor; data deletion |
| NYC Local Law 144 | New York City | Annual bias audit for automated employment decision tools; public posting |
| Maryland HB 1202 | Maryland | Facial recognition consent requirements |

### Privacy Risk Matrix for HR Data

| Data Type | Privacy Risk | Special Protection Needed |
|-----------|-------------|--------------------------|
| Video interview recordings | Very High | Illinois AIVIA, consent, time-limited retention |
| Biometric data (voice, face) | Very High | BIPA (IL), GDPR Article 9 special category |
| Health / disability data | Very High | ADA, GDPR Article 9 |
| Email and communication content | High | GDPR legitimate interest test; monitoring disclosure |
| Performance ratings | Medium | GDPR subject access rights |
| Job application data | Medium | FCRA if third-party compiled; EEOC adverse impact |
| LinkedIn public profile | Low | Scraping may violate platform ToS |

---

## 7. Explainability Law and Practice

### Legal Requirements

**GDPR Article 22 / Recital 71**: Right to "meaningful information about the logic involved" in automated decisions. "Black box" is not a legally acceptable response.

**NYC Local Law 144**: Requires employers using automated employment decision tools (AEDT) to:
1. Conduct and publish annual bias audit by an independent auditor
2. Notify candidates/employees that an AEDT is being used

**Illinois AI Video Interview Act**: Requires employers to:
1. Notify applicants before using AI in video interview analysis
2. Explain how AI works in general terms
3. Obtain consent
4. Limit sharing of videos
5. Delete recordings within 30 days of request

### Explainability in Practice

When an employee asks "Why was I passed over for promotion?" the answer "Our AI model scored you at the 42nd percentile" is not meaningful. A meaningful explanation:
- Names the primary factors that contributed to the score (SHAP values translated to plain language)
- Distinguishes model output from the human decision
- Describes what the employee could change to improve the score (actionability)

**Implementation**: Build explanation templates into HR AI UI. For every consequential decision, generate: "Your score reflected [top 3 factors]. To improve your standing, consider [actionable recommendations]."

---

## 8. AI Governance Structure

### AI Ethics Council

Recommended composition for organizations with >500 employees using HR AI:
- CHRO or senior HR representative
- Chief Legal Officer or employment law counsel
- Chief People Analytics officer
- Employee representative / works council member (where applicable)
- External ethics advisor (annual rotation)

Responsibilities:
- Approve deployment of new HR AI tools
- Review bias audit results and respond to failures
- Set organization-wide fairness metric standards
- Review and respond to employee appeals
- Publish annual HR AI transparency report

### Vendor Evaluation Framework

Third-party HR AI vendors must provide:
1. **Validation study**: Independent evidence of predictive validity for stated use case
2. **Bias audit**: Evidence of disparate impact testing across protected groups
3. **Explainability**: Ability to generate individual-level explanations for decisions
4. **Data terms**: Clear data processing agreement; confirmation of data deletion on contract termination
5. **Regulatory compliance**: NYC LL144 compliance; GDPR data processing agreement for EU use
6. **Incident response**: Process for notifying customer of identified bias, data breach, or model failure

### Escalation Path

```
Individual employee appeal
         ↓
HRBP review within 5 business days
         ↓
HR AI governance team review within 15 business days
         ↓
AI Ethics Council decision within 30 business days
         ↓
External independent review (if employee requests)
```

---

## 9. Blockchain and Emerging Technologies

### Blockchain for HR Credentials

Blockchain provides a decentralized, immutable ledger with no central authority needed for trust verification. Relevant HR applications:

**On-tap credentialing**: Employees maintain verifiable, employer-independent records of qualifications, certifications, and employment history. MIT Digital Diplomas; Consensys skills passport. Eliminates credential fraud; reduces time-to-verify.

**Cross-border payroll**: Smart contracts automate multi-currency payroll execution across jurisdictions without banking intermediaries. Significant cost reduction for organizations with distributed international workforces.

**GDPR-compliant data storage**: Immutable audit trail of data access and consent. Paradox: blockchain immutability conflicts with GDPR "right to be forgotten" — reconciled through off-chain storage of personal data with on-chain hash pointers.

**Fine-grained productivity data**: Objective, tamper-proof record of individual contributions (code commits, design iterations, document edits) without reliance on manager judgment.

### Limitations

- Immutability is both the feature and the problem: errors cannot be corrected
- Scalability: transaction throughput limitations for high-volume HR operations
- Adoption network effects: credential verification only works if both issuer and verifier are on-chain
- Energy cost: proof-of-work chains have significant environmental footprint (proof-of-stake addresses this)

---

## 10. AI's Effect on HR Jobs and Roles

### The Skeptical View on Job Elimination

Historical concern: AI/robots will eliminate HR jobs. Historical reality: most technology adoption predictions about job elimination have been wrong.

Pattern from prior technology waves:
- **Numerically controlled machines (1970s)**: Predicted to eliminate machinists. Actual outcome: machinists took on programming roles; total employment in sector stable.
- **Bank ATMs (1980s)**: Predicted to eliminate bank tellers. Actual outcome: lower branch cost → more branches opened → more tellers employed.
- **Driverless trucks**: Still not deployed at scale as of 2024 despite decade of predictions. Market failure: insurance, liability, infrastructure, regulation.

### Management Decisions Determine Outcomes

The key variable is not technology capability but **management choice about work redesign**:
- GM installed robots in 1980s → laid off workers, replaced with robots
- Toyota installed same-generation robots → retrained workers, assigned them to robot oversight and quality

Same technology, different choices, different employment outcomes. The technology did not determine the outcome; the management decision about work organization did.

### What Changes in HR Roles

AI does not eliminate HR roles but **shifts skill requirements**:

| Role Shift | Before AI | After AI |
|------------|-----------|---------|
| HR Business Partner | Benefits admin, policy enforcement | Strategic advisor, AI output interpreter |
| Recruiter | Resume screening, phone screens | Candidate experience, AI audit, final selection |
| L&D Specialist | Content delivery | Learning path design, skills gap analysis |
| Compensation Analyst | Market data lookup, salary bands | Equity analysis, AI model oversight |
| HR Analyst | Report generation | Model development, bias testing, interpretation |

**Upskilling required**: HR professionals need literacy in ML basics, data quality assessment, bias identification, and regulatory compliance for AI systems. Not PhD-level data science — but enough to be intelligent consumers and governors of AI tools.

---

## Companion skills + artifacts

| Pair with | Why |
|---|---|
| `/threat-model` skill | Apply §2 Risk Taxonomy to a specific HR system (hiring, performance, attrition) |
| `/red-team` skill | Operationalize §4 Bias Sources + §5 Fairness Defaults |
| `/eval-design` skill | Build the §3 Pillar 3 audit metrics (TPR/FPR/calibration parity by group) |
| `/model-card` skill | Document the chosen HR model for downstream consumers |
| `bias-audit-hr.html` (templates/governance/) | Pre-deployment audit template — implements §3 Pillar 3 with EEOC 4/5ths calc |
| `bias-audit-general.html` (templates/governance/) | Generalized companion to the HR-specific template |
| `governance-playbook-general.html` (templates/governance/) | Risk-tier playbook covering all four tiers in §2 |
| `genai-risk-checklist.html` (templates/governance/) | GenAI-specific risk lens (résumé generation, candidate communication, interview transcript summarization) |
| `ai-governance-framework.md` (reference/) | General governance frame — start there, then apply this HR-specific overlay |

---

## Key References (public sources)

- EEOC: *Uniform Guidelines on Employee Selection Procedures* (29 CFR Part 1607)
- EEOC: *Assessing Adverse Impact in Software, Algorithms, and Artificial Intelligence Used in Employment Selection Procedures Under Title VII of the Civil Rights Act of 1964* (technical assistance document, 2023)
- EU: *General Data Protection Regulation* (GDPR, Regulation 2016/679) — Articles 5, 13, 14, 17, 22, 25, 35; Recital 71
- New York City: *Local Law 144 of 2021* (Automated Employment Decision Tools) + Department of Consumer and Worker Protection rules
- Illinois: *Artificial Intelligence Video Interview Act* (820 ILCS 42)
- Illinois: *Biometric Information Privacy Act* (740 ILCS 14)
- California: *Consumer Privacy Act* (CCPA) / *Privacy Rights Act* (CPRA)
- Chouldechova, A.: *Fair Prediction with Disparate Impact: A Study of Bias in Recidivism Prediction Instruments*, Big Data 5(2) (2017) — incompatibility theorem
- Angwin, J., Larson, J., Mattu, S., Kirchner, L.: *Machine Bias* (ProPublica, 2016) — COMPAS analysis
- Lundberg, S. M., Lee, S.-I.: *A Unified Approach to Interpreting Model Predictions* (SHAP), NeurIPS (2017)
- Bessen, J.: *Learning by Doing: The Real Connection between Innovation, Wages, and Wealth* (Yale, 2015) — ATM/teller employment data
- Autor, D. H.: *Why Are There Still So Many Jobs? The History and Future of Workplace Automation*, Journal of Economic Perspectives 29(3) (2015)
