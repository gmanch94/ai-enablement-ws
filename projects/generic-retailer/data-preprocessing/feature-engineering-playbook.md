# Retail ML Feature Engineering Playbook

**Status:** Template / Reference
**Owner:** AI Platform Team / ML Engineers
**Last updated:** [DATE]
**Policy reference:** ADR-0045 — Retail ML Data Preprocessing Policy

> **Purpose:** Define the canonical feature engineering strategy per retail ML use case archetype. These are not suggestions — they are the validated patterns that prevent the most common retail ML failures (temporal leakage, cold-start crashes, silent semantic drift). Teams building new models must justify deviation from this playbook.

---

## Global Rules (apply to all use cases)

These rules are non-negotiable. Deviating from them without explicit approval from the AI Platform Lead is a policy violation.

### 1. Temporal Split is Mandatory

**Random train/test splits are prohibited for all retail time-series targets.**

Demand, markdown, churn, and CLV are time-dependent. A random split leaks future information into training — a model trained this way achieves inflated offline metrics and degrades in production.

Required approach:
- **Training window:** [T_start] to [T_cutoff - validation_gap]
- **Validation gap:** ≥ [X] days between last training record and first validation record (prevents data leakage from rolling features)
- **Validation window:** [T_cutoff - validation_gap + 1] to [T_cutoff]
- **Test window:** [T_cutoff + 1] to [T_end] — held out entirely until final evaluation before production

The cutoff date must be chosen such that validation and test windows both contain at least one seasonal cycle of the target phenomenon (e.g., for weekly seasonal demand, at least 4 weeks).

See ADR-0045 §Temporal Splitting Policy for the required cutoff calculation.

### 2. Cold-Start Strategy is Mandatory

Every feature pipeline must have an explicit strategy for new entities — new SKUs, new stores, new customers. Dropping new entities is not a strategy; it is a design debt that surfaces as production failures.

| Entity | Cold-Start Strategy | Notes |
|--------|-------------------|-------|
| New SKU | Use category-level aggregations; embed product description; fall back to category median | Cannot rely on transaction history that doesn't exist yet |
| New Store | Use store format + region averages; cluster by demographic similarity to existing stores | A new store has no sales history but has location attributes |
| New Customer | Use session behavioral features; no RFM — fall back to demographic segment averages | RFM requires history; day-1 customers have none |

### 3. Hierarchical Rollups are Required

Retail data is hierarchical. Every feature pipeline must be able to aggregate at multiple levels when entity-level history is sparse.

| Hierarchy | Levels (coarse → fine) |
|-----------|----------------------|
| Product | Department → Category → Subcategory → SKU |
| Location | Region → Market → District → Store → Aisle |
| Time | Year → Quarter → Month → Week → Day → Hour |
| Customer | Segment → Household → Individual |

Rule: when entity-level feature is sparse (< [X] observations), fall back to the next coarser level. Document the sparsity threshold in the feature pipeline.

### 4. Feature Naming Convention

All features follow this naming convention to ensure traceability:

```
{source_dataset}_{entity}_{feature_name}_{aggregation}_{window}
```

Examples:
- `pos_item_units_sold_sum_7d` — sum of units sold at item level, 7-day window, from POS data
- `loyalty_customer_visit_count_28d` — visit count at customer level, 28 days
- `catalog_item_category_id` — item's category from catalog (no window — point-in-time attribute)
- `mlpartner_item_demand_forecast_7d_ahead` — ML partner's 7-day forward demand forecast

### 5. Feature Leakage Audit

Before any model goes to staging, run a leakage audit:
- No feature has a temporal dependency on the label or any post-event data
- Rolling features use only data available at the time of prediction, not at the time of training
- [ML_PARTNER] forecasts used as features must be the forecast *as issued at prediction time*, not retroactively corrected values

---

## Use Case 1: Demand Forecasting / Replenishment (P1-B)

**Target variable:** Forecasted units sold per SKU per store per day over a [N]-day horizon
**Grain:** One row = one (SKU, store, forecast date) triplet
**Minimum training history:** 52 weeks (to capture full seasonal cycle)
**Temporal split gap:** 7 days (accounts for weekly seasonality)

