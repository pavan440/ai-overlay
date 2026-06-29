from typing import Generator


def call_openai(cfg: dict, messages: list) -> Generator[str, None, None]:
    import openai
    client = openai.OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    response = client.chat.completions.create(
        model=cfg["model"],
        messages=messages,
        stream=True,
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
