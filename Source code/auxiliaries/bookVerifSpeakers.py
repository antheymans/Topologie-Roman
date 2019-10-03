'''
Created on 26 janv. 2015

@author: thibautnicodeme
'''

from helpers import PATH_CSV, PATH_CORRECTED
from ConvertOccurrences import generate_occurrences

#Compares the CSV output for a filename and the corrected_occurrences for the same filename
def compare_occurrences(filename):
    occurrences_file = open(PATH_CSV + filename + "/occurrences_CID.csv", "r")
    o = generate_occurrences(occurrences_file)[0]
    corrected_file = open(PATH_CORRECTED+filename+".csv","r")
    oc = generate_occurrences(corrected_file)[0]
    indices = oc.keys()
    len_from = len(indices)
    correct_from = 0
    
    current_context = 0
    context_speakers = []
    correct_speakers = []
    conversation_speakers = 0
    conversation_correct = 0
    for index in indices:
        oi = o[index]
        oci = oc[index]
        if current_context != oci["context"]:
            current_context += 1
            for s in correct_speakers:
                conversation_speakers += 1
                if s in context_speakers:
                    conversation_correct += 1
            context_speakers = []
            correct_speakers = []
            
        if oci["from"] == "":
            len_from -= 1
        else:
            if oci['from'] not in correct_speakers:
                correct_speakers.append(oci['from'])
            if oi['from'] not in context_speakers and oi['from'] != "":
                context_speakers.append(oi['from'])
            if oi["from"] == oci["from"]:
                correct_from += 1
    print "Correct speaker identification:",float(correct_from)/len_from, correct_from, len_from
    print "Conversation speaker identification:",float(conversation_correct)/float(conversation_speakers),conversation_correct,conversation_speakers

if __name__ == '__main__':
    test_books = ["Harry_Potter_1"]
    for filename in test_books:
        compare_occurrences(filename)