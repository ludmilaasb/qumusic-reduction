from pyqubo import Binary, Constraint
from toolbox import *

def max_num_measures(file):
    return max([len(p) for p in file.parts])

def qubo_form_from(file):
    H = 0
    for j in range(1,max_num_measures(file)):
        c = 0
        o = 0
        for i in range(len(file.parts)):
            if file.parts[i].measure(j) != None:
                c += Binary(f"x_{i}_{j}")
                o += get_entropy_from_measure(file,i,j)*Binary(f"x_{i}_{j}")
        H += Constraint((2-c)**2, f"measure_{j}") + o
    return H.compile().to_qubo()
