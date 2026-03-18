# send-attachment

OpenClaw skill for sending one or more local attachments to supported messaging platforms through a single wrapper.

## What it does

- Send one or more files
- Prefer the current conversation when context env vars are available
- Support explicit cross-platform delivery with `--to channel:target`
- Wrap `openclaw message send` behind a simpler interface

## Supported channels

- Telegram
- Discord
- Slack
- Signal
- WhatsApp
- iMessage
- LINE
- Google Chat

## Files

- `SKILL.md` — skill metadata and usage guidance
- `scripts/send-attachment` — short shell entrypoint
- `scripts/send_attachment.py` — Python implementation

## Examples

Send to the current conversation:

```bash
export OPENCLAW_CURRENT_CHANNEL=telegram
export OPENCLAW_CURRENT_TARGET=5794255231
scripts/send-attachment /absolute/path/to/file.mp3
```

Send to an explicit destination:

```bash
scripts/send-attachment \
  --to discord:123456789012345678 \
  /tmp/file.png
```

Preview without sending:

```bash
scripts/send-attachment \
  --to telegram:5794255231 \
  --message "test file" \
  --dry-run \
  /tmp/file.txt
```

## Notes

- Local media paths must be readable by OpenClaw from an allowed directory.
- In this environment, using files inside the workspace is the safest path.
