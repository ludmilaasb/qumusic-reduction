from music21 import converter, corpus, instrument, midi, note, chord, pitch
import sys
import numpy as np

# ipt = sys.argv[1]

# for non-numpy array
# import collections, numpy
# a = numpy.array([0, 3, 0, 1, 0, 1, 2, 1, 0, 0, 0, 0, 1, 3, 4])
# collections.Counter(a)
# Counter({0: 7, 1: 4, 3: 2, 2: 1, 4: 1})

file = converter.parse('stalker.mid')
# print('This file contains %d tracks'%len(file))

def get_pitches(phrase):
    pitches_list = []
    for nt in phrase.flat.getElementsByClass(['Note','Chord']):
        pitches_list.append(nt.pitches[-1].ps)
    return pitches_list

def get_rests(phrase):
    rest_list = []
    for nt in phrase.flat.getElementsByClass(['Rest']):
        print(nt.offset)
        rest_list.append(nt.duration.quarterLength/4)
    return rest_list

def get_rhythm(phrase):
    rhythm_list = []
    count = 0
    for nt in file[1].measures(1,7).flat.getElementsByClass(['Note','Chord','Rest']):
        print(nt)
        if nt.isRest:
            count+= nt.duration.quarterLength/4
        if nt.isRest == False and count >= 0:
            rhythm_list.append(count)
            count = 0
    return rhythm_list

def get_list_entropy(a_list):
    unique,counts = np.unique(a_list,return_counts=True)
    # dict(zip(unique, counts/num_pitches))
    list_entropy = sum([-p*np.log(p) for p in counts/len(a_list)])
    return list_entropy





if __name__ == "__main__":
    phrase = file[0].measures(1,7)
    print(get_pitches(phrase))
    print(get_rests(phrase))
    print(get_pitch_entropy(phrase))
    print(phrase.show('text'))
