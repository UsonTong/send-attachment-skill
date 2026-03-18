#!/usr/bin/env python3
import argparse
import os
import pathlib
import shlex
import subprocess
import sys
from typing import Iterable

SUPPORTED_CHANNELS = {
    'telegram': {'supports_silent': True},
    'discord': {'supports_silent': False},
    'slack': {'supports_silent': False},
    'signal': {'supports_silent': False},
    'whatsapp': {'supports_silent': False},
    'imessage': {'supports_silent': False},
    'line': {'supports_silent': False},
    'googlechat': {'supports_silent': False},
}

CHANNEL_TARGET_ENV_VARS = {
    'telegram': ('OPENCLAW_CURRENT_TG_TARGET', 'OPENCLAW_TG_TARGET', 'TELEGRAM_CHAT_ID'),
    'discord': ('OPENCLAW_CURRENT_DISCORD_TARGET', 'OPENCLAW_DISCORD_TARGET', 'DISCORD_CHANNEL_ID'),
    'slack': ('OPENCLAW_CURRENT_SLACK_TARGET', 'OPENCLAW_SLACK_TARGET', 'SLACK_CHANNEL_ID'),
    'signal': ('OPENCLAW_CURRENT_SIGNAL_TARGET', 'OPENCLAW_SIGNAL_TARGET', 'SIGNAL_TARGET'),
    'whatsapp': ('OPENCLAW_CURRENT_WHATSAPP_TARGET', 'OPENCLAW_WHATSAPP_TARGET', 'WHATSAPP_TARGET'),
    'imessage': ('OPENCLAW_CURRENT_IMESSAGE_TARGET', 'OPENCLAW_IMESSAGE_TARGET', 'IMESSAGE_TARGET'),
    'line': ('OPENCLAW_CURRENT_LINE_TARGET', 'OPENCLAW_LINE_TARGET', 'LINE_TARGET'),
    'googlechat': ('OPENCLAW_CURRENT_GOOGLECHAT_TARGET', 'OPENCLAW_GOOGLECHAT_TARGET', 'GOOGLECHAT_TARGET'),
}


