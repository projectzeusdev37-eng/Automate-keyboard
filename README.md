# Automate-keyboard

Python script that types the contents of a text file via simulated keystrokes at a configurable speed (WPM) and after a configurable startup delay.

## Install

```bash
pip install pynput
```

## Usage

```bash
python main.py <path-to-text-file> [--wpm 60] [--delay 5]
```

Example:

```bash
python main.py message.txt --wpm 80 --delay 3
```

Click into the target window during the startup countdown. Abort with `Ctrl+C` in the terminal.

## Arguments

- `file` — path to the text file to type out (required).
- `--wpm` — typing speed in words per minute (default `60`; 1 word = 5 characters).
- `--delay` — seconds to wait before typing starts (default `5`).
- `--encoding` — file encoding (default `utf-8`).

## Limitations

- **Remote desktop targets don't work.** Over Chrome Remote Desktop, RDP, or VNC, the remote protocol drops synthesized Shift events — uppercase letters and shifted symbols (`:`, `(`, `{`, `_`, `"`, `?`, etc.) are silently skipped while lowercase letters come through normally. Workaround: run the script *on* the remote machine itself so no remote-desktop channel sits between the script and the target window.
- **WSL cannot drive Windows applications.** pynput inside WSL reaches only the Linux input layer (X11/Wayland). Use Windows-native Python when targeting Windows apps.
- **Code editors auto-indent.** IDEs (VS Code, PyCharm, etc.) add their own indent on newline, which compounds with the script's leading whitespace and produces runaway indentation. Target a plain text field (Notepad, web textarea) or disable auto-indent on the target.
- **Keyboard layout.** Shifted-character handling assumes a US layout; other layouts may mistype some symbols.
- **Linux requires a display server.** pynput needs X11 or Wayland — headless environments are not supported.
- **Injected-input filtering.** Some applications (games with anti-cheat, certain secure input modes) ignore programmatically synthesized keystrokes entirely. A real-hardware workaround (e.g. a Raspberry Pi Pico flashed as a USB HID keyboard) is the only reliable bypass.

## Tested On

- Windows 11, native Python, local targets — works reliably.
