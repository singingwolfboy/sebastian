"""
This script will build up the first movement of Mozart's C major Sonata (K545)
while trying out experimental features of Sebastian.
"""
from pprint import pprint
from sebastian.core import Point, HSeq, VSeq, OSequence, DURATION_64
from sebastian.core.transforms import midi_pitch, degree_in_key_with_octave, add
from sebastian.core.notes import Key, major_scale
from sebastian.midi import write_midi


def sequence_map(key, elements):
    return HSeq({key: x} for x in elements)


def transpose_degree(point, degree_delta):
    result = Point(point)
    result["degree"] = result["degree"] + degree_delta
    return result


def chord(inversion=(0, 2, 4)):
    def _(point):
        result = point.copy()
        final_inversion = point.get("inversion", inversion)
        children = [transpose_degree(point, i) for i in final_inversion]
        result.update({"sequence": VSeq(children)})
        return result
    return _


def expand_sequences(points):
    result = []
    for point in points:
        result.extend(point["sequence"]._elements)
    return HSeq(result)


def alberti(vseq, duration):
    """
    takes a VSeq of 3 notes and returns an HSeq of those notes in an
    alberti figuration with each new note having the given duration.
    """
    return HSeq(vseq[i] for i in [0, 2, 1, 2]) | add(Point({DURATION_64: duration}))


def index(points):
    for i, p in enumerate(points):
        p["index"] = i
    return points


def build_movement():
    C_major = Key("C", major_scale)
    intervals = sequence_map("degree", [1, 5, 1, 4, 1, 5, 1])
    intervals[1]["inversion"] = (-3, -1, 0, 2)  # second inversion 7th
    intervals[3]["inversion"] = (-3, 0, 2)  # second inversion
    intervals[5]["inversion"] = (-5, -3, 0)  # first inversion
    rhythm = sequence_map(DURATION_64, [128, 64, 64, 64, 64, 64, 64])
    melody = intervals & rhythm
    melody = melody.map_points(chord())
    duration = 8
    for point in melody:
        point["sequence"] = alberti(point["sequence"], duration) * (point[DURATION_64] / (8 * duration))
    melody = expand_sequences(melody)

    # note values filled-out for C major in octave 5 then MIDI pitches calculated
    melody = melody | degree_in_key_with_octave(C_major, 5) | midi_pitch()

    melody = OSequence(melody)
    index(melody._elements)

    return melody

if __name__ == "__main__":
    movement = build_movement()
    for point in movement:
        pprint(point)
    write_midi.write("first_movement.mid", [movement])
