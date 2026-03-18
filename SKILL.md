---
name: send-attachment
description: Send one or more local files to supported messaging platforms via OpenClaw CLI. Use when an agent needs a simple black-box flow to post attachments (audio/images/docs) to Telegram, Discord, Slack, Signal, WhatsApp, iMessage, LINE, or Google Chat with optional caption/message text, dry-run, silent send, or current-session defaults.
---

# Send Attachment

## Overview
Use this skill to send one or more local files through OpenClaw's built-in messaging path with one consistent wrapper.

Prefer current-session delivery by default: when the caller provides current chat context through environment variables, this script automatically sends back to the active conversation unless explicitly overridden.

## Supported channels
- `telegram`
- `discord`
- `slack`
- `signal`
- `whatsapp`
- `imessage`
- `line`
- `googlechat`

## Commands
Send to the current conversation when context env vars are present:
```bash
export OPENCLAW_CURRENT_CHANNEL=telegram
export OPENCLAW_CURRENT_TARGET=5794255231
python3 skills/send-attachment/scripts/send_attachment.py /absolute/path/to/file.mp3
```

Send a file with an explicit destination:
```bash
skills/send-attachment/scripts/send-attachment \
  --to telegram:5794255231 \
  /absolute/path/to/file.mp3
```

Send multiple files:
```bash
python3 skills/send-attachment/scripts/send_attachment.py \
  --channel discord \
  --target 123456789012345678 \
  /tmp/a.jpg /tmp/b.jpg
```

Preview commands without sending:
```bash
python3 skills/send-attachment/scripts/send_attachment.py \
  --to slack:C0123456789 \
  --dry-run \
  /tmp/file.pdf
```

## Options
- `files` (required): one or more local file paths as positional arguments
- `--file`: alternative repeatable file flag
- `--channel`: messaging channel
- `--target`: target chat/channel/user id depending on channel
- `--to`: combined destination in the form `channel:target`
- `--caption`: optional attachment text
- `--message`: alias for `--caption`
- `--caption-file`: read attachment text from a local file
- `--account`: OpenClaw account id (`default` by default)
- `--silent`: send as silent notification when supported
- `--current`: prefer current-session env vars (default behavior)
- `--no-current`: ignore current-session env vars
- `--dry-run`: print command(s) without sending

## Resolution rules
Resolve channel in this order:
1. `--channel`
2. `--to channel:target`
3. `OPENCLAW_CURRENT_CHANNEL`
4. `OPENCLAW_CHANNEL`
5. `CHANNEL`

Resolve target in this order:
1. `--target`
2. `--to channel:target`
3. Channel-specific current env vars such as `OPENCLAW_CURRENT_TG_TARGET`, `OPENCLAW_CURRENT_DISCORD_TARGET`
4. Generic current env vars: `OPENCLAW_CURRENT_TARGET`
5. Channel-specific default env vars such as `OPENCLAW_TG_TARGET`, `OPENCLAW_DISCORD_TARGET`
6. Generic default env vars: `OPENCLAW_TARGET`, `OPENCLAW_CHAT_ID`, `CHAT_ID`

Use `--no-current` when you want to ignore current-session context and fall back only to explicit args or generic defaults.

## Notes
- This skill is a wrapper around `openclaw message send --channel ... --target ... --media ...`
- Send files serially to reduce rate-limit and debugging pain.
- If multiple files are sent with `--caption` or `--message`, the same text is applied to each file.
- If send fails, check provider permissions and target correctness.
e-limit and debugging pain.
- If multiple files are sent with `--caption` or `--message`, the same text is applied to each file.
- If send fails, check provider permissions and target correctness.
rectness.
