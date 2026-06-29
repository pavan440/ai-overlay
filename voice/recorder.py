import io
import threading
from typing import Callable

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024

# VAD tuning
SILENCE_THRESHOLD = 300          # RMS below this = silence
MIN_SPEECH_CHUNKS = int(0.3 * SAMPLE_RATE / CHUNK_SIZE)   # 0.3s minimum speech
SILENCE_CHUNKS_TO_STOP = int(1.5 * SAMPLE_RATE / CHUNK_SIZE)  # 1.5s silence → stop


class VoiceRecorder:
    def __init__(self) -> None:
        self._recording = False
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    # ── Manual mode (Ctrl+R) ──────────────────────────────────────────────────

    def start(self) -> None:
        with self._lock:
            self._frames = []
            self._recording = True
        threading.Thread(target=self._manual_loop, daemon=True).start()

    def stop(self) -> bytes | None:
        with self._lock:
            self._recording = False
            frames = list(self._frames)
        if not frames:
            return None
        return _to_wav(np.concatenate(frames, axis=0))

    def _manual_loop(self) -> None:
        device = _loopback_device()
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                            dtype="int16", blocksize=CHUNK_SIZE,
                            **({'device': device} if device is not None else {})) as stream:
            while True:
                with self._lock:
                    if not self._recording:
                        break
                data, _ = stream.read(CHUNK_SIZE)
                with self._lock:
                    self._frames.append(data.copy())

    # ── Auto (VAD) mode (Ctrl+L) ──────────────────────────────────────────────

    def start_vad(self, on_complete: Callable[[bytes | None], None]) -> None:
        """Listen until silence is detected, then call on_complete with WAV bytes."""
        with self._lock:
            self._frames = []
            self._recording = True
        threading.Thread(target=self._vad_loop, args=(on_complete,), daemon=True).start()

    def _vad_loop(self, on_complete: Callable[[bytes | None], None]) -> None:
        silence_count = 0
        speech_count = 0

        device = _loopback_device()
        stream_kwargs: dict = {
            "samplerate": SAMPLE_RATE, "channels": CHANNELS,
            "dtype": "int16", "blocksize": CHUNK_SIZE,
        }
        if device is not None:
            stream_kwargs["device"] = device

        with sd.InputStream(**stream_kwargs) as stream:
            while True:
                with self._lock:
                    if not self._recording:
                        break
                data, _ = stream.read(CHUNK_SIZE)
                chunk = data.copy()
                rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))

                if rms > SILENCE_THRESHOLD:
                    speech_count += 1
                    silence_count = 0
                    with self._lock:
                        self._frames.append(chunk)
                else:
                    if speech_count >= MIN_SPEECH_CHUNKS:
                        silence_count += 1
                        with self._lock:
                            self._frames.append(chunk)
                        if silence_count >= SILENCE_CHUNKS_TO_STOP:
                            break

        self._recording = False
        with self._lock:
            frames = list(self._frames)

        if speech_count >= MIN_SPEECH_CHUNKS and frames:
            on_complete(_to_wav(np.concatenate(frames, axis=0)))
        else:
            on_complete(None)

    def cancel(self) -> None:
        with self._lock:
            self._recording = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_wav(audio: np.ndarray) -> bytes:
    buf = io.BytesIO()
    wav.write(buf, SAMPLE_RATE, audio)
    return buf.getvalue()


def _loopback_device() -> int | None:
    """Return the WASAPI loopback device index, or None to use default mic."""
    try:
        for i, d in enumerate(sd.query_devices()):
            name = d.get("name", "").lower()
            if "loopback" in name and d.get("max_input_channels", 0) > 0:
                return i
    except Exception:
        pass
    return None
