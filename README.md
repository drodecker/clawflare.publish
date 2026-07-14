# ClawFlare Publisher

**OpenClaw skill + tooling for publishing web content to Cloudflare Pages.**

ClawFlare turns natural language instructions ("Publish a new landing page for the plumbing promo") into live, globally distributed static sites on Cloudflare's edge network — with reliable project management, subdomain handling, and clean agentic workflows.

> **Repo purpose**: Home for the ClawFlare OpenClaw skill, prototype, and supporting specification.

## Quick Start

### 1. Try the Prototype Immediately

```bash
git clone https://github.com/drodecker/clawflare.publish.git
cd clawflare.publish

# Install minimal dependency
pip install requests

# List your accounts
python prototype/prototype_clawflare.py --token YOUR_CLOUDFLARE_API_TOKEN list-accounts

# Publish a test HTML page
python prototype/prototype_clawflare.py --token YOUR_CLOUDFLARE_API_TOKEN --account-id YOUR_ACCOUNT_ID \
  publish-html --project test-clawflare \
  --html '<h1>Hello from ClawFlare</h1><p>Published via prototype</p>'
```

See the full prototype documentation inside `prototype/prototype_clawflare.py`.

### 2. Use the Skill in OpenClaw

Copy (or symlink) the `skill/` directory into your OpenClaw workspace `skills/` folder, or install via ClawHub once published.

The `skill/SKILL.md` contains rich instructions so the agent knows exactly when and how to use the tools, ask clarifying questions, and return clean results.

## What's in This Repo

- **`spec/`** — High-level business requirements & technical specification (revised with emphasis on value beyond raw API wrapping and tight MVP scope).
- **`prototype/`** — Standalone CLI script for immediate testing of auth + project listing + HTML publishing (direct upload, no Wrangler required).
- **`skill/`** — The actual OpenClaw skill scaffold:
  - `SKILL.md` — Agent instructions, tool descriptions, example workflows, error handling.
  - `tools/` — Python implementation (`cf_auth`, `cf_projects`, `cf_publish`).
  - Ready to drop into an OpenClaw workspace.

## Why a Dedicated Skill?

Even if you can already prompt OpenClaw to call the Cloudflare API directly, ClawFlare provides:

- **Reliability** — Correct manifest handling, deployment logic, and error recovery in stable code.
- **Great agent UX** — Built-in clarification flows and structured outputs.
- **Composability** — Easy to chain with content generation, testing, and notification skills.
- **Maintainability** — One place to evolve the capability.

## Status

- **Current state**: MVP scaffold + working prototype + detailed spec.
- **Next**: Iterate on the skill based on real usage, improve Wrangler integration, consider OAuth path, then publish to ClawHub.

## Contributing / Feedback

This is early-stage work by David Rodecker (Relevant Ads / Local Splash) with assistance from Grok. Feedback, issues, and PRs are welcome.

## License

MIT (see LICENSE if added in future commits).

---

**Built for the OpenClaw ecosystem.** Turn agent-generated content into live production sites with minimal friction.