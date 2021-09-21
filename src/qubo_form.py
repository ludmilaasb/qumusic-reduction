from pyqubo import Binary, Constraint
from toolbox import *



def max_num_measures(file):
    return max([len(p) for p in file.parts])


def add_measurecountrains_from(file):
    H = 0
    for j in range(50,max_num_measures(file)):
        c = 0
        for i in range(len(file.parts)):
#             print(i,j, file.measure(j).parts[i])
            if file.parts[i].measure(j) != None:
                c += Binary(f"x_{i}_{j}")
        H += Constraint((2-c)**2, f"measure_{j}")
    return H
