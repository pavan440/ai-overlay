import os
import tempfile

from .recorder import VoiceRecorder


def transcribe(wav_bytes: bytes, api_key: str, base_url: str) -> str:
    import openai

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tmp.write(wav_bytes)
        tmp.close()
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        with open(tmp.name, "rb") as f:
            result = client.audio.transcriptions.create(model="whisper-1", file=f)
        return result.text
    finally:
        os.unlink(tmp.name)


__all__ = ["VoiceRecorder", "transcribe"]
