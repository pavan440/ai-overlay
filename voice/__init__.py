import io

from .recorder import VoiceRecorder


def transcribe(wav_bytes: bytes, api_key: str, base_url: str) -> str:
    import openai
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    audio_file = io.BytesIO(wav_bytes)
    audio_file.name = "recording.wav"          # type: ignore[attr-defined]
    result = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return result.text


__all__ = ["VoiceRecorder", "transcribe"]
