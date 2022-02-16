from collections import defaultdict

from music21 import converter, corpus, instrument, midi, note, chord, pitch, stream, tempo
import numpy as np
import itertools as it

def get_pitches(phrase):
    pitches_list = []
    for nt in phrase.flat.getElementsByClass(['Note','Chord']):
        pitches_list.append(nt.pitches[-1].ps)
    return pitches_list

def get_ioi_list(phrase): 
    ioi_list = []
    notes = phrase.flat.getElementsByClass(["Note", "Chord"])
    for n1, n2 in zip(notes, notes[1:]):
        ioi_list.append(n2.offset - n1.offset)
    return ioi_list

def get_list_entropy(a_list):
    unique,counts = np.unique(a_list,return_counts=True)
    # dict(zip(unique, counts/num_pitches))
    list_entropy = sum([-p*np.log(p) for p in counts/len(a_list)])
    return list_entropy

def get_entropy(file,track,meas_start,meas_end):
    total_entropy = 0
    file = file.stripTies()
    E_p = get_pitches(file.parts[track].measures(meas_start,meas_end).flat)
    E_ioi = get_ioi_list(file.parts[track].measures(meas_start,meas_end).flat)
    total_entropy = get_list_entropy(E_p) + get_list_entropy(E_ioi)
    return total_entropy

def get_entropy_from_measure(file,track,measure):
    E_p = get_pitches(file.measure(measure).parts[track])
    E_r = get_rhythm(file.measure(measure).parts[track])
    E_s = get_rests(file.measure(measure).parts[track])
    total_entropy = get_list_entropy(E_p) + get_list_entropy(E_r)+ get_list_entropy(E_s)
    return total_entropy



def max_num_measures(file):
    return max([len(p) for p in file.parts])


if __name__ == "__main__":
    file_name = 'bach-air-score.mid'

    file = converter.parse(file_name)

    #phrase = file[1].measures(1,7)
    #print(get_pitches(phrase),get_list_entropy(get_pitches(phrase)))
    #print(get_rests(phrase),get_list_entropy(get_rests(phrase)))
    #print(get_rhythm(phrase),get_list_entropy(get_rhythm(phrase)))
    #print(phrase.show('text'))

    print(get_entropy_from_measure(file, 0, 2))
    print(get_entropy(file, 0,0, 2))
