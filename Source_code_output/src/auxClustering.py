'''
@author: thibautnicodeme
'''

from bookInputOutput import get_files_in_folder, CSV_COMMA, get_object
from helpers import PATH_CSV, PATH_BOOKS_OBJECT, PATH_SERIALIZED, PATH_PNG
import os.path
import numpy as np
import scipy.cluster.hierarchy as hac
import scipy.cluster.vq as vq
from scipy.cluster.hierarchy import dendrogram, fcluster
import pylab


## Objective not defined by first author
## degree csv file does not exist
## library scipy cause issue

def get_threshold(filename):
    frequencies = open(PATH_CSV+filename+"/frequencies.csv","r")
    firstline = frequencies.readline().decode("UTF-8")
    return firstline[28:-1]

def get_rates():
    resfilename = PATH_SERIALIZED+"speakerIDstats.txt"
    if os.path.isfile(resfilename):
        resfile = get_object(resfilename)
    return resfile

def get_clustering(filename):
    clustering_file = open(PATH_CSV+filename+"/clustering_incremental.csv","r").read().decode("UTF-8").split("\n")
    return clustering_file[-2].split(CSV_COMMA)[1]
    
def get_degrees():#graph_degrees or degrees_exponents ? bug
    degrees_files = open(PATH_CSV+"graph_degrees.csv","r").read().decode("UTF_8").split("\n")
    degrees_exponents = {}
    for line in degrees_files:
        if line != "":
            splitline = line.split(CSV_COMMA)
            degrees_exponents[splitline[0]]=splitline[1]
    return degrees_exponents

def make_cluster_hier(bookarray, books_labels):
    methods = ["single", "complete","average","weighted","centroid","median","ward"]
    for method in methods:
        booklinkage =  hac.linkage(bookarray,method=method)
        dendrogram(booklinkage, labels = books_labels, leaf_font_size=5)
        pylab.savefig(PATH_PNG+"dendrogram_"+method+".png")
        pylab.clf()
    
def make_cluster_kmean(bookarray, books_labels):
    kmeans_tests = {}
    for k in range(2,15):
        kmeans = vq.kmeans2(bookarray, k)
        
        kmeans_res = []
        for i in range(len(books_labels)):
            kmeans_res.append([books_labels[i],kmeans[1][i]])
        
        good_cluster = [ (kmeans_res[i][0][:-2] != kmeans_res[j][0][:-2]) ^ (kmeans_res[i][1] == kmeans_res[j][1]) for i in range(len(kmeans_res)) for j in range(i+1,len(kmeans_res))]
        ksum =  sum(good_cluster)
        klen =  len(good_cluster)
        kmeans_tests[k] = [float(ksum)/float(klen), kmeans]
        print(k, float(ksum)/float(klen))
    classifier= kmeans_tests[10][1][1]
    classes= {}
    for i in range(len(classifier)):
        classes[classifier[i]] = classes.get(classifier[i],[])
        classes[classifier[i]].append(books_labels[i])
    print(classes)

def make_cluster(signature, withdegrees):
    books = []
    books_labels=[]
    for book in list(signature.keys()):
        books_labels.append(book)
        if withdegrees:
            books.append([float(signature[book]["Threshold"]),float(signature[book]["SIR"]),float(signature[book]["Clustering"]),float(signature[book]["Degree"])])
        else:
            books.append([float(signature[book]["Threshold"]),float(signature[book]["SIR"]),float(signature[book]["Clustering"])])
    
    bookarray = np.array(books)
    for i in range(bookarray.shape[1]):
        bookarray[:,i] /= bookarray.max(axis=0)[i]
    
    make_cluster_hier(bookarray, books_labels)
    #make_cluster_kmean(bookarray, books_labels)

def export_signature_table(signature):
    csv = "Book" + CSV_COMMA + "Threshold" + CSV_COMMA + "SIR" + CSV_COMMA + "Clustering" + CSV_COMMA + "Degree" + "\n"
    for book in list(signature.keys()):
        csv += book + CSV_COMMA + str(signature[book]["Threshold"]) + CSV_COMMA + str(signature[book]["SIR"]) + CSV_COMMA 
        csv += str(signature[book]["Clustering"]) + CSV_COMMA + "\n" # + str(signature[book]["Degree"]) ADD BEFORE \N
    f = open(PATH_CSV+"signatures.csv","w+")
    f.write(csv)
    f.close()

if __name__ == '__main__':
    signature = {}
    speaker_rates = get_rates()
    #degrees = get_degrees()
    for book_file in get_files_in_folder(PATH_BOOKS_OBJECT):
        filename = book_file[:-5]
        signature[filename] = {"Threshold":get_threshold(filename),"SIR":speaker_rates[filename], "Clustering": get_clustering(filename)#, "Degree": degrees.get(filename,u"N/A")#
                                }
    make_cluster(signature, False)
    export_signature_table(signature)