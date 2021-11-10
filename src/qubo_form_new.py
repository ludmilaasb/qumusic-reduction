from collections import defaultdict

import neal

from phrase_identification import get_phrase_list
from music21 import *
from pyqubo import Binary, Constraint

from qubo_form import max_num_measures
from toolbox import get_entropy, measures_to_music, get_new_piece

#TODO Should we udpate entropy function to give some bias to high pitch notes?
#TODO Same as above for measures with a single note?
#TODO Could not implement changing instruemnts
#TODO rests are not implemented in phrase identification
#TODO Check measure numbers, measures start from 1 in music21 I suppose
#TODO Boundaries should be checked: i.e. the first measure, last measure etc.
#TODO Check if phrases are iterated correctly, start-end measures, is/should start taken? is end taken? Again boundary conditions.
#TODO What if a phrase starts and ends in the same measure, we should check and avoid such situation
#TODO Make penalties parametrized as a dictionary
#TODO Write a function which identifies dissonant measures
#TODO Given that a track has a certain range of pitches, write a function which would identify invalid phrases for that track
#TODO Write a function to incorporate the above constraint


def get_objective(file,phrase_list):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        bias = 1
        if i == 0:
            bias = 1.7
        elif i == 1:
            bias = 1.2
        for j in range(len(phrase_list[i])-1):
            o += -get_entropy(file,i,phrase_list[i][j],phrase_list[i][j+1])*Binary(f"x_{i}_{j}")*bias
    return o

def add_phrase_measure_cons(file,phrase_list):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            for measure in range(phrase_list[i][j],phrase_list[i][j+1]):
                o += 10*Binary(f"x_{i}_{j}")*(1-Binary(f"m_{i}_{measure}"))
    return o

def add_track_cons(file,M):
    no_parts = len(file.parts)
    num_measures = max_num_measures(file)
    c=0
    for j in range(num_measures) :
       c+= Constraint(10*(M-sum(Binary(f"m_{i}_{j}") for i in range(no_parts)))**2, f"measure_{j}")
    return c

def get_qubo(file,phrase_list,M):
    return get_objective(file, phrase_list) + add_phrase_measure_cons(file, phrase_list) + add_track_cons(file, M)

def get_selected_measures(file,sample):
    no_parts = len(file.parts)
    num_measures = max_num_measures(file)
    new_piece = defaultdict(int)

    for i in range(no_parts):
        new_piece[i] = [j for j in  range(num_measures) if sample[f"m_{i}_{j}"]==1]
    return new_piece

if __name__ == "__main__":
    file_name = 'bach-air-score.mid'
    file = converter.parse(file_name)
    phrase_list = get_phrase_list(file)
    M = 2
    H = get_qubo(file,phrase_list,M)
    qubo, offset = H.compile().to_qubo()

    s = neal.SimulatedAnnealingSampler()
    sampleset = s.sample_qubo(qubo, num_reads=100)
    print(sampleset.first)
    sample = sampleset.first.sample
    print("offset", offset)
    print(get_selected_measures(file,sample))
    print(phrase_list)

    solution = measures_to_music(get_selected_measures(file,sample), M)
    print(solution)
    get_new_piece(file, solution, M).show('text')
    get_new_piece(file,solution, M).recurse().write("midi", "new_music.mid")

