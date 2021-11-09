from collections import defaultdict
from music21 import *

def get_pitch_int(file):
    pitch_int = defaultdict(list)
    for i, part in enumerate(file.parts):
        for p1,p2 in zip(part.pitches, part.pitches[1:]):
            intvl = interval.Interval(p1,p2)
            pitch_int[i].append(abs(intvl.chromatic.semitones)+1)
    return pitch_int

def get_ioi(file):
    ioi = defaultdict(list)
    for i, part in enumerate(file.parts):
        notes = part.flat.getElementsByClass(['Note', 'Chord'])
        for n1, n2 in zip(notes, notes[1:]):
            ioi[i].append(n2.offset - n1.offset)
    return ioi

def get_rests(file):
    rests = defaultdict(list)
    for i, part in enumerate(file.parts):
        rs = part.flat.getElementsByClass(['Rest'])
        for rest in rs:
            rests[i].append(rest.duration.quarterLength)
    return rests

def get_doc(no_parts, intervals):
    rdict = defaultdict(lambda: [0])
    for i in range(no_parts):
        rdict[i] += [abs(int2-int1)/(int1+int2) for int1,int2 in zip(intervals[i],intervals[i][1:])]
    return rdict

def get_strength(no_parts,intervals,doc):
    sdict = defaultdict(list)
    for i in range(no_parts):
        slist = [intervals[i][j+1]*(doc[i][j]+doc[i][j+1]) for j in range(len(intervals[i])-1)]
        s = sum(slist)
        normed_s = [r/s for r in slist]
        sdict[i] = normed_s
    return sdict

def get_measures(file):
    measures = []
    import math
    for n in file.parts[0].flat.getElementsByClass(['Note', 'Chord']):
        measures.append(math.ceil(n.offset / 4))
    return measures

def find_maxima(a,threshold):
    mlist = []
    for i in range(1,len(a)-1):
        if a[i]>a[i+1] and a[i-1]<a[i] and a[i]>threshold :
            mlist.append(i)
    return mlist

def find_maxima_measures(measures,mlist):
    meas_list = [measures[m] for m in mlist]
    return meas_list


def get_phrase_list(file):
    no_parts = len(file.parts)

    pitch_int = get_pitch_int(file)
    rpitch = get_doc(no_parts, pitch_int)

    ioi = get_ioi(file)
    rioi = get_doc(no_parts, ioi)

    spitch = get_strength(no_parts, pitch_int, rpitch)
    sioi = get_strength(no_parts, ioi, rioi)

    lbsp = [0] * no_parts
    max_measures = defaultdict(int)
    for i in range(no_parts):
        lbsp[i] = [0.25 * pitch + 0.75 * ioi for pitch, ioi in zip(spitch[i], sioi[i])]
        mlist = find_maxima(lbsp[i], 0.02)
        measures = get_measures(file)
        max_measures[i] = find_maxima_measures(measures, mlist)

    return max_measures