### Required Features

#### Temporal Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `pos_item_store_units_sold_7d` | Sum units sold, rolling 7-day window | Core demand signal |
| `pos_item_store_units_sold_28d` | Sum units sold, rolling 28-day window | Smoothed signal |
| `pos_item_store_units_sold_364d` | Same, 364-day (52-week) window | Seasonal baseline |
| `pos_item_store_lag_1` | Units sold, t-1 day | Autoregressive feature |
| `pos_item_store_lag_7` | Units sold, t-7 days | Same day last week |
| `pos_item_store_lag_28` | Units sold, t-28 days | Same day last month |
| `pos_item_store_trend_28d` | Linear slope of units sold over 28 days | Momentum signal |
| `pos_item_store_ewma_alpha_02` | Exponentially-weighted moving avg (α=0.2) | Noise-robust signal |

#### Calendar / Seasonality Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `time_day_of_week` | Integer 0–6 | Encode as cyclical (sin/cos) for neural models |
| `time_week_of_year` | Integer 1–52 | Encode as cyclical |
| `time_is_holiday` | Binary; source from external holiday calendar | National + regional holidays |
| `time_days_to_next_holiday` | Integer | Demand increases before holidays |
| `time_days_since_last_holiday` | Integer | Post-holiday demand drop |
| `time_is_back_to_school` | Binary; [Aug 15 – Sep 15] | Category-specific seasonality |
| `time_is_super_bowl_week` | Binary | Snacks, beverages spike |
| `time_month_end_week` | Binary; last 7 days of month | Pay-cycle effects on spending |

#### Product Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `catalog_item_category_id` | From product catalog | Encoded; used for hierarchy fallback |
| `catalog_item_department_id` | From product catalog | |
| `catalog_item_is_private_label` | Binary | Private label has different demand pattern |
| `catalog_item_shelf_life_days` | From product catalog | Critical for perishables |
| `catalog_item_unit_of_measure` | Unit vs. weight-based | Different demand semantics |
| `pos_item_price_current` | Current shelf price from pricing system | |
| `pos_item_price_regular_ratio` | Current price / regular price | <1 = on promotion |
| `pos_item_is_on_promotion` | Binary; derived from price ratio | |
| `pos_item_substitute_count` | # of direct substitutes in same category | Competitive cannibalization |

#### Store Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `store_format` | From store master | Large format vs. small format vs. express |
| `store_region` | From store master | Regional demand patterns |
| `store_avg_weekly_units_store_level_52w` | Store-level total units, 52-week avg | Store traffic proxy |
| `store_category_avg_units_52w` | Category-level units at store, 52-week avg | Category-specific traffic |

#### [ML_PARTNER] Enrichment Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `mlpartner_item_store_demand_forecast_7d` | [ML_PARTNER] 7-day forward forecast at item × store | Use as feature, not label |
| `mlpartner_item_store_demand_forecast_28d` | [ML_PARTNER] 28-day forward forecast | |
| `mlpartner_signal_age_hours` | Hours since [ML_PARTNER] signal was issued | Staleness indicator |
| `mlpartner_signal_available` | Binary; 1 if [ML_PARTNER] data present | For fallback handling |

#### External Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `ext_weather_temp_avg_3d` | Average temperature, 3-day forecast | Affects produce, beverages, ice cream |
| `ext_weather_precip_prob_3d` | Probability of precipitation | Affects store footfall |
| `ext_economic_consumer_confidence` | Monthly index | Spend tier shifts |

### Target Engineering
- **Label:** `pos_item_store_units_sold_Nd_forward` — sum of actual units sold over the forecast horizon
- **Label lag:** Ensure label is computed from data *after* the feature cutoff date — no leakage
- **Outlier treatment:** Cap labels at P99 per item × store group; log-transform before regression targets

