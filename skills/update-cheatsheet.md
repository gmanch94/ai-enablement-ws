# /update-cheatsheet

Keep `context/azure-ai-mlops-cheatsheet.md` current with the latest Azure AI and MLOps announcements.

## When to run
- After major Microsoft events: **Build** (May), **Ignite** (November)
- When you hear about a new Azure AI service or SDK release
- When the monthly scheduled agent flags pending changes

## Steps

1. **Read the current cheatsheet**
   - Load `reference/azure-ai-mlops-cheatsheet.md`
   - Note the `Last updated` date at the top

2. **Web-search for updates** — run all three in parallel:
   - `Microsoft Foundry Azure AI new services features <current year>`
   - `Azure Machine Learning MLOps SDK updates <current year>`
   - `Azure AI announcements Build Ignite <current year>`
   - Fetch `https://learn.microsoft.com/en-us/azure/foundry/whats-new-foundry` for the official what's-new page

3. **Diff against current content** — identify:
   - New services not yet in the cheatsheet
   - Services that have moved from Preview → GA
   - Deprecations or EOL announcements
   - SDK version changes or new packages
   - Rebrands or category restructures

4. **Present a proposed diff** — show the user:
   - What would be ADDED (new rows, new sections)
   - What would be CHANGED (status updates, descriptions)
   - What would be REMOVED or flagged as deprecated
   - Do NOT write anything yet

5. **Wait for approval** — ask the user to confirm, reject, or modify the proposed changes

6. **Apply approved changes** — update `reference/azure-ai-mlops-cheatsheet.md`:
   - Update the `Last updated` date
   - Apply only the approved changes
   - Add new items to the `What's Changed` section at the bottom

## Scope
- Azure and Microsoft 1st-party services only
- Microsoft SDKs used in AIEnablement and MLOps code
- No ISV or open-source tools unless Microsoft-owned (e.g. Semantic Kernel, AutoGen)
