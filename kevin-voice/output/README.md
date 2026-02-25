# your-voice

A Claude Code plugin that applies Kevin Conti's writing voice and style for content generation.

## What it does

This plugin provides a voice skill that teaches Claude to write in Kevin's voice — direct, casual, opinionated, grounded in specifics. It covers blog posts (strategy, personal, daily standup), tweets, emails, and reddit comments.

The skill was extracted from 10 writing samples across 4 content types using a 3-pass voice extraction process.

## Installation

### Option A: Local plugin

```bash
cp -r . ~/claude-plugins/your-voice/
claude plugin add ~/claude-plugins/your-voice/
```

### Option B: Git repository

```bash
git init
git add .
git commit -m "Personal voice skill v0.1.0"
git remote add origin <your-repo-url>
git push -u origin main
```

## Usage

Once installed, ask Claude to write in Kevin's voice:

- "Write a blog post about [topic] in my voice"
- "Draft an email to [person] about [topic]"
- "Write a tweet about [topic]"

The skill automatically applies voice patterns, vocabulary preferences, and format-specific conventions based on the content type.

## Structure

```
.claude-plugin/
  plugin.json          # Plugin metadata
skills/
  your-voice/
    SKILL.md           # Voice skill definition
README.md              # This file
```

## Maintenance

Re-run the extraction process when:
- Claude's output no longer sounds like you
- You've started writing in a new format
- Your style has evolved (yearly re-extraction is reasonable)
