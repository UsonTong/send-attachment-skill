---
name: send-attachment
description: Send local files to messaging platforms via OpenClaw CLI.
---

# Send Attachment

Wrapper around `openclaw message send` for sending files to Telegram/Discord/Slack/Signal/WhatsApp/iMessage/LINE/Google Chat.

## Usage

```bash
# Current conversation (auto from env vars)
scripts/send-attachment /path/to/file.mp3

# Explicit destination
scripts/send-attachment --to telegram:5794255231 /path/to/file.mp3

# Multiple files with caption
scripts/send-attachment --channel discord --target 12345 --caption "hi" /tmp/a.jpg /tmp/b.jpg

# Preview only
scripts/send-attachment --to slack:C0123 --dry-run /tmp/file.pdf
```

## Key options
`files` | `--to channel:target` | `--channel` | `--target` | `--caption`/`--message` | `--caption-file` | `--account` | `--silent` | `--dry-run`

## Resolution priority
- **Channel**: `--channel` > `--to` > `OPENCLAW_CURRENT_CHANNEL` > `OPENCLAW_CHANNEL` > `CHANNEL`
- **Target**: `--target` > `--to` > channel-specific `OPENCLAW_CURRENT_*_TARGET` > `OPENCLAW_CURRENT_TARGET` > channel-specific defaults > `OPENCLAW_TARGET`/`CHAT_ID`