### Validation Strategy
- Offline: RMSE, MAPE, WAPE per store × category × horizon
- Seasonal holdout: include at least one major seasonal event (Black Friday, Super Bowl) in test set
- Baseline: beat naïve model (last-year same week) on WAPE by ≥ [X]%

---

## Use Case 2: Fresh Markdown Optimization (P3-A)

**Target variable:** Whether a markdown recommendation at price P and time T results in sell-through (binary) — or optionally, the optimal markdown % (regression)
**Grain:** One row = one (SKU, store, markdown decision time) event
**Minimum training history:** 26 weeks of markdown + outcome data per category
**Temporal split gap:** 3 days (shorter horizon than demand forecasting)

### Required Features

#### Time-to-Expiry Features (most predictive for fresh markdown)
| Feature | Calculation | Notes |
|---------|------------|-------|
| `wms_item_days_to_bestby` | Best-by date - decision date | THE most predictive feature |
| `wms_item_hours_to_store_close` | Hours until end of business day | Intraday urgency |
| `wms_item_is_last_day_sellable` | Binary; days_to_bestby ≤ 1 | Immediate action required |
| `wms_item_time_on_shelf_days` | Days since item received | Freshness proxy |

#### Inventory Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `wms_item_store_units_on_hand` | Current inventory count | |
| `wms_item_store_units_sold_last_3h` | Velocity: units sold last 3 hours | Intraday demand signal |
| `wms_item_store_units_sold_prev_day` | Prior day sales | |
| `wms_item_store_projected_sellthrough_rate` | Units on hand / avg daily velocity | If > days_to_bestby → markdown needed |
| `wms_item_store_waste_rate_28d` | % of received units historically disposed | Category-level disposal risk |

#### Markdown History Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `markdown_item_store_prev_markdown_pct` | Last markdown depth for this item at this store | |
| `markdown_item_category_elasticity_90d` | Price elasticity: % demand change per 1% price change | Category-level, 90-day rolling |
| `markdown_item_store_acceptance_rate_90d` | % of prior markdowns that achieved sell-through | Trust signal for recommendation engine |
| `markdown_item_markdown_floor_pct` | Minimum markdown allowed (from ERP config) | Hard constraint |

#### Demand Signal Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `mlpartner_item_store_demand_forecast_24h` | [ML_PARTNER] 24-hour demand forecast | Signals whether natural sell-through is likely |
| `pos_item_store_weekend_uplift_ratio` | Weekend vs weekday average velocity | If approaching weekend → different urgency |

### Label Engineering
- **Sell-through label:** 1 if units_remaining_at_bestby = 0 (sold out before expiry), 0 otherwise
- **Optimal markdown label (regression variant):** Markdown % that maximized revenue, derived from historical markdown × sell-through outcomes
- [RISK: HIGH] This label has a selection bias: we only observe outcomes of markdowns that were *actually applied*. Models trained on this data will not generalize to items that never received a markdown. Document this counterfactual gap in the model card.

---

## Use Case 3: Customer Segmentation / CLV (P2-A, P2-B)

**Target variable (segmentation):** Cluster assignment; (CLV) predicted 12-month spend
**Grain:** One row = one household (loyalty member)
**Minimum training history:** 12 months for RFM; 24+ months for CLV
**Cold-start:** New members have no RFM — use enrollment cohort and initial session features

### RFM Features (required baseline)
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_customer_recency_days` | Days since last purchase | Decaying engagement signal |
| `loyalty_customer_frequency_12m` | Number of distinct visit days in last 12 months | Visit cadence |
| `loyalty_customer_monetary_12m` | Total spend in last 12 months | Value signal |
| `loyalty_customer_aov_12m` | Average order value, 12 months | Basket size signal |
| `loyalty_customer_visits_per_week_12m` | Visits / 52 | Normalized frequency |

### Basket / Category Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_customer_category_penetration_[CAT]` | % of visits including category [CAT] | One feature per top-N category |
| `loyalty_customer_category_spend_share_[CAT]` | % of total spend in category [CAT] | Wallet share by category |
| `loyalty_customer_brand_loyalty_score` | Fraction of category spend on preferred brand | High = brand-loyal; low = value-seeking |
| `loyalty_customer_private_label_ratio` | % of units that are private label | Price sensitivity proxy |
| `loyalty_customer_promo_sensitivity` | % of purchases coinciding with a promotion | Promo-driven vs. organic shopper |
| `loyalty_customer_basket_diversity_score` | Entropy of category distribution per basket | High = full-trip shopper |

