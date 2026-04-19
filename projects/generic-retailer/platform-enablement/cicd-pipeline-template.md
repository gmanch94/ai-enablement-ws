# CI/CD Pipeline Template — [RETAILER] AI Platform

**Owner:** AI Platform Team
**Applies to:** All AI agent and ML model deployments
**Tooling:** [CALLOUT: confirm CI/CD platform — GitHub Actions, GitLab CI, Azure DevOps, or other]

---

## Pipeline Stages Overview

```
PR opened
  │
  ├── 1. Lint & static analysis
  ├── 2. Unit tests
  ├── 3. Governance checks (automated — blocks merge if failed)
  │
Merge to main
  │
  ├── 4. Build & push container image
  ├── 5. Deploy to staging
  ├── 6. Eval gate (blocks prod promotion if failed)
  ├── 7. Human sign-off (Tier 2+)
  │
Promote to prod
  │
  └── 8. Deploy to production + smoke test
```

---

## GitHub Actions Template

> [CALLOUT: If using Azure DevOps, GitLab CI, or another CI/CD platform, request the equivalent pipeline template from the AI Platform Team. The stage logic and governance checks are identical; only the YAML syntax differs.]

```yaml
# .github/workflows/ai-agent-deploy.yml

name: AI Agent — CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CLOUD_SUBSCRIPTION_ID: ${{ secrets.CLOUD_SUBSCRIPTION_ID }}    # [CALLOUT: fill]
  LLM_PLATFORM_ENDPOINT: ${{ secrets.LLM_PLATFORM_ENDPOINT }}   # [CALLOUT: fill]
  RESOURCE_GROUP: rg-ai-${{ vars.BU_NAME }}-prod                 # set BU_NAME in repo vars
  CONTAINER_REGISTRY: ${{ secrets.CONTAINER_REGISTRY }}          # [CALLOUT: fill]

jobs:
  # ─────────────────────────────────────────
  # STAGE 1-2: Lint + Unit Tests
  # ─────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint (ruff)
        run: ruff check .

      - name: Type check (mypy)
        run: mypy src/

      - name: Unit tests
        run: pytest tests/unit/ -v --tb=short

  # ─────────────────────────────────────────
  # STAGE 3: Governance Checks (blocks merge)
  # ─────────────────────────────────────────
  governance:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Check model card exists
        run: |
          if [ ! -f "model-card.md" ]; then
            echo "❌ model-card.md not found — required for all AI deployments"
            exit 1
          fi
          echo "✅ model card found"

      - name: Check model card is complete
        run: python scripts/check_model_card.py model-card.md
        # check_model_card.py validates required sections are filled in (not placeholder text)

      - name: Check required tags defined
        run: python scripts/check_tags.py infra/tags.json
        # validates all required [RETAILER_TAG]-* tags present

      - name: Check no hardcoded secrets
        run: |
          pip install detect-secrets
          detect-secrets scan --baseline .secrets.baseline
          detect-secrets audit .secrets.baseline

      - name: Check no hardcoded prompts
        run: python scripts/check_no_hardcoded_prompts.py src/
        # scans for long string literals that look like system prompts — fail if found

      - name: Check PII checklist signed off
        run: python scripts/check_pii_signoff.py docs/pii-handling-checklist.md
        # verifies sign-off section is not blank

  # ─────────────────────────────────────────
  # STAGE 4: Build & Push Image
  # (runs on merge to main only)
  # ─────────────────────────────────────────
  build:
    runs-on: ubuntu-latest
    needs: governance
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to [CLOUD_PRIMARY]
        # [CALLOUT: Replace with [CLOUD_PRIMARY] login action]
        # Azure: uses: azure/login@v2
        # AWS: uses: aws-actions/configure-aws-credentials@v4
        # GCP: uses: google-github-actions/auth@v2
        uses: [CALLOUT: cloud-login-action]
        with:
          creds: ${{ secrets.CLOUD_CREDENTIALS }}

      - name: Build and push to [CONTAINER_REGISTRY]
        # [CALLOUT: Replace with [CLOUD_PRIMARY] container build command]
        # Azure: az acr build --registry $CONTAINER_REGISTRY ...
        # AWS: docker build + aws ecr get-login-password | docker push ...
        # GCP: gcloud builds submit --tag ...
        run: |
          [CALLOUT: container build and push command for [CLOUD_PRIMARY]]
          --image ${{ vars.BU_NAME }}-${{ vars.PROJECT_NAME }}:${{ github.sha }} \
          --file Dockerfile .

  # ─────────────────────────────────────────
  # STAGE 5-6: Deploy to Staging + Eval Gate
  # ─────────────────────────────────────────
  staging:
    runs-on: ubuntu-latest
    needs: build
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to [CLOUD_PRIMARY]
        uses: [CALLOUT: cloud-login-action]
        with:
          creds: ${{ secrets.CLOUD_CREDENTIALS }}

      - name: Deploy to staging endpoint
        # [CALLOUT: Replace with [CLOUD_PRIMARY] managed endpoint deployment command]
        run: |
          [CALLOUT: deploy to staging ML endpoint for [CLOUD_PRIMARY]]

      - name: Run eval gate
        run: |
          python scripts/run_eval.py \
            --endpoint staging \
            --golden-dataset eval-datasets/${{ vars.PROJECT_NAME }}/golden/latest.jsonl \
            --thresholds eval-config/thresholds.json \
            --fail-on-miss
        # Exits non-zero if any required metric is below threshold — blocks production promotion

      - name: Upload eval results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results-${{ github.sha }}
          path: eval-results/

  # ─────────────────────────────────────────
  # STAGE 7-8: Production Deploy
  # (requires manual approval for Tier 2+)
  # ─────────────────────────────────────────
  production:
    runs-on: ubuntu-latest
    needs: staging
    environment: production  # configure required reviewers for Tier 2+
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to [CLOUD_PRIMARY]
        uses: [CALLOUT: cloud-login-action]
        with:
          creds: ${{ secrets.CLOUD_CREDENTIALS }}

      - name: Deploy to production
        # [CALLOUT: Replace with [CLOUD_PRIMARY] managed endpoint deployment command]
        run: |
          [CALLOUT: deploy to production ML endpoint for [CLOUD_PRIMARY]]

      - name: Smoke test
        run: python scripts/smoke_test.py --endpoint prod --timeout 60

      - name: Notify on success
        run: |
          echo "✅ Deployed ${{ vars.PROJECT_NAME }} to production — SHA ${{ github.sha }}"
          # [CALLOUT: add Slack/Teams notification here]
```

