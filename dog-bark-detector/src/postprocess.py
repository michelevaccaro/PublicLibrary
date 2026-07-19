"""Applica le regole di padding e merge alle sequenze di abbaio rilevate."""

from dataclasses import dataclass


@dataclass
class Sequence:
    start: float
    end: float
    bark_count: int
    bark_windows: list  # [(start, end), ...] tempo assoluto nel file sorgente

    @property
    def bark_starts(self):
        return [w[0] for w in self.bark_windows]


def merge_and_pad(candidates, gap_threshold_s=5.0, padding_s=3.0, duration_s=None):
    if not candidates:
        return []

    events = sorted(candidates, key=lambda c: c.start)

    sequences = []
    current_start = events[0].start
    current_end = events[0].end
    current_windows = [(events[0].start, events[0].end)]

    for event in events[1:]:
        if event.start - current_end < gap_threshold_s:
            current_end = max(current_end, event.end)
            current_windows.append((event.start, event.end))
        else:
            sequences.append((current_start, current_end, current_windows))
            current_start, current_end = event.start, event.end
            current_windows = [(event.start, event.end)]
    sequences.append((current_start, current_end, current_windows))

    padded = []
    for start, end, windows in sequences:
        padded_start = max(0.0, start - padding_s)
        padded_end = end + padding_s
        if duration_s is not None:
            padded_end = min(duration_s, padded_end)
        padded.append(Sequence(padded_start, padded_end, len(windows), windows))

    return _merge_overlaps(padded)


def _merge_overlaps(sequences):
    if not sequences:
        return []

    merged = [sequences[0]]
    for seq in sequences[1:]:
        last = merged[-1]
        if seq.start <= last.end:
            merged[-1] = Sequence(
                last.start,
                max(last.end, seq.end),
                last.bark_count + seq.bark_count,
                last.bark_windows + seq.bark_windows,
            )
        else:
            merged.append(seq)

    return merged
