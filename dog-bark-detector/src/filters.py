"""Filtro passa-banda per isolare la frequenza tipica dell'abbaio."""

from scipy.signal import butter, sosfiltfilt


def bandpass_filter(audio, sr, low_hz=1000.0, high_hz=4000.0, order=4):
    nyquist = sr / 2.0
    low = low_hz / nyquist
    high = min(high_hz / nyquist, 0.999)
    sos = butter(order, [low, high], btype="band", output="sos")
    return sosfiltfilt(sos, audio)
