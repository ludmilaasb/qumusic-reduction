from jobs_to_qubo import *

def phrase_to_jobs(phrase_list,file):
    job_list = []
    for track,value in phrase_list.items():
        for phrase in value:
            job = Job(phrase[0]-1,phrase[1],get_entropy(file,track,phrase[0],phrase[1]))
            job.set_track(track)
            job_list.append(job)
    return job_list



# def machines_to_tracks(machine_dict,file):


if __name__ == "__main__":
    file_name = 'bach-air-score.mid'
    file = converter.parse(file_name).measures(0, 40).stripTies()
    longest_phrase = 4


    M = 2
    max_time = 30
    phrase_list = get_phrase_list(file,longest_phrase,{"p": 0.25, "i": 0.5, "r": 0.25})
    p_dict = {"machine": 2, "idle": 1}
    mode = "sim"
    job_list = phrase_to_jobs(phrase_list,file)
    qubo,_,model = get_qubo(job_list,M,max_time,p_dict)
    sampleset = anneal(qubo, mode)
    sample = sampleset.first.sample
    print("this is the sample", sample,"\n")
    
    analyze_solution(model, sample)
    
    new_jobs = sample_to_jobs(sample,job_list)
    # print(new_jobs)

    for job in new_jobs:
        print(job,job.track)

    sorted_jobs = sort_jobs(new_jobs)
    machine_jobs = greddy_machines(M,sorted_jobs)

    print(machine_jobs)