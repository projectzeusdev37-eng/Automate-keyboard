#!/usr/bin/env python3
"""Keyboard typing simulator.

Reads text from a file and types it as if from a real keyboard, at a
user-defined speed (WPM) and after a user-defined startup delay.

Usage:
    python main.py <path-to-text-file> [--wpm 60] [--delay 5]

Example:
    python main.py message.txt --wpm 80 --delay 3

Notes:
    - Standard typing convention: 1 word = 5 characters (including spaces).
    - During the start delay, click into the target window/text field.
    - Abort with Ctrl+C in the terminal, or close the target window.

See README.md for platform limitations (remote desktop, WSL, code editors).
"""

import argparse
import sys
import time
from pathlib import Path

try:
    from pynput.keyboard import Controller, Key
except ImportError:
    print(
        "Missing dependency 'pynput'. Install it with:\n"
        "    pip install pynput",
        file=sys.stderr,
    )
    sys.exit(1)


# Characters that need a dedicated Key event rather than Controller.type().
SPECIAL_KEYS = {
    "\n": Key.enter,
    "\r": Key.enter,
    "\t": Key.tab,
}

# Characters that require Shift on a US keyboard layout. Pressing Shift
# explicitly (instead of relying on Controller.type()) is more reliable
# on platforms that inspect modifier state separately from the key event.
SHIFTED = set('~!@#$%^&*()_+{}|:"<>?') | set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Minimum hold/gap time (seconds) for each keypress. Raise this for
# remote-desktop protocols that drop sub-millisecond key events; leave
# small (~0.02) for local targets.
MIN_KEY_HOLD = 0.02


def type_text(text: str, wpm: float) -> None:
    """Type ``text`` at approximately ``wpm`` words per minute."""
    chars_per_second = wpm * 5 / 60
    delay_per_char = max(1.0 / chars_per_second, MIN_KEY_HOLD * 2)

    keyboard = Controller()

    for char in text:
        if char in SPECIAL_KEYS:
            keyboard.press(SPECIAL_KEYS[char])
            time.sleep(MIN_KEY_HOLD)
            keyboard.release(SPECIAL_KEYS[char])
        elif char in SHIFTED:
            keyboard.press(Key.shift)
            time.sleep(MIN_KEY_HOLD)
            keyboard.type(char)
            time.sleep(MIN_KEY_HOLD)
            keyboard.release(Key.shift)
        else:
            keyboard.type(char)
        time.sleep(delay_per_char)


def countdown(seconds: float) -> None:
    """Print a live countdown so the user can focus the target window."""
    whole = int(seconds)
    for remaining in range(whole, 0, -1):
        print(
            f"Starting in {remaining}...  (focus your target window)",
            end="\r",
            flush=True,
        )
        time.sleep(1)
    frac = seconds - whole
    if frac > 0:
        time.sleep(frac)
    print(" " * 60, end="\r")  # clear the countdown line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Type the contents of a text file as if from a keyboard.",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the text file to type out.",
    )
    parser.add_argument(
        "--wpm",
        type=float,
        default=60.0,
        help=(
            "Typing speed in words per minute (default: 60). "
            "1 word = 5 characters by convention."
        ),
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help=(
            "Seconds to wait before typing starts (default: 5). "
            "Use this time to click into the target window."
        ),
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.file.is_file():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    if args.wpm <= 0:
        print("Error: --wpm must be greater than 0.", file=sys.stderr)
        return 1

    if args.delay < 0:
        print("Error: --delay cannot be negative.", file=sys.stderr)
        return 1

    try:
        text = args.file.read_text(encoding=args.encoding)
    except UnicodeDecodeError as e:
        print(
            f"Error decoding file as {args.encoding}: {e}",
            file=sys.stderr,
        )
        return 1

    if not text:
        print("Warning: file is empty. Nothing to type.", file=sys.stderr)
        return 0

    print(f"File:  {args.file}  ({len(text)} chars)")
    print(f"Speed: {args.wpm} WPM")
    print(f"Delay: {args.delay} seconds")
    print()

    countdown(args.delay)

    try:
        type_text(text, args.wpm)
    except KeyboardInterrupt:
        print("\nAborted.")
        return 130

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
