from experiment import *
from pyqubo.integer.log_encoded_integer import LogEncInteger 

np.random.seed(100)

class Job:
    count = 0
    def __init__(self, start, end, weight, id = -1):
        self.start = start
        self.end = end
        self.weight = weight
        if id == -1:
            self.id = Job.count
        else:
            self.id = id
        Job.count += 1
    def set_track(self,track):
        self.track = track
    def __repr__(self): 
        return  f"Job id no: {self.id}, start: {self.start}, end: {self.end}, weight:{self.weight} \n" 

def random_jobs(num_jobs,max_time,max_weight):
    rdm_jobs_list = []
    for i in range(num_jobs):
        start = np.random.randint(0,max_time)
        end = np.random.randint(start+1,max_time+1)
        weight = np.random.randint(1,max_weight+1)
        rdm_jobs_list.append(Job(start, end, weight, id = i))
    return rdm_jobs_list


def get_objective(job_list):
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
    for job in job_list:
        o += (-job.weight * Binary(f"x_{job.id}"))
    return o

def runing_jobs(job_list, t):
    run_jobs = []
    for job in job_list:
        if t > job.start and t <= job.end:
            run_jobs.append(job.id)
    return run_jobs
    
            

def num_machine_cons(M, job_list, max_time, p):
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
    for j in range(1,max_time+1):
        run_jobs = runing_jobs(job_list,j)
        if len(run_jobs) < 1:
            continue
        c += Constraint(
            p * (M - sum(Binary(f"x_{i}") for i in run_jobs)) ** 2,
            f"num_machine_{j}",
        )   
    return c

def min_idle_time_cons(M, job_list, max_time, p):
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
    for j in range(1,max_time+1):
        run_jobs = runing_jobs(job_list,j)
        if len(run_jobs) < 1:
            continue
        slack_var = LogEncInteger( f"slack{j}", (0, M)) 
        c += Constraint(
            p * (M - sum(Binary(f"x_{i}") for i in run_jobs)-slack_var) ** 2,
            f"min_idle{j}",
        )   
    return c

def get_qubo(job_list, M, max_time, p_dict):
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
    H = get_objective(job_list)
    H += num_machine_cons(M,job_list,max_time, p_dict["machine"])
    H += min_idle_time_cons(M,job_list,max_time, p_dict["idle"])

    model = H.compile()
    qubo, offset = model.to_qubo()
    return qubo, offset, model

if __name__ == "__main__":
    # job1 = Job(1,3,1,2)
    # print(job1)
    # job2 = Job(3,4,2,1)
    # job_list = [job1,job2]
    M = 1
    # p = 1
    max_time = 4

    job_list = random_jobs(5,max_time,4)

    print(job_list)
    p_dict = {"machine": 2, "idle": 1}
    mode = "sim"
    # # print(get_objective(job_list)) ok
    # # print(num_machine_cons(M, job_list, max_time, p)) ok
    # # print(min_idle_time_cons(M, job_list, max_time, p)) ok

    qubo,_,model = get_qubo(job_list,M,max_time,p_dict)
    sampleset = anneal(qubo, mode)
    sample = sampleset.first.sample
    print("this is the sample", sample,"\n")
    
    analyze_solution(model, sample)