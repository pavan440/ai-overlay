import io
import threading

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 1


class VoiceRecorder:
    def __init__(self) -> None:
        self._recording = False
        self._frames: list[np.ndarray] = []
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        with self._lock:
            self._frames = []
            self._recording = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self) -> bytes | None:
        with self._lock:
            self._recording = False
            frames = list(self._frames)
        if not frames:
            return None
        audio = np.concatenate(frames, axis=0)
        buf = io.BytesIO()
        wav.write(buf, SAMPLE_RATE, audio)
        return buf.getvalue()

    def _loop(self) -> None:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16") as stream:
            while True:
                with self._lock:
                    if not self._recording:
                        break
                data, _ = stream.read(1024)
                with self._lock:
                    self._frames.append(data.copy())
