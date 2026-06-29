# AI Overlay

A stealth Windows overlay that connects to OpenAI or Anthropic. Invisible to screen sharing, hidden from the taskbar and Alt+Tab.

## Features

- **Stealth** — excluded from screen capture (OBS, Teams, Zoom, Windows capture), hidden from taskbar and Alt+Tab switcher
- **AI Chat** — streams responses from OpenAI (GPT-4o, GPT-4o-mini) or Anthropic (Claude)
- **Voice Input** — press `Ctrl+R` to record, releases and auto-transcribes via OpenAI Whisper
- **Screenshot** — press `Ctrl+G` to capture your screen and send it to GPT-4o vision
- **RAG / File Context** — upload PDF, DOCX, TXT, or code files; relevant chunks are injected automatically into every query
- **Role Play** — switch between presets (Interview Coach, Technical Interviewer, Tutor, Code Reviewer) or write a custom system prompt
- **Model Selector** — switch models without leaving the chat

## Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+R` | Start / stop voice recording |
| `Ctrl+G` | Capture screenshot and attach to next message |
| `Ctrl+H` | Hide / show the overlay |
| `Ctrl+Q` | Quit |
| `Enter` | Send message |
| `Shift+Enter` | New line in input |

## Requirements

- Windows 10 version 2004 (build 19041) or later
- Python 3.11+ **or** the pre-built `AIOverlay.exe` (no Python needed)

## Quick Start

### Run from source

```bash
pip install openai anthropic sounddevice Pillow scikit-learn pypdf
python overlay.py
```

### Run the built exe

Double-click `dist\AIOverlay\AIOverlay.exe` — no Python required.

### Build the exe yourself

```bash
pip install pyinstaller
build.bat
```

Output: `dist\AIOverlay\AIOverlay.exe`

## Configuration

On first run, go to **Settings › Model** and enter your API key. Settings are saved to `config.json` in the same folder.

### config.json format

```json
{
  "provider": "openai",
  "api_key": "sk-proj-...",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "system_prompt": "You are a helpful assistant. Give concise, clear answers.",
  "opacity": 0.9
}
```

| Key | Values | Description |
|---|---|---|
| `provider` | `"openai"` / `"anthropic"` | Which AI provider to use |
| `api_key` | `"sk-proj-..."` | Your API key — never commit this |
| `base_url` | URL | OpenAI-compatible base URL (change for Groq, local LLMs, etc.) |
| `model` | e.g. `"gpt-4o-mini"` | Model name for the selected provider |
| `system_prompt` | Any string | Default AI persona / instructions |
| `opacity` | `0.2` – `1.0` | Window transparency |

> `config.json` is in `.gitignore` and will never be committed.

## Project Structure

```
ai-overlay/
├── overlay.py          # Entry point
├── config.py           # Config loading + model/role constants
├── theme.py            # Colour palette
├── win32_utils.py      # Screen-capture exclusion, always-on-top, taskbar hiding
├── ai/                 # OpenAI + Anthropic streaming clients
├── voice/              # Mic recording + Whisper transcription
├── vision/             # Screenshot capture
├── rag/                # File ingestion, chunking, TF-IDF retrieval
├── ui/                 # Tkinter UI (app, chat tab, settings tab)
├── build.bat           # PyInstaller build script
└── overlay.spec        # PyInstaller spec
```

## Supported File Types for RAG

PDF, DOCX, TXT, MD, PY, JS, TS, JSON, CSV — any plain-text format works as a fallback.