### Channel & Lifecycle Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_customer_digital_channel_ratio` | % of visits via app or web | Digital-first vs. in-store |
| `loyalty_customer_tenure_days` | Days since first purchase | Loyalty lifecycle stage |
| `loyalty_customer_enrollment_cohort_month` | Month of enrollment | Cohort-level seasonal patterns |
| `loyalty_customer_is_lapsed` | Binary; recency_days > [X] | Churn risk indicator |
| `loyalty_customer_reactivation_count` | # of times customer lapsed then returned | Resilience signal |

### CLV-Specific Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_customer_predicted_tenure_months` | Estimated remaining active months | Survival model output |
| `loyalty_customer_spend_trend_6m` | Slope of monthly spend over 6 months | Growing vs. declining customer |
| `loyalty_customer_seasonal_spend_peak_month` | Month of highest historical spend | Engagement timing |

> [RISK: MED] Income, age, and household size are often partially inferred by the loyalty platform, not self-reported. Before using demographic features in models, confirm the inference methodology and assess for demographic bias. Run a Responsible AI assessment (see `responsible-ai-assessment.md`) before production.

---

## Use Case 4: Retail Media Audience Targeting (P2-B)

**Target variable:** Probability of purchase in target category within 30 days
**Grain:** One row = one household × campaign target category
**Minimum training history:** 12 months (to observe purchase cycle)
**Temporal split gap:** 30 days (matches prediction horizon)

### Audience Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `pos_customer_category_purchase_prob_30d` | P(purchase in category in next 30d), computed from historical base rate | Requires calibration |
| `pos_customer_category_recency_days` | Days since last purchase in target category | Recency within category |
| `pos_customer_category_frequency_12m` | Purchase occasions in category, 12 months | Category engagement depth |
| `loyalty_customer_brand_affinity_[BRAND]` | Purchase frequency for specific brand vs. category average | One-feature-per-brand for top-N brands |
| `loyalty_customer_price_sensitivity_tier` | HIGH / MED / LOW — derived from promo_sensitivity and private_label_ratio | Value vs. premium orientation |
| `web_customer_category_sessions_30d` | Sessions involving category product pages in last 30 days | Consideration signal from web |
| `web_customer_category_search_30d` | Search queries in category, 30 days | High-intent signal |

### Lookalike / Expansion Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_customer_segment_id` | Cluster assignment from segmentation model | Enables lookalike expansion |
| `loyalty_customer_embedding_[1..N]` | Dense embedding from trained customer tower | Enables nearest-neighbor lookalike |

> [RISK: HIGH] Retail media models must not use protected characteristics (race, religion, health status) as features, even indirectly via proxy variables. Run pii-scan before training. Income proxies (price sensitivity tier) require bias assessment.

---

## Use Case 5: Computer Vision — Fresh Freshness Scoring (P3-A Phase 2)

**Target variable:** Freshness score 1–5 (1=unacceptable, 5=excellent) — human annotated
**Grain:** One row = one image of one item at one point in time
**Minimum training images:** ≥ [5,000] labeled images per fresh category; balanced across freshness scores
**Cold-start:** No cold start issue — new produce items use the same visual model as existing ones

### Image Preprocessing Pipeline
1. **Resize** — standardize to [224 × 224] pixels (ImageNet-compatible); or [448 × 448] for detail-sensitive categories
2. **Normalize** — pixel values to [0, 1]; apply ImageNet mean/std normalization (`mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]`)
3. **Augmentation (training only):**
   - Random horizontal flip
   - Random rotation ± 15°
   - Random brightness / contrast jitter (range: ±15%)
   - Random crop + resize (simulates different camera angles)
   - [DO NOT augment: color hue shift — color is a freshness signal; do not destroy it]
