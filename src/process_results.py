from qubo_form_new import *

def get_selected_measures(file, sample):
    ''' Given a sample, the selected measures, i.e. the variables corresponding to measures which are set to 1 are returned.

    :param file: File to process
    :type file: music21 Stream
    :param sample: A single sample obtained from D-Wave
    :type sample: dict
    :return: A dictionary of measures list selected for each part
    :rtype: defaultdict
    '''
    measures_list = defaultdict(int)

    for i in range(len(file.parts)):
        measures_list[i] = [j for j in range(max_num_measures(file)) if sample[f"m_{i}_{j}"] == 1]
    return measures_list

def measures_to_tracks(measure_list, M):
    ''' Assigns the given measures to the tracks

    :param measure_list: Selected measures from each part
    :type measure_list: defaultdict
    :param M: Number of tracks in the reduced music
    :type M: int
    :return: Information about which measure should be selected from which track
    :rtype: defaultdict
    '''
    tracks = defaultdict(dict)
    for p, measures in measure_list.items():
        for m in measures:
            for t in range(M):
                if tracks[t].get(m, -1) == -1: #If measure m of track t is empty
                    tracks[t][m] = p # Assign the m'th measure of part p to track t
                    break
    for t, d in tracks.items():
        tracks[t] = dict(sorted(d.items()))  #Sort by measures
    return tracks

def create_midi(file, tracks):
    '''
    
    :param file: File to process
    :type file: music21 Stream
    :param tracks: Information about which measure should be selected from which track
    :type tracks: defaultdict
    :return: New music file
    :rtype: music21 Stream
    '''
    M = len(tracks)
    new_arrange = stream.Stream()
    stream_parts = [stream.Part(id=f"part{i}") for i in range(M)]
    print("solution", tracks)
    for t, measure_list in tracks.items():
        for m, orig_track in measure_list.items():
            stream_parts[t].append(file.parts[orig_track].getElementsByClass(stream.Measure)[m])
    for i in range(M):
        new_arrange.insert(0, stream_parts[i])
    return new_arrange









def sample_to_music(file,sample,M,filename):
    selected_measures = get_selected_measures(file, sample)
    solution = measures_to_tracks(selected_measures,M)
    print(selected_measures)
    print(solution[0])
    print(solution[1])
    get_new_piece(file, solution, M).recurse().write("midi", f"{filename}.mid")
    # get_new_piece(file, solution, M).show('text')
