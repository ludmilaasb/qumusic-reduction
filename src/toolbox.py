from music21 import converter, corpus, instrument, midi, note, chord, pitch
import sys

# ipt = sys.argv[1]

file = converter.parse('stalker.mid')
# print('This file contains %d tracks'%len(file))

def get_pitches(phrase):
    notes_list = []
    for nt in phrase.flat.getElementsByClass(['Note','Chord']):
        notes_list.append(nt.pitches[-1].ps)

    return notes_list
def get_rests(phrase):
    rest_list = []
    for nt in phrase.flat.getElementsByClass(['Rest']):
        print(nt.offset)
        rest_list.append(nt.duration.quarterLength/4)

    return rest_list
phrase = file[0].measures(1,7)
print(get_pitches(phrase))
print(get_rests(phrase))
print(phrase.show('text'))
    # print(measure.notes)
    # print(getnotes(measure))
#
# song_features_dict = {}
# for i,part in file:
#     song_features_dict[part.name] = {}
#     for k,measure in enumerate(part.measure):
#         song_features_dict[part.name][k] = getnotes(measure)