def first_env(names: Iterable[str]) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def parse_to(value: str) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    if ':' not in value:
        return None, value
    channel, target = value.split(':', 1)
    channel = channel.strip().lower()
    target = target.strip()
    return channel or None, target or None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Send one or more attachments to a supported messaging channel via openclaw message send'
    )
    parser.add_argument('files', nargs='*', help='Local file path(s) to send')
    parser.add_argument('--file', dest='files_flag', action='append', default=[], help='Local file path to send (repeatable)')
    parser.add_argument('--channel', help='Messaging channel, e.g. telegram, discord, slack, signal, whatsapp')
    parser.add_argument('--target', help='Target chat/channel/user id depending on channel')
    parser.add_argument('--to', help='Combined destination in the form channel:target, e.g. telegram:5794255231')
    parser.add_argument('--caption', default='', help='Optional caption text')
    parser.add_argument('--caption-file', help='Read caption text from a local file')
    parser.add_argument('--message', default='', help='Alias for --caption')
    parser.add_argument('--account', default='default', help='OpenClaw account id (default: default)')
    parser.add_argument('--silent', action='store_true', help='Send silently when the channel supports it')
    parser.add_argument('--current', action='store_true', help='Prefer current-session context env vars over generic defaults (default behavior)')
    parser.add_argument('--no-current', action='store_true', help='Ignore current-session context env vars and use only explicit args / generic env defaults')
    parser.add_argument('--dry-run', action='store_true', help='Print the command(s) without sending')
    args = parser.parse_args()

    args.files = [*args.files, *args.files_flag]
    if not args.files:
        parser.error('at least one file must be provided as a positional argument or via --file')

    if args.caption and args.message:
        parser.error('use either --caption or --message, not both')
    if args.caption_file and (args.caption or args.message):
        parser.error('use either --caption/--message or --caption-file, not both')
    if args.current and args.no_current:
        parser.error('use either --current or --no-current, not both')

    if args.message:
        args.caption = args.message

    if args.caption_file:
        caption_path = pathlib.Path(args.caption_file).expanduser().resolve()
        if not caption_path.exists() or not caption_path.is_file():
            parser.error(f'caption file not found: {caption_path}')
        args.caption = caption_path.read_text(encoding='utf-8')

    to_channel, to_target = parse_to(args.to) if args.to else (None, None)
    use_current = not args.no_current

    current_channel_env = ('OPENCLAW_CURRENT_CHANNEL',)
    generic_channel_env = ('OPENCLAW_CHANNEL', 'CHANNEL')
    generic_target_env = ('OPENCLAW_TARGET', 'OPENCLAW_CHAT_ID', 'CHAT_ID')

    channel_sources = [args.channel, to_channel]
    if use_current:
        channel_sources.append(first_env(current_channel_env))
    channel_sources.append(first_env(generic_channel_env))
    channel = next((value.strip().lower() for value in channel_sources if value and value.strip()), '')
    if not channel:
        parser.error('missing channel: pass --channel, use --to channel:target, or set OPENCLAW_CURRENT_CHANNEL / OPENCLAW_CHANNEL / CHANNEL')
    if channel not in SUPPORTED_CHANNELS:
        parser.error(f'unsupported channel: {channel}. Supported: {", ".join(sorted(SUPPORTED_CHANNELS))}')

    current_channel_target_env = tuple(
        name for name in CHANNEL_TARGET_ENV_VARS.get(channel, ()) if name.startswith('OPENCLAW_CURRENT_')
    )
    generic_channel_target_env = tuple(
        name for name in CHANNEL_TARGET_ENV_VARS.get(channel, ()) if not name.startswith('OPENCLAW_CURRENT_')
    )
    current_target_env = ('OPENCLAW_CURRENT_TARGET',)

    target_sources = [args.target, to_target]
    if use_current:
        target_sources.append(first_env(current_channel_target_env))
        target_sources.append(first_env(current_target_env))
    target_sources.append(first_env(generic_channel_target_env))
    target_sources.append(first_env(generic_target_env))
    target = next((value.strip() for value in target_sources if value and value.strip()), '')
    if not target:
        env_hint = ' / '.join(CHANNEL_TARGET_ENV_VARS.get(channel, ()) + CURRENT_TARGET_ENV_VARS)
        parser.error(f'missing target: pass --target, use --to {channel}:<target>, or set {env_hint}')

    args.channel = channel
    args.target = target
    args.used_current_context = use_current and (
        (not args.channel and False)  # kept for explicitness; resolved below via source strings
    )

    if args.silent and not SUPPORTED_CHANNELS[channel]['supports_silent']:
        print(f'WARN: --silent is not marked as supported for channel={channel}; passing it through anyway', file=sys.stderr)

    return args


def resolve_files(file_args: list[str]) -> list[pathlib.Path]:
    files = []
    missing = []
    for raw in file_args:
        path = pathlib.Path(raw).expanduser().resolve()
        if not path.exists() or not path.is_file():
            missing.append(str(path))
        else:
            files.append(path)
    if missing:
        joined = '\n  - '.join(['', *missing])
        raise SystemExit(f'ERROR: file not found:{joined}')
    return files


def build_command(channel: str, target: str, file_path: pathlib.Path, account: str, caption: str, silent: bool) -> list[str]:
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', channel,
        '--target', str(target),
        '--media', str(file_path),
        '--account', account,
    ]
    if caption:
        cmd += ['--message', caption]
    if silent:
        cmd += ['--silent']
    return cmd


def shell_join(parts: list[str]) -> str:
    return shlex.join(parts)


def main():
    args = parse_args()
    files = resolve_files(args.files)

    if len(files) > 1 and args.caption:
        print('INFO: applying the same caption to all files', file=sys.stderr)

    success = 0
    failed = 0
    exit_code = 0

    for file_path in files:
        cmd = build_command(args.channel, args.target, file_path, args.account, args.caption, args.silent)
        if args.dry_run:
            print(shell_join(cmd))
            continue

        print(f'[{args.channel}] sending {file_path} -> {args.target}', file=sys.stderr)
        proc = subprocess.run(cmd, text=True)
        if proc.returncode == 0:
            success += 1
            print(f'[{args.channel}] sent: {file_path} -> {args.target}', file=sys.stderr)
        else:
            failed += 1
            exit_code = proc.returncode
            print(f'[{args.channel}] ERROR: send failed for {file_path} -> {args.target}', file=sys.stderr)

    if not args.dry_run:
        print(f'Done: {success} succeeded, {failed} failed', file=sys.stderr)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()
