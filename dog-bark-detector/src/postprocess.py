"""Applica le regole di padding e merge alle sequenze di abbaio rilevate."""

from dataclasses import dataclass


@dataclass
class Sequence:
    start: float
    end: float
    bark_count: int
    bark_starts: list


def merge_and_pad(candidates, gap_threshold_s=5.0, padding_s=3.0, duration_s=None):
    if not candidates:
        return []

    events = sorted(candidates, key=lambda c: c.start)

    sequences = []
    current_start = events[0].start
    current_end = events[0].end
    current_barks = [events[0].start]

    for event in events[1:]:
        if event.start - current_end < gap_threshold_s:
            current_end = max(current_end, event.end)
            current_barks.append(event.start)
        else:
            sequences.append((current_start, current_end, current_barks))
            current_start, current_end = event.start, event.end
            current_barks = [event.start]
    sequences.append((current_start, current_end, current_barks))

    padded = []
    for start, end, barks in sequences:
        padded_start = max(0.0, start - padding_s)
        padded_end = end + padding_s
        if duration_s is not None:
            padded_end = min(duration_s, padded_end)
        padded.append(Sequence(padded_start, padded_end, len(barks), barks))

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
                last.bark_starts + seq.bark_starts,
            )
        else:
            merged.append(seq)

    return merged
