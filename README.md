# send-attachment

OpenClaw skill for sending one or more local attachments to supported messaging platforms through a single wrapper.

一个用于 OpenClaw 的附件发送 skill，用统一入口把一个或多个本地文件发送到多个主流消息平台。

## What it does / 作用

- Send one or more files
- Prefer the current conversation when context env vars are available
- Support explicit cross-platform delivery with `--to channel:target`
- Wrap `openclaw message send` behind a simpler interface

- 支持发送一个或多个文件
- 在存在当前会话上下文时，默认优先发回当前对话
- 支持通过 `--to channel:target` 显式跨平台发送
- 用更简单的接口封装 `openclaw message send`

## Supported channels / 支持的平台

- Telegram
- Discord
- Slack
- Signal
- WhatsApp
- iMessage
- LINE
- Google Chat

## Files / 文件结构

- `SKILL.md` — skill metadata and usage guidance / skill 元数据与使用说明
- `scripts/send-attachment` — short shell entrypoint / 更短的 shell 入口
- `scripts/send_attachment.py` — Python implementation / Python 实现

## Examples / 示例

### Send to the current conversation / 发到当前对话

```bash
export OPENCLAW_CURRENT_CHANNEL=telegram
export OPENCLAW_CURRENT_TARGET=5794255231
scripts/send-attachment /absolute/path/to/file.mp3
```

### Send to an explicit destination / 显式指定目标发送

```bash
scripts/send-attachment \
  --to discord:123456789012345678 \
  /tmp/file.png
```

### Preview without sending / 预览命令但不实际发送

```bash
scripts/send-attachment \
  --to telegram:5794255231 \
  --message "test file" \
  --dry-run \
  /tmp/file.txt
```

## Notes / 注意事项

- Local media paths must be readable by OpenClaw from an allowed directory.
- In this environment, using files inside the workspace is the safest path.
- 本地附件路径需要位于 OpenClaw 允许读取的目录内。
- 在当前环境下，优先使用 workspace 内的文件最稳。
