"""Conferma opzionale dei candidati con YAMNet (TensorFlow nativo).

Caricamento lazy: tensorflow/tensorflow-hub vengono importati solo se
questo modulo viene effettivamente usato (--use-yamnet nella CLI).
"""

import csv
import io

import numpy as np

DEFAULT_TARGET_CLASSES = [
    "Bark", "Yip", "Howl", "Growling", "Whimper (dog)",
    "Dog", "Domestic animals, pets",
]

_model = None
_class_names = None


def _load_model():
    global _model, _class_names
    if _model is not None:
        return _model, _class_names

    import tensorflow_hub as hub
    import tensorflow as tf

    _model = hub.load("https://tfhub.dev/google/yamnet/1")
    class_map_path = _model.class_map_path().numpy().decode("utf-8")
    with tf.io.gfile.GFile(class_map_path) as f:
        reader = csv.DictReader(io.StringIO(f.read()))
        _class_names = [row["display_name"] for row in reader]

    return _model, _class_names


def confirm_segment(audio_16k_mono, target_classes=None, threshold=0.1):
    model, class_names = _load_model()
    target_classes = target_classes or DEFAULT_TARGET_CLASSES

    scores, _, _ = model(audio_16k_mono.astype(np.float32))
    scores = scores.numpy()
    max_scores_per_class = scores.max(axis=0)

    target_indices = [i for i, name in enumerate(class_names) if name in target_classes]
    if not target_indices:
        return False, 0.0, []

    relevant = [(class_names[i], float(max_scores_per_class[i])) for i in target_indices]
    relevant.sort(key=lambda x: -x[1])
    best_score = relevant[0][1]

    return best_score >= threshold, best_score, relevant
