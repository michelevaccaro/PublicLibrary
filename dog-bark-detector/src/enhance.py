"""Esalta la presenza dell'abbaio rispetto al rumore di fondo nell'output.

Il registratore, fermo e non direzionale a 60 metri, cattura il rumore a
bassa frequenza (treni, traffico) molto più forte di quanto lo si percepisca
a orecchio dal balcone, dove l'abbaio risulta relativamente più presente e
fastidioso. Per avvicinare l'ascolto all'esperienza reale: si taglia il
rumore sotto la frequenza dell'abbaio (passa-alto) e si somma un boost
parallelo nella banda dove si concentra l'abbaio, invece di isolarlo del
tutto con un passa-banda stretto (che lo farebbe suonare innaturale/sottile).
"""

import numpy as np
from scipy.signal import butter, sosfiltfilt

from .filters import bandpass_filter


def enhance_bark_presence(audio, sr, highpass_hz=400.0, boost_band=(1200.0, 2500.0), boost_gain_db=6.0):
    single_channel = audio.ndim == 1
    data = audio[:, None] if single_channel else audio

    hp_sos = butter(2, highpass_hz / (sr / 2.0), btype="highpass", output="sos")
    boost_gain = 10 ** (boost_gain_db / 20.0)

    out = np.zeros_like(data)
    for ch in range(data.shape[1]):
        channel = data[:, ch]
        highpassed = sosfiltfilt(hp_sos, channel)
        boosted = bandpass_filter(channel, sr, boost_band[0], boost_band[1])
        out[:, ch] = highpassed + boost_gain * boosted

    return out[:, 0] if single_channel else out
