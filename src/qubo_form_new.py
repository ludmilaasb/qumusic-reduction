from collections import defaultdict
from pyqubo import Binary, Constraint
from toolbox import *

# TODO Identify same measures from different tracks and implement a constraint

# TODO Should we udpate entropy function to give some bias to high pitch notes?
# TODO Same as above for measures with a single note?
# TODO Could not implement changing instruemnts
# TODO Check measure numbers, measures start from 1 in music21 I suppose
# TODO Boundaries should be checked: i.e. the first measure, last measure etc.
# TODO Check if phrases are iterated correctly, start-end measures, is/should start taken? is end taken? Again boundary conditions.
# TODO Given that a track has a certain range of pitches, write a function which would identify invalid phrases for that track

# TODO Write a function which identifies dissonant measures
# TODO Write a function to incorporate the above constraint


def get_objective(file, phrase_list, bias):
    """Implements the objective part of the QUBO

    :param file: File to process
    :type file: music21 Stream
    :param phrase_list: List of start and end measures of phrases
    :type phrase_list: defaultdict
    :param bias: Bias for each instrument
    :type bias: list
    :return: pyqubo object corresponding to the objective function
    :rtype: cpp_pyqubo.Add
    """
    o = 0
    for i in range(len(file.parts)):
        for j in range(len(phrase_list[i]) - 1):
            o += (
                -get_entropy(file, i, phrase_list[i][j], phrase_list[i][j + 1])
                * Binary(f"x_{i}_{j}")
                * bias[i]
            )
    return o


def phrase_measure_cons(file, phrase_list, p):
    """Implements the constraint a phrase is selected iff corresponding measures are selected

    :param file: File to process
    :type file: music21 Stream
    :param phrase_list: List of start and end measures of phrases
    :type phrase_list: defaultdict
    :param p: Penalty value
    :type p: float
    :return: pyqubo object corresponding to the objective function
    :rtype: cpp_pyqubo.Add
    """

    c = 0
    for i in range(len(file.parts)):
        for j in range(len(phrase_list[i]) - 1):
            for measure in range(phrase_list[i][j], phrase_list[i][j + 1]):
                c += Constraint(
                    p * Binary(f"x_{i}_{j}") * (1 - Binary(f"m_{i}_{measure}")),
                    f"phrase_measure_{i}_{j}_{measure}",
                )
                c += Constraint(
                    p * (1 - Binary(f"x_{i}_{j}")) * Binary(f"m_{i}_{measure}"),
                    f"measure_phrase_{i}_{j}_{measure}",
                )
    return c


def num_track_cons(file, M, p):
    """Implements the number of tracks constraint, which ensures that there are M tracks after the reduction

    :param file: File to process
    :type file: music21 Stream
    :param M: Number of tracks after reduction
    :type M: int
    :param p: Penalty value
    :type p: float
    :return: pyqubo object corresponding to the objective function
    :rtype: cpp_pyqubo.Add
    """
    c = 0
    for j in range(max_num_measures(file)):
        c += Constraint(
            p * (M - sum(Binary(f"m_{i}_{j}") for i in range(len(file.parts)))) ** 2,
            f"num_track_{j}",
        )
    return c


def conf_ins_cons(file, conf_list, p):
    """This constraint make sures that conflicting instruments are not selected at the same time. For instance, two violins may not be desirable to selected at the same time for instance.

    :param file: File to process
    :type file: music21 Stream
    :param conf_list: List of conflicting pairs
    :type conf_list: list
    :param p: penalty
    :type p: float
    :return: pyqubo object corresponding to the objective function
    :rtype: cpp_pyqubo.Add
    """
    c = 0
    for nc, conf in enumerate(conf_list):
        for j in range(max_num_measures(file)):
            c += Constraint(
                p
                * (1 - sum(Binary(f"m_{i}_{j}") for i in conf) - Binary(f"s_{nc}_{j}"))
                ** 2,
                f"main_ins_{j}",
            )
    return c


def get_qubo(file, phrase_list, M, bias, conf_list, p_dict):
    """

    :param file: File to process
    :type file: music21 Stream
    :param phrase_list: List of start and end measures of phrases
    :type phrase_list: defaultdict
    :param M: Number of tracks to reduce
    :type M: int
    :param bias:Bias for the instruments
    :type bias: dict
    :param conf_list:
    :type conf_list:
    :param p_dict:
    :type p_dict:
    :return: QUBO formulation, the offset and the model
    :rtype: dict, float, cpp_pyqubo.Model
    """
    H = get_objective(file, phrase_list, bias)
    H += phrase_measure_cons(file, phrase_list, p_dict["phrase_measure"])
    H += num_track_cons(file, M, p_dict["num_track"])
    H += conf_ins_cons(file, conf_list, p_dict["main_ins"])

    model = H.compile()
    qubo, offset = model.to_qubo()
    return qubo, offset, model
