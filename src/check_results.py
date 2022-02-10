def get_selected_phrases(file, sample, phrase_list):
    no_parts = len(file.parts)
    new_piece = []

    for i in range(no_parts):
        for j in range(len(phrase_list[i]) - 1):
            if sample.get(f"x_{i}_{j}", 0) == 1:
                new_piece.append((i, j))
    return new_piece

def analyze_solution(model,sample):
    dec = model.decode_sample(sample, vartype='BINARY')
    print(dec.constraints(only_broken=True))