4. **Background removal (optional):** If store shelf background creates noise, use segment-anything to isolate produce item before feature extraction

### Additional Features to Pair with Image
| Feature | Calculation | Notes |
|---------|------------|-------|
| `wms_item_days_to_bestby` | From WMS — days remaining on best-by date | Pairs image with known expiry signal |
| `wms_item_time_on_shelf_days` | Days since item was put on shelf | Age of item |
| `catalog_item_produce_category` | Category (e.g., leafy greens, citrus, stone fruit) | Category-specific freshness decay rates |

### Labeling Strategy
- Human annotators use a standardized rubric per category (e.g., for leafy greens: color, wilting, moisture, texture)
- Minimum 2 annotators per image; resolve disagreements by consensus or third annotator
- Inter-annotator agreement tracked; images with low agreement are flagged, not used in training
- Label distribution must be checked before training — should include images at all freshness levels

---

## Use Case 6: Fraud Detection — Loyalty Program (P0-B, supporting)

**Target variable:** Binary — is this transaction or redemption event fraudulent?
**Grain:** One row = one loyalty transaction or redemption event
**Class imbalance:** Fraud rate ≈ [X]% — requires explicit handling (oversampling, class weighting, or threshold tuning)
**Temporal split gap:** 7 days

### Fraud Features
| Feature | Calculation | Notes |
|---------|------------|-------|
| `loyalty_acct_redemptions_24h` | Count of redemption events in last 24 hours for this account | Velocity |
| `loyalty_acct_redemptions_distinct_locations_7d` | Count of distinct store IDs with redemption in 7 days | Geographic spread |
| `loyalty_acct_days_since_last_activity` | Days since any loyalty account activity | Dormant accounts suddenly active = risk |
| `loyalty_acct_email_change_7d` | Binary; email address changed in last 7 days | Account takeover signal |
| `loyalty_acct_phone_change_7d` | Binary; phone changed in last 7 days | Account takeover signal |
| `pos_txn_amount_vs_avg_ratio` | This transaction value / account avg transaction value | High-value anomaly |
| `pos_txn_category_vs_history` | % of basket in categories never purchased before | Category anomaly |
| `pos_txn_time_of_day` | Hour of transaction | Night transactions are higher risk |
| `loyalty_acct_linked_accounts_count` | # of accounts sharing same email/phone/address | Ring network signal |

> [RISK: HIGH] Fraud models must not directly or indirectly discriminate by protected class. Store geography can proxy for race and income. Audit feature importance regularly and flag any geographic feature driving > [X]% of predictions for bias review.

---

## Feature Store Registration

All features produced by this playbook must be registered in the feature store before use in production models.

| Registration Field | Required? |
|-------------------|-----------|
| Feature name (per naming convention) | Yes |
| Dataset source (DS-XX) | Yes |
| Calculation logic (SQL / Python) | Yes |
| Data contract version | Yes |
| PII flag | Yes |
| Temporal window | Yes |
| Update frequency (online / offline) | Yes |
| First available date | Yes |
| Owner / on-call team | Yes |

Online features (latency ≤ 100ms): serve from feature store online layer.
Offline features (training / batch inference): serve from feature store offline layer (e.g., Parquet in object storage).

---

## Related Artifacts

- [`use-case-dataset-matrix.md`](use-case-dataset-matrix.md) — dataset inputs per use case
- [`data-catalog-template.md`](data-catalog-template.md) — dataset quality assessment
- [`preprocessing-pipeline-design.md`](preprocessing-pipeline-design.md) — where feature engineering fits in the pipeline
- [`ADR-0045`](../../../decisions/ADR-0045-retail-ml-data-preprocessing-policy.md) — policy governing feature engineering and temporal splitting
- [`eval-baseline-guide.md`](../platform-enablement/eval-baseline-guide.md) — offline evaluation standards that these features are validated against
- [`responsible-ai-assessment.md`](../platform-enablement/responsible-ai-assessment.md) — bias assessment required before deploying segmentation / fraud models
