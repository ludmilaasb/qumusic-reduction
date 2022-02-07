from collections import defaultdict
from music21 import *

from qubo_form import max_num_measures


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
        notes = part.flat.getElementsByClass(['Note', 'Chord'])
        for n1, n2 in zip(notes, notes[1:]):
            rests[i].append((n2.offset) - (n1.offset + n1.duration.quarterLength)+1)
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
        if s!=0:
            slist = [r/s for r in slist]
        sdict[i] = slist
    return sdict

def get_measures(file, i):
    measures = []
    import math
    for n in file.parts[i].flat.getElementsByClass(['Note', 'Chord']):
        measures.append(math.ceil(n.offset / file.parts[0].measure(2).offset))
    return measures

def find_maxima(a,threshold):
    mlist = []
    for i in range(1,len(a)-1):
        if a[i]>a[i+1] and a[i-1]<a[i] and a[i]>threshold :
            mlist.append(i)
    return mlist

def find_maxima_measures(measures,mlist):
    meas_list = [0]
    if mlist!=[]:
        meas_list += [measures[m] for m in mlist]
    return meas_list


def get_phrase_list(file, p):
    no_parts = len(file.parts)

    pitch_int = get_pitch_int(file)
    rpitch = get_doc(no_parts, pitch_int)

    ioi = get_ioi(file)
    rioi = get_doc(no_parts, ioi)

    rests = get_rests(file)
    rrests = get_doc(no_parts, rests)

    spitch = get_strength(no_parts, pitch_int, rpitch)
    sioi = get_strength(no_parts, ioi, rioi)
    srests = get_strength(no_parts,rests,rrests)

    lbsp = [0] * no_parts
    max_measures = defaultdict(int)
    for i in range(no_parts):
        lbsp[i] = [0.25 * pitch + 0.5 * ioi + 0.25*rest for pitch, ioi,rest in zip(spitch[i], sioi[i],srests[i])]
        mlist = find_maxima(lbsp[i], p)
        measures = get_measures(file, i)
        max_measures[i] = find_maxima_measures(measures, mlist)
        max_measures[i].append(max_num_measures(file))

    return max_measures
