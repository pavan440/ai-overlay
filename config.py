import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG: dict = {
    "provider": "openai",
    "api_key": "",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini",
    "system_prompt": "You are a helpful assistant. Give concise, clear answers.",
    "opacity": 0.9,
}

OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
ANTHROPIC_MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-8"]

ROLE_PRESETS: dict[str, str] = {
    "Helpful Assistant": "You are a helpful assistant. Give concise, clear answers.",
    "Interview Coach": (
        "You are an interview coach helping a candidate prepare for technical interviews. "
        "Provide tips, model answers, and constructive feedback on their responses."
    ),
    "Technical Interviewer": (
        "You are an experienced technical interviewer. Ask focused questions, evaluate "
        "answers critically, and give detailed feedback on correctness and communication."
    ),
    "Code Reviewer": (
        "You are an expert code reviewer. Analyse code for bugs, performance issues, "
        "readability, and best practices. Be specific and actionable."
    ),
    "Tutor": (
        "You are a patient tutor. Explain concepts clearly with analogies and examples. "
        "Check understanding before moving on."
    ),
    "Custom": "",
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return {**DEFAULT_CONFIG, **data}
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
