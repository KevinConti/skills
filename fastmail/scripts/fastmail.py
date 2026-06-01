#!/usr/bin/env python3
"""Fastmail CLI — read-only email access via JMAP API."""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime, timedelta, timezone

import requests

CREDENTIALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials")
TOKEN_PATH = os.path.join(CREDENTIALS_DIR, "fastmail-token.json")
SESSION_URL = "https://api.fastmail.com/jmap/session"


def load_token():
    env_token = os.environ.get("SKILL_CONFIG_FASTMAIL_API_TOKEN") or os.environ.get("FASTMAIL_API_TOKEN")
    if env_token:
        return env_token
    if not os.path.exists(TOKEN_PATH):
        print("Error: No Fastmail API token found.")
        print("Set SKILL_CONFIG_FASTMAIL_API_TOKEN or FASTMAIL_API_TOKEN env var,")
        print("or run: python fastmail.py setup")
        sys.exit(1)
    with open(TOKEN_PATH) as f:
        data = json.load(f)
    return data["api_token"]


def get_session(token):
    """Fetch JMAP session to discover account ID and API URL."""
    resp = requests.get(SESSION_URL, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 401:
        print("Error: Invalid or expired API token. Run: uv run python fastmail.py setup")
        sys.exit(1)
    resp.raise_for_status()
    session = resp.json()
    account_id = session["primaryAccounts"]["urn:ietf:params:jmap:mail"]
    api_url = session["apiUrl"]
    # apiUrl may be relative
    if api_url.startswith("/"):
        api_url = "https://api.fastmail.com" + api_url
    return account_id, api_url, token


def jmap_call(api_url, token, method_calls):
    """Make a JMAP API call."""
    payload = {
        "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
        "methodCalls": method_calls,
    }
    resp = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


def find_mailbox_id(account_id, api_url, token, mailbox_name):
    """Find mailbox ID by name (case-insensitive)."""
    result = jmap_call(api_url, token, [
        ["Mailbox/get", {"accountId": account_id, "properties": ["id", "name", "role", "totalEmails", "unreadEmails"]}, "m0"],
    ])
    mailboxes = result["methodResponses"][0][1]["list"]
    name_lower = mailbox_name.lower()
    # Try role match first (inbox, sent, drafts, trash, etc.)
    for mb in mailboxes:
        if mb.get("role") and mb["role"].lower() == name_lower:
            return mb["id"]
    # Then name match
    for mb in mailboxes:
        if mb["name"].lower() == name_lower:
            return mb["id"]
    return None


def format_addr(addr_list):
    """Format email address list for display."""
    if not addr_list:
        return ""
    parts = []
    for a in addr_list:
        name = a.get("name", "")
        email = a.get("email", "")
        if name:
            parts.append(f"{name} <{email}>")
        else:
            parts.append(email)
    return ", ".join(parts)


def format_date(date_str):
    """Format ISO date string for display."""
    if not date_str:
        return ""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if dt.date() == now.date():
            return dt.strftime("Today %I:%M %p")
        elif dt.date() == (now - timedelta(days=1)).date():
            return dt.strftime("Yesterday %I:%M %p")
        elif (now - dt).days < 7:
            return dt.strftime("%a %I:%M %p")
        else:
            return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return date_str


def get_text_body(email_data, api_url, token, account_id):
    """Extract plain text body from email data."""
    # Try textBody parts first
    text_parts = email_data.get("textBody", [])
    if text_parts:
        blob_ids = [p["blobId"] for p in text_parts if p.get("blobId")]
        if blob_ids:
            return download_blob(api_url, token, account_id, blob_ids[0])

    # Fall back to htmlBody
    html_parts = email_data.get("htmlBody", [])
    if html_parts:
        blob_ids = [p["blobId"] for p in html_parts if p.get("blobId")]
        if blob_ids:
            html = download_blob(api_url, token, account_id, blob_ids[0])
            # Basic HTML stripping for readability
            import re
            text = re.sub(r'<br\s*/?>', '\n', html)
            text = re.sub(r'<p[^>]*>', '\n', text)
            text = re.sub(r'</p>', '\n', text)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'&nbsp;', ' ', text)
            text = re.sub(r'&amp;', '&', text)
            text = re.sub(r'&lt;', '<', text)
            text = re.sub(r'&gt;', '>', text)
            text = re.sub(r'&#\d+;', '', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()

    return email_data.get("preview", "(no body)")


def download_blob(api_url, token, account_id, blob_id):
    """Download a blob (email body part) from JMAP."""
    # JMAP download URL pattern
    base = api_url.rsplit("/", 1)[0]  # Remove /api/ or /jmap/
    download_url = f"https://api.fastmail.com/jmap/download/{account_id}/{blob_id}/body?accept=application/octet-stream"
    resp = requests.get(download_url, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.text


# --- Commands ---

def cmd_setup(args):
    """Store Fastmail API token."""
    print("=== Fastmail CLI Setup ===\n")
    print("Create a read-only API token at:")
    print("  Fastmail → Settings → Privacy & Security → Integrations → API tokens\n")
    print("Settings:")
    print("  - Check 'Read-only access'")
    print("  - Select 'Mail' only (uncheck Contacts, Calendars)\n")

    token = input("Paste your API token: ").strip()
    if not token:
        print("Error: No token provided.")
        sys.exit(1)

    # Validate token
    print("\nValidating token...")
    resp = requests.get(SESSION_URL, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 401:
        print("Error: Invalid token. Check that you copied the full token value.")
        sys.exit(1)
    resp.raise_for_status()

    session = resp.json()
    account_id = session["primaryAccounts"]["urn:ietf:params:jmap:mail"]
    username = session.get("username", "unknown")

    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump({"api_token": token, "account_id": account_id, "username": username}, f, indent=2)
    os.chmod(TOKEN_PATH, 0o600)

    print(f"Authenticated as: {username}")
    print(f"Account ID: {account_id}")
    print(f"Token saved to: {TOKEN_PATH}\n")
    print("You can now use: uv run python fastmail.py list")


def cmd_mailboxes(args):
    """List all mailboxes."""
    token = load_token()
    account_id, api_url, token = get_session(token)

    result = jmap_call(api_url, token, [
        ["Mailbox/get", {"accountId": account_id, "properties": ["id", "name", "role", "totalEmails", "unreadEmails", "parentId"]}, "m0"],
    ])
    mailboxes = result["methodResponses"][0][1]["list"]

    # Sort: role-based first, then alphabetical
    def sort_key(mb):
        role_order = {"inbox": 0, "sent": 1, "drafts": 2, "archive": 3, "trash": 4, "junk": 5}
        role = mb.get("role", "")
        return (role_order.get(role, 99), mb["name"].lower())

    mailboxes.sort(key=sort_key)

    if args.json:
        print(json.dumps(mailboxes, indent=2))
        return

    print(f"\n{'Mailbox':<30} {'Total':>8} {'Unread':>8}  {'Role':<10}")
    print("-" * 62)
    for mb in mailboxes:
        name = mb["name"]
        total = mb.get("totalEmails") or 0
        unread = mb.get("unreadEmails") or 0
        role = mb.get("role") or ""
        unread_str = str(unread) if unread > 0 else ""
        print(f"  {name:<28} {total:>8} {unread_str:>8}  {role:<10}")
    print()


def cmd_list(args):
    """List recent emails in a mailbox."""
    token = load_token()
    account_id, api_url, token = get_session(token)

    mailbox_name = args.mailbox or "inbox"
    mailbox_id = find_mailbox_id(account_id, api_url, token, mailbox_name)
    if not mailbox_id:
        print(f"Error: Mailbox '{mailbox_name}' not found. Run: uv run python fastmail.py mailboxes")
        sys.exit(1)

    limit = args.limit or 20

    result = jmap_call(api_url, token, [
        ["Email/query", {
            "accountId": account_id,
            "filter": {"inMailbox": mailbox_id},
            "sort": [{"property": "receivedAt", "isAscending": False}],
            "limit": limit,
        }, "q0"],
        ["Email/get", {
            "accountId": account_id,
            "#ids": {"resultOf": "q0", "name": "Email/query", "path": "/ids"},
            "properties": ["id", "subject", "from", "to", "receivedAt", "preview", "keywords"],
        }, "g0"],
    ])

    emails = result["methodResponses"][1][1]["list"]

    if args.json:
        print(json.dumps(emails, indent=2))
        return

    print(f"\n=== {mailbox_name.title()} (showing {len(emails)} of {limit} requested) ===\n")
    for email in emails:
        unread = "$seen" not in email.get("keywords", {})
        marker = "*" if unread else " "
        date = format_date(email.get("receivedAt", ""))
        frm = format_addr(email.get("from", []))
        subject = email.get("subject", "(no subject)")
        preview = email.get("preview", "")[:80]
        eid = email["id"]

        print(f" {marker} {date:<20} {frm:<30}")
        print(f"   {subject}")
        print(f"   {preview}...")
        print(f"   ID: {eid}")
        print()


def cmd_search(args):
    """Search emails."""
    token = load_token()
    account_id, api_url, token = get_session(token)

    # Build filter
    filter_conditions = []

    if args.text:
        filter_conditions.append({"text": args.text})
    if args.subject:
        filter_conditions.append({"subject": args.subject})
    if getattr(args, "from", None):
        filter_conditions.append({"from": getattr(args, "from")})
    if args.to:
        filter_conditions.append({"to": args.to})
    if args.after:
        filter_conditions.append({"after": args.after + "T00:00:00Z"})
    if args.before:
        filter_conditions.append({"before": args.before + "T23:59:59Z"})

    if args.mailbox:
        mailbox_id = find_mailbox_id(account_id, api_url, token, args.mailbox)
        if mailbox_id:
            filter_conditions.append({"inMailbox": mailbox_id})

    if not filter_conditions:
        print("Error: At least one search filter is required (--text, --from, --subject, etc.)")
        sys.exit(1)

    if len(filter_conditions) == 1:
        email_filter = filter_conditions[0]
    else:
        email_filter = {"operator": "AND", "conditions": filter_conditions}

    limit = args.limit or 20

    email_properties = ["id", "subject", "from", "to", "receivedAt", "preview", "keywords"]
    email_get_opts = {
        "accountId": account_id,
        "#ids": {"resultOf": "q0", "name": "Email/query", "path": "/ids"},
        "properties": email_properties,
    }

    if args.body:
        email_properties.extend(["textBody", "htmlBody", "bodyValues"])
        email_get_opts["fetchTextBodyValues"] = True

    result = jmap_call(api_url, token, [
        ["Email/query", {
            "accountId": account_id,
            "filter": email_filter,
            "sort": [{"property": "receivedAt", "isAscending": False}],
            "limit": limit,
        }, "q0"],
        ["Email/get", email_get_opts, "g0"],
    ])

    total = result["methodResponses"][0][1].get("total", "?")
    emails = result["methodResponses"][1][1]["list"]

    if args.body:
        for email in emails:
            body_values = email.get("bodyValues", {})
            if body_values:
                parts = [part.get("value", "") for part in body_values.values() if part.get("value")]
                email["body"] = "\n".join(parts)
            else:
                email["body"] = get_text_body(email, api_url, token, account_id)

    if args.json:
        print(json.dumps({"total": total, "emails": emails}, indent=2))
        return

    print(f"\n=== Search Results ({len(emails)} shown, {total} total) ===\n")
    if not emails:
        print("  No results found.")
        print()
        return

    for email in emails:
        unread = "$seen" not in email.get("keywords", {})
        marker = "*" if unread else " "
        date = format_date(email.get("receivedAt", ""))
        frm = format_addr(email.get("from", []))
        subject = email.get("subject", "(no subject)")
        preview = email.get("preview", "")[:80]
        eid = email["id"]

        print(f" {marker} {date:<20} {frm:<30}")
        print(f"   {subject}")
        print(f"   {preview}...")
        print(f"   ID: {eid}")
        print()


def cmd_read(args):
    """Read a specific email by ID."""
    token = load_token()
    account_id, api_url, token = get_session(token)

    result = jmap_call(api_url, token, [
        ["Email/get", {
            "accountId": account_id,
            "ids": [args.id],
            "properties": ["id", "subject", "from", "to", "cc", "bcc", "replyTo", "receivedAt",
                           "sentAt", "preview", "textBody", "htmlBody", "bodyValues",
                           "keywords", "mailboxIds", "threadId"],
            "fetchTextBodyValues": True,
        }, "g0"],
    ])

    emails = result["methodResponses"][0][1]["list"]
    if not emails:
        not_found = result["methodResponses"][0][1].get("notFound", [])
        if not_found:
            print(f"Error: Email ID '{args.id}' not found.")
        else:
            print("Error: No email returned.")
        sys.exit(1)

    email = emails[0]

    if args.json:
        print(json.dumps(email, indent=2))
        return

    # Display header
    print(f"\n{'='*70}")
    print(f"Subject: {email.get('subject', '(no subject)')}")
    print(f"From:    {format_addr(email.get('from', []))}")
    print(f"To:      {format_addr(email.get('to', []))}")
    if email.get("cc"):
        print(f"CC:      {format_addr(email['cc'])}")
    print(f"Date:    {email.get('receivedAt', '')}")
    print(f"ID:      {email['id']}")
    print(f"Thread:  {email.get('threadId', '')}")
    print(f"{'='*70}\n")

    # Display body
    body_values = email.get("bodyValues", {})
    if body_values:
        for part_id, part in body_values.items():
            text = part.get("value", "")
            if text:
                print(text)
    else:
        body = get_text_body(email, api_url, token, account_id)
        print(body)

    print()


def cmd_thread(args):
    """Read an email thread (conversation)."""
    token = load_token()
    account_id, api_url, token = get_session(token)

    # First get the email to find its threadId
    result = jmap_call(api_url, token, [
        ["Email/get", {
            "accountId": account_id,
            "ids": [args.id],
            "properties": ["threadId"],
        }, "g0"],
    ])

    emails = result["methodResponses"][0][1]["list"]
    if not emails:
        print(f"Error: Email ID '{args.id}' not found.")
        sys.exit(1)

    thread_id = emails[0]["threadId"]

    # Get the thread
    result = jmap_call(api_url, token, [
        ["Thread/get", {
            "accountId": account_id,
            "ids": [thread_id],
        }, "t0"],
    ])

    thread = result["methodResponses"][0][1]["list"]
    if not thread:
        print(f"Error: Thread '{thread_id}' not found.")
        sys.exit(1)

    email_ids = thread[0]["emailIds"]

    # Fetch all emails in the thread
    result = jmap_call(api_url, token, [
        ["Email/get", {
            "accountId": account_id,
            "ids": email_ids,
            "properties": ["id", "subject", "from", "to", "receivedAt", "preview",
                           "textBody", "htmlBody", "bodyValues", "keywords"],
            "fetchTextBodyValues": True,
        }, "g0"],
    ])

    thread_emails = result["methodResponses"][0][1]["list"]
    # Sort chronologically
    thread_emails.sort(key=lambda e: e.get("receivedAt", ""))

    if args.json:
        print(json.dumps(thread_emails, indent=2))
        return

    print(f"\n=== Thread: {thread_emails[0].get('subject', '(no subject)')} ({len(thread_emails)} messages) ===\n")

    for i, email in enumerate(thread_emails, 1):
        print(f"--- Message {i}/{len(thread_emails)} ---")
        print(f"From: {format_addr(email.get('from', []))}")
        print(f"To:   {format_addr(email.get('to', []))}")
        print(f"Date: {email.get('receivedAt', '')}")
        print()

        body_values = email.get("bodyValues", {})
        if body_values:
            for part_id, part in body_values.items():
                text = part.get("value", "")
                if text:
                    print(text)
        else:
            print(email.get("preview", "(no body)"))

        print()


def main():
    parser = argparse.ArgumentParser(description="Fastmail CLI — read-only email access via JMAP")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # setup
    subparsers.add_parser("setup", help="Store Fastmail API token")

    # mailboxes
    p_mailboxes = subparsers.add_parser("mailboxes", help="List all mailboxes")
    p_mailboxes.add_argument("--json", action="store_true", help="Output raw JSON")

    # list
    p_list = subparsers.add_parser("list", help="List recent emails")
    p_list.add_argument("--mailbox", "-m", help="Mailbox name (default: inbox)")
    p_list.add_argument("--limit", "-n", type=int, help="Number of emails (default: 20)")
    p_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # search
    p_search = subparsers.add_parser("search", help="Search emails")
    p_search.add_argument("--text", "-t", help="Full-text search")
    p_search.add_argument("--from", dest="from", help="Filter by sender")
    p_search.add_argument("--to", help="Filter by recipient")
    p_search.add_argument("--subject", "-s", help="Filter by subject")
    p_search.add_argument("--mailbox", "-m", help="Limit to mailbox")
    p_search.add_argument("--after", help="Emails after date (YYYY-MM-DD)")
    p_search.add_argument("--before", help="Emails before date (YYYY-MM-DD)")
    p_search.add_argument("--limit", "-n", type=int, help="Max results (default: 20)")
    p_search.add_argument("--body", action="store_true", help="Include full email body text")
    p_search.add_argument("--json", action="store_true", help="Output raw JSON")

    # read
    p_read = subparsers.add_parser("read", help="Read a specific email")
    p_read.add_argument("id", help="Email ID")
    p_read.add_argument("--json", action="store_true", help="Output raw JSON")

    # thread
    p_thread = subparsers.add_parser("thread", help="Read an email thread (conversation)")
    p_thread.add_argument("id", help="Any email ID in the thread")
    p_thread.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    commands = {
        "setup": cmd_setup,
        "mailboxes": cmd_mailboxes,
        "list": cmd_list,
        "search": cmd_search,
        "read": cmd_read,
        "thread": cmd_thread,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
