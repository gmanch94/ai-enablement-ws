# /update-cheatsheet-aws

Keep `context/aws-ai-mlops-cheatsheet.md` current with the latest AWS AI and MLOps announcements.

## When to run
- After **AWS re:Invent** (December) or **AWS re:Inforce** / **AWS Summit** events
- When you hear about a new Amazon Bedrock or SageMaker release
- When the monthly scheduled agent flags pending changes

## Steps

1. **Read the current cheatsheet**
   - Load `reference/aws-ai-mlops-cheatsheet.md`
   - Note the `Last updated` date and all services, SDKs, and status labels

2. **Web-search for updates** — run all in parallel:
   - `Amazon Bedrock SageMaker new services features <current year>`
   - `AWS AI MLOps announcements re:Invent re:Inforce <current year>`
   - `AWS AI SDK boto3 sagemaker deprecation EOL <current year>`
   - Fetch `https://aws.amazon.com/blogs/aws/` for recent AWS AI posts
   - Fetch `https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html`

3. **Diff against current content** — identify:
   - New services not yet in the cheatsheet
   - Preview → GA promotions
   - Deprecation or EOL notices
   - SDK version changes or new packages

4. **Present proposed diff** — show what would be ADDED, CHANGED, or REMOVED. Do NOT write yet.

5. **Wait for approval**, then apply and update `Last updated` date.

## Scope
- AWS 1st-party services only
- AWS SDKs: boto3, sagemaker Python SDK, amazon-bedrock-runtime, AWS CDK, Neuron SDK
