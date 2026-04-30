# Feature Engineering Cookbook

Patterns for turning raw data into model-ready features. Architect-grade reference for tabular, text, and unstructured-data pipelines.

> **Anchor doctrine.** *"More data usually beats a better algorithm — and better features usually beat both."* See Halevy, Norvig, Pereira (2009), *The Unreasonable Effectiveness of Data*, IEEE Intelligent Systems 24(2). Corollary for unstructured data: stop hand-engineering and let the network learn the features.

---

## 1. What feature engineering is (and isn't)

| Is | Isn't |
|---|---|
| Designing the *inputs* the model sees | Designing the model |
| Encoding domain knowledge into columns | Replacing the need for data |
| The single highest-ROI activity in classical ML | A one-time step |
| Where business + data science actually collaborate | Just "data cleaning" |

**Mental model.** A model can only learn patterns *that exist in its features*. If a critical signal isn't in the input, no algorithm will find it.

**Tabular vs. unstructured.** A logistic regression with great features beats a neural net with raw inputs *most of the time on tabular data*. Save the deep learning budget for unstructured data where features must be learned.

---

## 2. The feature taxonomy

### 2.1 Direct features
Already in the source columns: age, price, country, device. Often the weakest signals on their own.

### 2.2 Aggregated features
Summary statistics over a window.

| Pattern | Example | When |
|---|---|---|
| Count | # logins last 30 days | Engagement, fatigue |
| Sum | $ spend in past 90 days | Revenue propensity |
| Mean / median | Avg session length | Habit formation |
| Min / max | Largest single transaction | Anomaly priors |
| Std dev | Variability of order size | Pattern stability |
| Recency | Days since last purchase | Most-predictive single feature in churn / lifetime models |

### 2.3 Ratio features
Capture relationships that linear models cannot infer from raw inputs.

| Ratio | Why |
|---|---|
| Debt / income | Linear models can't multiply two columns |
| Page-views / session | Engagement intensity |
| Returns / orders | Customer quality signal |
| Items in cart / items bought | Indecision proxy |
| Spend on category A / total spend | Preference share |

### 2.4 Time features
Time is rarely directly useful; *transformations of time* are.

| Pattern | Example |
|---|---|
| Day-of-week, hour-of-day | Seasonality in retail, support volume |
| Is-weekend, is-holiday | Behavioral shift signal |
| Days since X | Recency (almost always predictive) |
| Cyclical encoding (sin/cos of hour) | Models that need smooth time wrap |
| Time since onboarding | Lifecycle stage |

### 2.5 Interaction features
Combinations of two raw features that matter only together.

| Interaction | Why |
|---|---|
| Premium-tier × weekend visit | Different segment behaves differently |
| Region × product category | Local demand patterns |
| Age-bucket × channel | Segment-specific conversion |

Tree models (random forest, GBM) can discover some interactions automatically. Linear models (logistic regression) cannot — you must engineer them in.

### 2.6 Bucketed / binned features
Convert a continuous variable into ordered groups.

