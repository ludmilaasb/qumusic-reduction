from collections import defaultdict

import neal

from phrase_identification import get_phrase_list
from music21 import *
from pyqubo import Binary, Constraint

from qubo_form import max_num_measures
from toolbox import get_entropy


def get_objective(file,phrase_list):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        for j in range(len(phrase_list[i])-1):
            o += -get_entropy(file,i,phrase_list[i][j],phrase_list[i][j+1])*Binary(f"x_{i}_{j}")
    return o

def add_phrase_measure_cons(file,phrase_list):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            for measure in range(phrase_list[i][j],phrase_list[i][j+1]):
                o += Binary(f"x_{i}_{j}")*(1-Binary(f"m_{i}_{measure}"))
    return o

def add_track_cons(file,M):
    no_parts = len(file.parts)
    num_measures = max_num_measures(file)
    c=0
    for j in range(num_measures) :
       c+= Constraint((M-sum(Binary(f"m_{i}_{j}") for i in range(no_parts)))**2, f"measure_{j}")
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

def get_selected_phrases(file,sample,phrase_list):
    no_parts = len(file.parts)
    new_piece = defaultdict(int)

    for i in range(no_parts):
        new_piece[i] = [j for j in  range(len(phrase_list)) if sample[f"x_{i}_{j}"]==1]
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
    print(get_selected_phrases(file,sample,phrase_list))
