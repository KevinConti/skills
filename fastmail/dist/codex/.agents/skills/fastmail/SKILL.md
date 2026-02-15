---
name: fastmail
description: "Read-only email access via Fastmail JMAP API — list mailboxes, search emails, read messages and threads"
version: 0.1.0
---

# fastmail v0.1.0

Read-only email access via Fastmail JMAP API — list mailboxes, search emails, read messages and threads

## Setup

Set the `SKILL_CONFIG_FASTMAIL_API_TOKEN` environment variable with a read-only Fastmail API token.

To create a token:
1. Go to Fastmail → Settings → Privacy & Security → Integrations → API tokens
2. Create a new token with **read-only** access and **Mail** scope only

Alternatively, run the interactive setup:
```bash
python scripts/fastmail.py setup
```

## Commands

All commands use the `scripts/fastmail.py` script. Requires Python 3 and the `requests` library (`pip install requests`).

### List mailboxes
```bash
python scripts/fastmail.py mailboxes
python scripts/fastmail.py mailboxes --json
```

### List recent emails
```bash
python scripts/fastmail.py list
python scripts/fastmail.py list --mailbox sent
python scripts/fastmail.py list --limit 10
python scripts/fastmail.py list --json
```

### Search emails
```bash
python scripts/fastmail.py search --text "meeting notes"
python scripts/fastmail.py search --from "alice@example.com"
python scripts/fastmail.py search --subject "invoice" --after 2025-01-01
python scripts/fastmail.py search --text "project" --body --json
```

Search flags: `--text`, `--from`, `--to`, `--subject`, `--mailbox`, `--after YYYY-MM-DD`, `--before YYYY-MM-DD`, `--body` (include full body), `--limit N`, `--json`.

### Read a specific email
```bash
python scripts/fastmail.py read <email-id>
python scripts/fastmail.py read <email-id> --json
```

### Read an email thread
```bash
python scripts/fastmail.py thread <email-id>
python scripts/fastmail.py thread <email-id> --json
```

Pass any email ID from the thread — the full conversation is returned in chronological order.

## Typical Workflows

1. **Check inbox**: `list` → scan subjects → `read <id>` for details
2. **Find an email**: `search --from "name" --after 2025-06-01` → `read <id>`
3. **Read a conversation**: `search --subject "topic"` → `thread <id>`
4. **Export data**: Add `--json` to any command for machine-readable output
