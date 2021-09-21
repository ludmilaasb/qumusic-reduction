from music21 import converter, corpus, instrument, midi, note, chord, pitch
import numpy as np

def get_pitches(phrase):
    pitches_list = []
    for nt in phrase.flat.getElementsByClass(['Note','Chord']):
        pitches_list.append(nt.pitches[-1].ps)
    return pitches_list

def get_rests(phrase):
    rest_list = []
    for nt in phrase.flat.getElementsByClass(['Rest']):
        rest_list.append(nt.duration.quarterLength/4)
    return rest_list

def get_rhythm(phrase):
    rhythm_list = []
    count = 0
    for nt in phrase.flat.getElementsByClass(['Note','Chord','Rest']):
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

def get_entropy_from_measure(file,track,measure):
    E_p = get_pitches(file.measure(measure).parts[track])
    E_r = get_rhythm(file.measure(measure).parts[track])
    E_s = get_rests(file.measure(measure).parts[track])
    total_entropy = get_list_entropy(E_p) + get_list_entropy(E_r)+ get_list_entropy(E_s)
    return total_entropy

if __name__ == "__main__":
    file = converter.parse('stalker.mid')

    phrase = file[1].measures(1,7)
    print(get_pitches(phrase),get_list_entropy(get_pitches(phrase)))
    print(get_rests(phrase),get_list_entropy(get_rests(phrase)))
    print(get_rhythm(phrase),get_list_entropy(get_rhythm(phrase)))
    print(phrase.show('text'))
