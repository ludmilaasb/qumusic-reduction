from collections import defaultdict

import neal
from dwave.system import LeapHybridSampler

from phrase_identification import get_phrase_list
from music21 import *
from pyqubo import Binary, Constraint
from toolbox import *


# TODO Should we udpate entropy function to give some bias to high pitch notes?
# TODO Same as above for measures with a single note?
# TODO Could not implement changing instruemnts
# TODO rests are not implemented in phrase identification
# TODO Check measure numbers, measures start from 1 in music21 I suppose
# TODO Boundaries should be checked: i.e. the first measure, last measure etc.
# TODO Check if phrases are iterated correctly, start-end measures, is/should start taken? is end taken? Again boundary conditions.
# TODO What if a phrase starts and ends in the same measure, we should check and avoid such situation
# TODO Make penalties parametrized as a dictionary
# TODO Write a function which identifies dissonant measures
# TODO Given that a track has a certain range of pitches, write a function which would identify invalid phrases for that track
# TODO Write a function to incorporate the above constraint


def get_objective(file, phrase_list, bias):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            o += -get_entropy(file, i, phrase_list[i][j], phrase_list[i][j + 1]) * Binary(f"x_{i}_{j}") * bias[i]
    return o


def phrase_measure_cons(file, phrase_list, p):
    no_parts = len(file.parts)
    o = 0
    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            for measure in range(phrase_list[i][j], phrase_list[i][j + 1]):
                o += Constraint(p * Binary(f"x_{i}_{j}") * (1 - Binary(f"m_{i}_{measure}")),
                                f"phrase_measure_{i}_{j}_{measure}")
                o += Constraint(p * (1 - Binary(f"x_{i}_{j}")) * Binary(f"m_{i}_{measure}"),
                                f"measure_phrase_{i}_{j}_{measure}")
    return o


def num_track_cons(file, M, p):
    no_parts = len(file.parts)
    num_measures = max_num_measures(file)
    c = 0
    for j in range(num_measures):
        c += Constraint(p * (M - sum(Binary(f"m_{i}_{j}") for i in range(no_parts))) ** 2, f"num_track_{j}")
    return c


def main_ins_cons(file, conf, p):
    # Suppose that we dont want violin 1 and violin 2 at the same time but at least 1 violin all the time
    num_measures = max_num_measures(file)
    c = 0
    for j in range(num_measures):
        c += Constraint(p * (1 - sum(Binary(f"m_{i}_{j}") for i in conf)) ** 2, f"main_ins_{j}")
    return c


def get_qubo(file, phrase_list, M, bias, p_dict):
    q = get_objective(file, phrase_list, bias)
    q += phrase_measure_cons(file, phrase_list, p_dict["phrase_measure"])
    q += num_track_cons(file,M,p_dict["num_track"])
    #q += main_ins_cons(file,[0,1], p_dict["main_ins"])
    return q
                         
                                                                                                            
def get_selected_measures(file, sample):
    no_parts = len(file.parts)
    num_measures = max_num_measures(file)
    measures_list = defaultdict(int)
    
    for i in range(no_parts):
        measures_list[i] = [j for j in range(num_measures) if sample[f"m_{i}_{j}"] == 1]
    return measures_list


def get_new_piece(file, solution, M):
    new_arrange = stream.Stream()
    stream_parts = [stream.Part(id=f"part{i}") for i in range(M)]

    for track, measure_list in solution.items():
        for m, orig_track in measure_list.items():
            if m != 18:
                stream_parts[track].append(file.parts[orig_track].getElementsByClass(stream.Measure)[m])
    for i in range(M):
        new_arrange.insert(0, stream_parts[i])
    return new_arrange


def measures_to_tracks(measure_list, M):
    tracks = defaultdict(dict)
    for k, v in measure_list.items():
        for measure in v:
            for new_track in range(M):
                if tracks[new_track].get(measure, -1) == -1:
                    tracks[new_track][measure] = k
                    break
    for k, d in tracks.items():
        tracks[k] = dict(sorted(d.items()))
    return tracks


def get_selected_phrases(file, sample, phrase_list):
    no_parts = len(file.parts)
    new_piece = []

    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            if sample.get(f"x_{i}_{j}", 0) == 1:
                new_piece.append((i, j))
    return new_piece

def anneal(qubo, mode):
    if mode == "sim":
        s = neal.SimulatedAnnealingSampler()
        sampleset = s.sample_qubo(qubo, num_reads=100)
        print(sampleset.first)
        sample = sampleset.first.sample
    elif mode == "hyb":
        sampler = LeapHybridSampler()
        sample = sampler.sample_qubo(qubo)
    return sample

def analyze_solution(model,sample):
    dec = model.decode_sample(sample, vartype='BINARY')
    print(dec.constraints(only_broken=True))

def sample_to_music(sample):
    selected_measures = get_selected_measures(file, sample)
    solution = measures_to_tracks(selected_measures)
    print(selected_measures)
    print(solution[0])
    print(solution[1])
    get_new_piece(file, solution, M).recurse().write("midi", "new_sym1.mid")
    # get_new_piece(file, solution, M).show('text')

if __name__ == "__main__":
    file_name = 'symphony.mid'
    file = converter.parse(file_name).measures(0, 40)

    phrase_list = get_phrase_list(file, 0.01)
    print("Phrase List", phrase_list)

    M = 2 #Number of tracks to reduce
    bias = [1] * len(file.parts)
    #bias[0] = 1.2
    #bias[1] = 1.3
    p_dict = {"phrase_measure":10, "num_track":5, "main_ins":0}
    H = get_qubo(file, phrase_list, M, bias, p_dict)
    model = H.compile()
    qubo, offset = model.to_qubo()
    mode = "sim"
    sample = anneal(qubo, mode)
    analyze_solution(model, sample)
    sample_to_music(sample)


