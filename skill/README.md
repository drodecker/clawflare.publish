# ClawFlare Publisher Skill (Scaffold)

This is the initial scaffold for the **ClawFlare** OpenClaw skill.

## Quick Start (for testing the scaffold)

1. Install dependencies:
   ```bash
   pip install requests
   ```

2. (Optional but recommended) Install Wrangler globally for best directory publishing:
   ```bash
   npm install -g wrangler
   # or use npx
   ```

3. The skill is designed to be placed in your OpenClaw workspace `skills/` directory (or installed via ClawHub later).

## Current Structure

```
clawflare-skill/
├── SKILL.md              # Rich instructions for the agent (most important file)
├── README.md             # This file
└── tools/
    ├── __init__.py
    ├── cf_auth.py        # Token validation & setup
    ├── cf_projects.py    # list / create / get projects
    └── cf_publish.py     # publish_html_string + publish_directory (Wrangler preferred)
```

## How the Agent Uses It

The `SKILL.md` contains detailed guidance so the LLM knows exactly when and how to call the tools, what clarifying questions to ask, and how to present results.

## Testing the Core Logic

You can test the underlying Python functions directly:

```python
from tools.cf_auth import validate_token
from tools.cf_publish import publish_content

result = validate_token("your_api_token_here")
print(result)

# Then publish a test page
publish_result = publish_content(
    token="your_token",
    account_id="your_account_id",
    project_name="your-existing-project",
    html_content="<h1>Hello from ClawFlare scaffold test</h1>"
)
print(publish_result)
```

See also the standalone `prototype_clawflare.py` in the parent artifacts folder for a CLI version you can run immediately.

## Next Steps (Development Roadmap for this skill)

- Hook into real OpenClaw tool registration / secrets system
- Improve Wrangler output parsing and progress streaming
- Add better error classification and retry logic
- Expand to full directory manifest support in pure Python (when Wrangler unavailable)
- Add OAuth PKCE path (later phase)
- Publish to ClawHub once stable

This scaffold already gives you a working, reliable foundation for agent-driven Cloudflare Pages publishing. 

Built for the OpenClaw ecosystem by Grok + David Rodecker.