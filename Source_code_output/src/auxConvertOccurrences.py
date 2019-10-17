'''
Created on 20 nov. 2014

@author: thibautnicodeme

'''


from helpers import PATH_CSV, PATH_CORRECTED
from bookInputOutput import CSV_COMMA, ALT_COMMA

#Takes a csv file of occurrences and generates occurrences and a "clean" csv file.
#Compatible with both csv files generated from bookInputOutput and with its own output to re-load a clean file
#Error in occurence.csv could be line shifted by one column, number appearing on unused column... 
def generate_occurrences(occurrences_file):
    occurrences = {}
    StringBuilder = "Occurrence" + CSV_COMMA + "From" + CSV_COMMA + "To" + CSV_COMMA + "Sentiment" + CSV_COMMA + "Index" + CSV_COMMA + "Context"
    for l in occurrences_file.read().split("\n")[1:]:
        try:
            o = l.split(";")
        
            o_sentence = " , ".join(o[0:-5])
            o_from = o[-5]
            o_to = o[-4].split(",")
            if o_to[-1] == '':
                o_to = o_to[:-1]
            o_sentiment = float(o[-3])
            o_index = int(o[-2])
            o_context = int(o[-1])
        
        except Exception:
            print o

        occurrences[o_index] = {"sentence":o_sentence, "from":o_from, "to" : o_to, "context" : o_context}
        StringBuilder += "\n" + o_sentence + CSV_COMMA + o_from + CSV_COMMA + ALT_COMMA.join(o_to) + CSV_COMMA + str(o_sentiment) + CSV_COMMA + str(o_index) + CSV_COMMA + str(o_context)
    return occurrences, StringBuilder

#Generates a clean occurrences file for correction
def convert_occurrences_export(filename):
    occurrences_file = open(PATH_CSV + filename + "/occurrences_CID.csv", "r")
    StringBuilder = generate_occurrences(occurrences_file)[1]
    f = open(PATH_CSV+ filename + "/corrected_occurences_CID.csv","w+")
    f.write(StringBuilder)
    f.close()

if __name__ == '__main__':
    test_books = ["Harry_Potter_1"]
    for filename in test_books:
        convert_occurrences_export(filename)
