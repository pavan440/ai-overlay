from typing import Generator


def call_anthropic(cfg: dict, messages: list) -> Generator[str, None, None]:
    import anthropic
    client = anthropic.Anthropic(api_key=cfg["api_key"])
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    chat_msgs = [m for m in messages if m["role"] != "system"]
    with client.messages.stream(
        model=cfg["model"],
        max_tokens=1024,
        system=system,
        messages=chat_msgs,
    ) as stream:
        for text in stream.text_stream:
            yield text
