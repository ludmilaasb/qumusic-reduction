import neal
from dwave.system import LeapHybridSampler

from check_results import *
from phrase_identification import get_phrase_list
from process_results import *

def anneal(qubo, mode):
    ''' Runs the annealing experiment

    :param qubo: QUBO formulation for the problem
    :type qubo: dict
    :param mode: Type of the experiment
    :type mode: string
    :return: Sampleset obtained
    :rtype: dimod.SampleSet
    '''
    if mode == "sim":
        sampler = neal.SimulatedAnnealingSampler()
        sampleset = sampler.sample_qubo(qubo, num_reads=1000,num_sweeps=4000)
    elif mode == "hyb":
        sampler = LeapHybridSampler()
        sampleset = sampler.sample_qubo(qubo)
    return sampleset

def run_experiment(mode,file,M,bias,p_dict,conf_list, longest_phrase, new_filename):
    phrase_list = get_phrase_list(file, longest_phrase, {"p": 0.25, "i": 0.5, "r": 0.25})
    print("Phrase List", phrase_list)
    qubo, offset, model = get_qubo(file, phrase_list, M, bias, conf_list, p_dict)
    print(type(model))
    sampleset = anneal(qubo, mode)
    sample = sampleset.first.sample
    analyze_solution(model, sample)
    sample_to_midi(file, sample, M, new_filename) 

if __name__ == "__main__":
    file_name = 'bach-air-score.mid'
    file = converter.parse(file_name).measures(0, 40).stripTies()
    M = 1 #Number of tracks to reduce
    bias = [1] * len(file.parts)
    bias[1] = 20
    bias[0] = 20
    p_dict = {"phrase_measure":50, "num_track":50, "conf_ins":5}
    conf_list = []
    mode = "sim"

    longest_phrase = 4

    run_experiment(mode, file, M, bias, p_dict, conf_list, longest_phrase,'new_bach555')