| When useful |
|---|
| Linear model + non-linear relationship (e.g., risk doesn't increase linearly with age) |
| Tree model that overfits to single split points |
| Interpretability requirement (regulators want "high / medium / low") |

**Caution.** Bucketing throws away information. Use only when you have a reason.

### 2.7 Categorical encodings
Categorical columns need numeric form.

| Encoding | Pros | Cons | When |
|---|---|---|---|
| **One-hot** (red → [1,0,0]) | Simple, no order assumed | Explodes dimensionality on high-cardinality cols | < 50 categories, linear models |
| **Ordinal** (small=1, med=2, large=3) | Preserves order | Implies equal spacing | Naturally ordered categories only |
| **Target encoding** (replace category with mean target) | Compact, captures signal | Leakage risk; needs hold-out | High-cardinality (zip codes, user IDs) |
| **Hashing** (hash to N buckets) | Constant memory | Collisions | Online / streaming systems |
| **Embeddings** (learned dense vector) | Captures semantic similarity | Needs lots of data + a deep model | NLP, recommender systems |

### 2.8 Text features
Bridges to NLP.

| Method | Output | Use |
|---|---|---|
| **Bag-of-words** | Sparse word-count vector | Baseline classification |
| **TF-IDF** | Word importance weighted by document rarity | Strong baseline; logreg companion |
| **N-grams** | Captures short phrases ("not good") | When word order partly matters |
| **Character n-grams** | Robust to typos | User-generated text, multilingual |
| **Embeddings** (word2vec, sentence-transformers) | Dense semantic vectors | Similarity, clustering, downstream classifiers |
| **LLM embeddings** (OpenAI, Voyage, Cohere, etc.) | Dense vectors with world knowledge baked in | RAG retrieval, modern semantic search |

### 2.9 Image / audio features
Classical: hand-engineered (HOG, SIFT, MFCC). Modern default: **let a pretrained CNN or transformer learn the features.** This is the bridge from feature engineering to representation learning — you stop hand-engineering and let the network do it.

---

## 3. When to stop engineering and start learning

| Data type | Default approach | When to switch to learned features |
|---|---|---|
| **Tabular** | Hand-engineer (this cookbook) | Almost never — gradient-boosted trees on engineered features wins |
| **Short text** (tweets, reviews) | TF-IDF + logistic regression | When >50k labeled examples → fine-tuned BERT |
| **Long text** (contracts, articles) | Embeddings + classifier head OR LLM | Almost always learned |
| **Images** | Pretrained CNN embedding + classifier | Almost always learned |
| **Audio** | Pretrained transformer (Whisper-style) embedding | Almost always learned |
| **Time-series** | Hand-engineered (lags, rolling stats, seasonality) | Only at very large scale + complex temporal patterns |

**The economics test.** Hand-engineering takes 1–4 weeks per major feature. Pretrained-model fine-tuning takes 1–3 days. **Use learned features when (a) data is unstructured, AND (b) you have enough volume to fine-tune or you can use pretrained off-the-shelf.**

---

## 4. The 12 highest-ROI feature patterns (memorize these)

| # | Pattern | Why it's a workhorse |
|---|---|---|
| 1 | Recency (days-since-X) | Most-predictive single feature in churn, lifetime value, fraud |
| 2 | Frequency (count over window) | Companion to recency — RFM in retail is built on these two |
| 3 | Monetary aggregate ($ over window) | Completes RFM |
| 4 | Ratio of "engagement" to "ceiling" (e.g., used-features / available-features) | Saturation signal |
| 5 | Z-score vs. peer group | Anomaly detection without training a model |
| 6 | Lag features (value at t-1, t-7, t-30) | Time-series default |
| 7 | Rolling mean / std (last 7 days vs. last 90 days) | Trend + volatility in one |
| 8 | Day-of-week + hour-of-day | Catches almost all behavioral seasonality |
| 9 | Interaction of segment × action | Lets linear models see what trees find naturally |
| 10 | Target encoding for high-cardinality categoricals (with hold-out) | Compact + signal-rich |
| 11 | TF-IDF on free-text fields | Text → numeric for cheap |
| 12 | Pretrained embedding of long text / image | Bypasses the engineering step entirely |

---

## 5. Anti-patterns

| Pattern | Why it fails | Fix |
|---|---|---|
| **Leaky features** (e.g., "policy_cancellation_date" used to predict cancellation) | Future information bleeds into training; production accuracy collapses | Audit each feature for "could this only be known after the event we're predicting?" |
| **Snapshot features computed at different times for train vs production** | Training sees clean weekly batch, production sees real-time messy | Recompute features at *prediction time* in both train and prod |
| **Categorical with 50,000 levels one-hot encoded** | Memory blow-up; sparse model | Target encoding, hashing, or embeddings |
| **Engineering on the test set** | Optimistic accuracy that disappears in prod | All transformations fit on train only |
| **Aggregating without a window** | "Total purchases" silently grows over time → drift | Always specify the window (last 30/90/365 days) |
| **Mixing scales** (some features 0–1, others 0–1M) | Distance- and gradient-based models break | Standardize / normalize for those model families |
| **Forgetting to handle nulls explicitly** | Some libraries crash, others silently impute median | Decide per feature: imputed mean, "missing" indicator, or drop |

---

## 6. The feature engineering workflow

```
1. Define the prediction target precisely
   (what + as-of-when + at what granularity)
        ↓
2. List candidate signals from the business
   (interview ops + frontline; document hypotheses)
        ↓
3. Engineer baseline features (direct + a few aggregates)
        ↓
4. Train a baseline model; measure
        ↓
5. Add interactions, ratios, time features one batch at a time
        ↓
6. Re-measure; keep features that improve held-out metric
        ↓
7. Audit for leakage and production-feasibility
        ↓
8. Document each feature: definition, source, refresh cadence,
   owner, last validated
```

**Discipline.** Step 8 is the difference between a research notebook and a production system. Without a feature catalog, your model breaks silently when an upstream column changes definition.

---

## 7. Production concerns

### Feature stores
Centralized service that computes features once and serves them to both training and inference. Solves the "training/serving skew" problem. **Only worth it once you have ≥3 models sharing features.**

### Refresh cadence
Each feature has a refresh cost + staleness tolerance. Document both:

| Cadence | Examples |
|---|---|
| Real-time | Account balance, current cart |
| Hourly | Active session count |
| Daily | RFM aggregates, day-of-week |
| Weekly | Customer-lifetime stats |
| Monthly | Long-cycle behavioral patterns |

### Drift monitoring
For each feature, track:
- Mean shift (>2σ change → alert)
- Distribution shape (PSI > 0.2 → alert)
- Null rate change (pipeline health)

Drift on inputs precedes drift on outputs. Catch it upstream.

---

## 8. Domain feature library (starting points)

### Customer / consumer
Recency-of-last-action; Frequency in window; Lifetime value; Channel mix; Device diversity; Tenure; Engagement saturation; Net Promoter proxy; Refund rate.

### Risk / fraud / lending
Velocity (transactions per minute / hour); Geographic diversity; Device fingerprint reuse; Time-since-account-creation × first-large-transaction (interaction); Amount vs. account-history percentile; Counterparty network features.

### Healthcare
Days since last visit; Comorbidity counts; Medication adherence ratio; Lab-value trends (slopes); Specialty referral patterns.

### Marketing / growth
Last-touch channel; Multi-touch attribution weights; Cohort × channel interactions; Time-of-day conversion patterns; Email open recency × click recency.

### Supply chain / operations
Lead-time variability; SKU velocity; Stock-out frequency; Supplier-on-time rate; Seasonality decomposition.

### Text-heavy domains (legal, insurance, support)
Document length; Section presence flags; Named entity counts; TF-IDF top-K terms; Embedding similarity to known categories.

---

## 9. The collaboration playbook (where data + business actually meet)

Feature engineering is the most under-staffed collaboration in enterprise ML. Run it as a workshop, not a Jira ticket.

| Step | Who | Output |
|---|---|---|
| 1. Hypothesis generation | Business + ops | "I think X drives churn because…" — 20 hypotheses |
| 2. Data feasibility | Data eng | "We have / don't have / could derive each" |
| 3. Feature spec | Data scientist + business | One-pager per feature: definition, formula, window, refresh |
| 4. Build + test | Data engineer | Feature in store with backfilled history |
| 5. Validate | Data scientist | Does it improve held-out metric? |
| 6. Document | All | Feature catalog entry; sign-off on owner |

**Time investment.** Steps 1–3 should take 1–2 days for a new model, not weeks. Most teams skip them and pay 10x in step 5 rework.

---

## 10. What to build vs. buy

| Task | Build | Buy |
|---|---|---|
| Domain-specific features (your customer behavior) | ✅ Always build | ❌ |
| Generic NLP features (sentiment, topics, NER) | ❌ | ✅ Pretrained models or APIs |
| Image embeddings | ❌ | ✅ Pretrained vision models (CLIP, etc.) |
| Time-series decomposition | Maybe build | Buy if you have <3 forecasting use cases |
| Geo / weather / demographic enrichment | ❌ | ✅ Third-party data providers |
| Feature store infrastructure | ❌ unless ≥10 models | ✅ Tecton, Feast, Vertex |

---

## Companion skills + artifacts

| Pair with | Why |
|---|---|
| `/dataset-readiness` skill | Score the data substrate before you engineer features |
| `/eval-design` skill | Measure whether each feature actually improves held-out metric |
| `prompt-engineering-cookbook.md` | When the "feature" is a prompt template (LLM era) |

---

## Further reading (public sources)

- Halevy, Norvig, Pereira (2009), *The Unreasonable Effectiveness of Data*, IEEE Intelligent Systems 24(2)
- Hosanagar (2019), *A Human's Guide to Machine Intelligence*, Viking — chapters on data substrate and ML decision-making
- Domingos (2012), *A Few Useful Things to Know About Machine Learning*, CACM 55(10) — feature engineering as the highest-leverage activity
