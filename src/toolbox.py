from collections import defaultdict

from music21 import converter, corpus, instrument, midi, note, chord, pitch, stream, tempo
import numpy as np
import itertools as it

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


def get_entropy(file,track,meas_start,meas_end):
    total_entropy = 0
    for measure in range(meas_start,meas_end):
        total_entropy += get_entropy_from_measure(file,track,measure+1)
    return total_entropy

def get_entropy_from_measure(file,track,measure):
    E_p = get_pitches(file.measure(measure).parts[track])
    E_r = get_rhythm(file.measure(measure).parts[track])
    E_s = get_rests(file.measure(measure).parts[track])
    total_entropy = get_list_entropy(E_p) + get_list_entropy(E_r)+ get_list_entropy(E_s)
    return total_entropy


def measures_to_music(measure_list,M):
    new_piece = defaultdict(dict)
    for k,v in measure_list.items():
        for measure in v:
            for new_track in range(M):
                if new_piece[new_track].get(measure,-1) == -1:
                    new_piece[new_track][measure] = k
                    break
    for k,d in new_piece.items():
        new_piece[k] = dict(sorted(d.items()))
    return new_piece

def get_new_piece(file,solution, M):

    new_arrange = stream.Stream()
    stream_parts = [stream.Part(id = f"part{i}") for i in range(M)]

    #for a,b in it.product(file.parts[1].measure(1).getElementsByClass(tempo.MetronomeMark),stream_parts):
    #    b.append(a)
    for track, measure_list in solution.items():
        for m, orig_track in measure_list.items():
            if m!=0:
                #for element in file.parts[orig_track].measure(m): #.getElementsByClass(['Note', 'Rest']):
                stream_parts[track].append(file.parts[orig_track].getElementsByClass(stream.Measure)[m])
    #for i in range(M):
    new_arrange.insert(0, stream_parts[0])

    return new_arrange



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