---

## Governance Check Scripts

The pipeline references several check scripts. The Platform Team provides these in a shared repo. BU teams copy them into their project.

**[CALLOUT: Platform Team to publish scripts to internal repo (e.g. `github.com/[RETAILER]/ai-platform-tools`).]**

| Script | What it checks |
|---|---|
| `check_model_card.py` | All required sections present and not placeholder text |
| `check_tags.py` | All required [RETAILER_TAG]-* tags defined in infra/tags.json |
| `check_no_hardcoded_prompts.py` | No long string literals that look like system prompts in src/ |
| `check_pii_signoff.py` | PII checklist sign-off section is not blank |
| `run_eval.py` | Runs [LLM_PLATFORM] eval pipeline, compares to thresholds, exits non-zero on miss |
| `smoke_test.py` | Sends a known-good test input to the prod endpoint, validates response format |

---

## Environment Configuration

| Environment | Approval Required | Eval Gate | Tagging |
|---|---|---|---|
| `dev` | None | Recommended | `[RETAILER_TAG]-env: dev` |
| `staging` | None | **Required** | `[RETAILER_TAG]-env: staging` |
| `production` | **Tier 2+: Yes** (AI/ML Lead + Business Owner) | **Required** | `[RETAILER_TAG]-env: prod` |

Configure CI/CD environment protection rules:
- `production` environment → require approval from platform approvers team + BU business owner

---

## Secrets Required

Configure in CI/CD secrets (or [SECRET_STORE] + federated identity):

| Secret | Value |
|---|---|
| `CLOUD_CREDENTIALS` | Service account / service principal credentials for deployment |
| `CLOUD_SUBSCRIPTION_ID` | [CALLOUT: fill with [CLOUD_PRIMARY] subscription / project ID] |
| `LLM_PLATFORM_ENDPOINT` | [CALLOUT: fill with [LLM_PLATFORM] workspace endpoint] |
| `CONTAINER_REGISTRY` | [CALLOUT: fill with [CONTAINER_REGISTRY] name / URL] |

**Never store secrets as plain text in YAML.** Use CI/CD secret references only.
