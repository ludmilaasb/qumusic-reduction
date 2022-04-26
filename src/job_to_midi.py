from jobs_to_qubo import *

def phrase_to_jobs(phrase_list,file):
    job_list = []
    for track,value in phrase_list.items():
        for phrase in value:
            job = Job(phrase[0]-1,phrase[1],get_entropy(file,track,phrase[0],phrase[1]))
            job.set_track(track)
            job_list.append(job)
    return job_list

def sample_to_jobs(sample,job_list):
    new_list = []
    for job in job_list:
        if sample[f"x_{job.id}"] == 1:
            new_list.append(job)
    return new_list

def sort_jobs(jobs_list):
    return sorted(jobs_list, key=lambda x: x.end, reverse=False) 

def greddy_machines(M,job_list):
    machines_dict = {i:[] for i in range(M)}
    for job in job_list:
        for m in range(M):
            try:
                if job.start >= machines_dict[m][-1].end:
                    machines_dict[m].append(job)
                    break
            except IndexError:
                print("list is empty")
                machines_dict[m].append(job)
                break
    return machines_dict

def machines_to_tracks(machine_dict,file):
    new_arrange = stream.Score()
    stream_parts = [stream.Part(id=f"part{i}") for i in range(len(machine_dict))]
    for machine,jobs in machine_dict.items():
        for job in jobs:
            stream_parts[machine].append(file.parts[job.track].measures(job.start+1,job.end))
    for i in range(len(machine_dict)):
        new_arrange.insert(0, stream_parts[i])
    print(new_arrange)
    # print(len(new_arrange))
    return new_arrange 

def store_midi(new_arrange,filename):
    return new_arrange.write("midi", f"{filename}.mid")



if __name__ == "__main__":
    file_name = 'bach-air-score.mid'
    file = converter.parse(file_name).measures(0, 40).stripTies()
    longest_phrase = 4
    filename = "bach-air-new"

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
    new_arrange = machines_to_tracks(machine_jobs,file)
    store_midi(new_arrange,filename)
    # print(machine_jobs)