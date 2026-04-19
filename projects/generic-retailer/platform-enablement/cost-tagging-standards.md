# Cost Tagging Standards — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Mandatory:** All [CLOUD_PRIMARY] resources in the AI platform must be tagged
**Enforcement:** Cloud policy — untagged resources are flagged and may be quarantined after 7 days

---

## Why Tagging Matters

[RETAILER]'s AI platform is shared infrastructure serving multiple BUs and projects. Without consistent tagging, it is impossible to attribute costs, enforce budget limits, or identify which team is consuming what. Tag-based attribution is the accountability mechanism for the federated model.

---

## Required Tags

Every cloud resource created for AI workloads must have all of the following tags:

| Tag Key | Format | Example | Purpose |
|---|---|---|---|
| `[RETAILER_TAG]-bu` | lowercase-hyphenated | `store-operations`, `supply-chain`, `digital`, `retail-media`, `pharmacy`, `engineering`, `platform` | Business unit owner |
| `[RETAILER_TAG]-project` | lowercase-hyphenated | `associate-copilot`, `replenishment-agent`, `knowledge-agent` | Use case / project |
| `[RETAILER_TAG]-env` | `dev` / `staging` / `prod` | `prod` | Deployment environment |
| `[RETAILER_TAG]-tier` | `tier-1` / `tier-2` / `tier-3` | `tier-1` | Risk tier (from intake form) |
| `[RETAILER_TAG]-owner` | email address | `aimlead@[RETAILER].com` | AI/ML lead responsible for the resource |
| `[RETAILER_TAG]-cost-centre` | cost centre code | `CC-12345` | Finance attribution — [CALLOUT: confirm cost centre codes with Finance] |

> **[CALLOUT: Set `[RETAILER_TAG]` to the company-specific prefix used in your tag taxonomy, e.g. `kroger`, `albertsons`, `target`. Must be consistent across all resources.]**

---

## Optional (Recommended) Tags

| Tag Key | Format | Example | Purpose |
|---|---|---|---|
| `[RETAILER_TAG]-model` | model name + version | `gpt-4o-2024-11` | Track model-specific spend |
| `[RETAILER_TAG]-created` | `YYYY-MM-DD` | `2026-04-17` | Resource creation date |
| `[RETAILER_TAG]-review-date` | `YYYY-MM-DD` | `2027-04-17` | When to review if resource is still needed |

---

## Tag Taxonomy — BU Values

| Tag Value | BU |
|---|---|
| `platform` | AI Platform Team (shared infra) |
| `store-operations` | Store Operations AI |
| `supply-chain` | Supply Chain AI |
| `digital` | Digital & eCommerce AI |
| `retail-media` | [MEDIA_NETWORK] / Retail Media AI |
| `pharmacy` | Pharmacy AI (if applicable) |
| `engineering` | Engineering AI Enablement |

---

## Applying Tags — IaC Examples

### Terraform (cloud-agnostic)

```hcl
resource "example_resource" "ai_workspace" {
  name     = var.workspace_name
  location = var.location

  tags = {
    "${var.retailer_tag}-bu"          = "store-operations"
    "${var.retailer_tag}-project"     = "associate-copilot"
    "${var.retailer_tag}-env"         = "prod"
    "${var.retailer_tag}-tier"        = "tier-1"
    "${var.retailer_tag}-owner"       = "aimlead@example.com"
    "${var.retailer_tag}-cost-centre" = "CC-12345"
  }
}
```

### Python (cloud SDK — generic pattern)

```python
tags = {
    f"{RETAILER_TAG}-bu": "store-operations",
    f"{RETAILER_TAG}-project": "associate-copilot",
    f"{RETAILER_TAG}-env": "prod",
    f"{RETAILER_TAG}-tier": "tier-1",
    f"{RETAILER_TAG}-owner": "aimlead@example.com",
    f"{RETAILER_TAG}-cost-centre": "CC-12345",
}
```

> [CALLOUT: Add cloud-specific IaC examples (Bicep/ARM for Azure, CloudFormation for AWS, Deployment Manager for GCP) once [CLOUD_PRIMARY] is confirmed.]

---

## Cost Reporting

**Monthly cost report:** [COST_MANAGEMENT] generates a per-BU, per-project cost breakdown using these tags. Shared by the Platform Team to BU leads on the 5th of each month.

**Budget alerts:** Each BU has a monthly budget configured in [COST_MANAGEMENT]. Alerts fire at 80% and 100% of budget — AI/ML Lead and Business Owner notified.

**Token-level cost:** LLM token usage is tracked per deployment. Tag your deployments — token costs roll up to `[RETAILER_TAG]-project` in the monthly report.

**Shared platform infra:** Costs for shared resources ([VECTOR_STORE] shared index, [LLM_PLATFORM] Control Plane, [DATA_GOVERNANCE]) are attributed to `[RETAILER_TAG]-bu: platform` and reported separately.

---

## Enforcement

Cloud policy is configured to:
1. **Audit** — flag resources missing any required tag (daily scan)
2. **Alert** — notify AI Platform Team of untagged resources
3. **Quarantine** — after 7 days untagged, resource is isolated from network (non-prod) or flagged for manual review (prod)

BU teams are responsible for ensuring all resources are tagged at creation time. Retroactive tagging is painful — build tags into your IaC from day one.
