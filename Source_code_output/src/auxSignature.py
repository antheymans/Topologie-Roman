'''
@author: thibautnicodeme
'''

from bookInputOutput import get_files_in_folder, CSV_COMMA, get_object
from helpers import PATH_CSV, PATH_BOOKS_OBJECT, PATH_SERIALIZED, PATH_PNG, PATH_GRAPHS

import os.path
import numpy as np
import scipy.cluster.hierarchy as hac
import scipy.cluster.vq as vq
from scipy.cluster.hierarchy import dendrogram, fcluster
import pylab
import networkx as nx

## Objective not defined by first author
## degree csv file does not exist
## library scipy cause issue

def get_threshold(filename):
    frequencies = open(PATH_CSV+filename+"/frequencies.csv","r")
    firstline = frequencies.readline()
    return firstline[28:-1]

def get_rates():
    resfilename = PATH_SERIALIZED+"speakerIDstats.txt"
    if os.path.isfile(resfilename):
        resfile = get_object(resfilename)
    return resfile

def get_clustering(filename):
    clustering_file = open(PATH_CSV+filename+"/clustering_incremental.csv","r").read().split("\n")
    return clustering_file[-2].split(CSV_COMMA)[1]

def get_graph(filename):
    return nx.read_gexf(PATH_GRAPHS+filename+".gexf")
   
def get_clustering_from_graph(G):
    return nx.average_clustering(G)

def get_transitivity_from_graph(G): #transitivity = general clustering
    return nx.transitivity(G)

def get_length_from_graph(G):
    return G.size()

def get_average_degree_from_graph(G):
    return (2*G.size())/len(G)
    
##Non functionning    
def get_degree(filename):#graph_degrees or degrees_exponents ? bug
    degrees_files = open(PATH_CSV+filename+"/graph_degrees.csv","r").read().split("\n")
    degree = {}
    for line in degrees_files[1:]:
        if line != "":
            splitline = line.split(CSV_COMMA)
            degree[splitline[0]]=int(splitline[1])
    return degree


def averaging_degree(degree):
    average_degree = 0.0
    for value in degree.values():
         average_degree += value
    #print(average_degree,len(degree))
    average_degree /= len(degree)
    return average_degree
    
    
    
def get_average_degree(filename):
    degrees_file = open(PATH_CSV+filename+"/graph_degrees.csv","r").read().split("\n")
    average_degree = 0.0
    value = 0
    for line in degrees_file[1:]:
        if line != "":
            value +=1
            splitline = line.split(CSV_COMMA)
            average_degree +=int(splitline[1])
    average_degree /= (len(degrees_file)-2)#-1 for "" line and -1 for title line
    return average_degree



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
    make_cluster_kmean(bookarray, books_labels)


            
def export_signature_table(signature):
    csv = "Book" + CSV_COMMA + "Threshold" + CSV_COMMA + "SIR" + CSV_COMMA + "Clustering" + CSV_COMMA +"Transitivity" + CSV_COMMA 
    csv += "Average Degree" + CSV_COMMA + "Graph Size" + CSV_COMMA + "\n"
    for book in list(signature.keys()):
        csv += book + CSV_COMMA + str(signature[book]["Threshold"]) + CSV_COMMA + str(signature[book]["SIR"]) + CSV_COMMA 
        csv += str(signature[book]["Clustering"]) + CSV_COMMA + str(signature[book]["Transitivity"]) + CSV_COMMA
        csv += str(signature[book]["Average Degree"]) + CSV_COMMA + str(signature[book]["Graph Size"]) + CSV_COMMA + "\n" 
    f = open(PATH_CSV+"signatures.csv","w+")
    f.write(csv)
    f.close()
  
def export_graph_signature_table(signature, filename):
    csv = "Book" + CSV_COMMA + "Clustering" + CSV_COMMA +"Transitivity" +  CSV_COMMA 
    csv += "Average Degree" + CSV_COMMA + "Graph Size" + CSV_COMMA + "\n"
    for book in list(signature.keys()):
        csv += book + CSV_COMMA + str(signature[book]["Clustering"]) + CSV_COMMA 
        csv += str(signature[book]["Transitivity"]) + CSV_COMMA + str(signature[book]["Average Degree"]) + CSV_COMMA
        csv += str(signature[book]["Graph Size"]) + CSV_COMMA + "\n" 
    f = open(PATH_CSV+ filename + ".csv","w+")
    f.write(csv)
    f.close()  

def get_signature(files):
    signature = {}
    signature_random_graph = {}
    signature_male_graph = {}
    signature_female_graph = {}
    signature_gendered_graph = {}
    speaker_rates = get_rates()
    for book_file in files:
        filename = book_file[:-5]
        #degree = get_degree(filename)
        graph = get_graph(filename)    
        graph_size = len(graph)
        graph_edge_size = graph.number_of_edges()
        male_graph = graph.subgraph([n for n, d in graph.nodes(data=True) if d['gender']==1])
        female_graph = graph.subgraph([n for n, d in graph.nodes(data=True) if d['gender']==-1])
        gendered_graph = graph.subgraph([n for n, d in graph.nodes(data=True) if d['gender']!=0])
        
        
        signature[filename] = {"Threshold":get_threshold(filename),"SIR":speaker_rates[filename], 
            "Clustering": get_clustering(filename),"Transitivity": get_transitivity_from_graph(graph),
            "Average Degree":get_average_degree(filename),"Graph Size": (len(graph), graph_edge_size) }
        

        
        random_graph = nx.fast_gnp_random_graph(graph_size, graph_edge_size * 2 /(graph_size * (graph_size -1))) #nbr edge among all existing edge 
        signature_random_graph[filename] = {"Clustering": get_clustering_from_graph(random_graph),"Transitivity": get_transitivity_from_graph(random_graph),
            "Average Degree":get_average_degree_from_graph(random_graph), "Graph Size": (len(random_graph), random_graph.number_of_edges()) }
        signature_male_graph[filename] = {"Clustering": get_clustering_from_graph(male_graph),"Transitivity": get_transitivity_from_graph(male_graph),
            "Average Degree":get_average_degree_from_graph(male_graph), "Graph Size": (len(male_graph), male_graph.number_of_edges()) }
        signature_female_graph[filename] = {"Clustering": get_clustering_from_graph(female_graph),"Transitivity": get_transitivity_from_graph(female_graph),
            "Average Degree":get_average_degree_from_graph(female_graph), "Graph Size": (len(female_graph), female_graph.number_of_edges()) }
        signature_gendered_graph[filename] = {"Clustering": get_clustering_from_graph(gendered_graph),"Transitivity": get_transitivity_from_graph(gendered_graph),
            "Average Degree":get_average_degree_from_graph(gendered_graph), "Graph Size": (len(gendered_graph), gendered_graph.number_of_edges()) }
    return signature, signature_random_graph, signature_male_graph, signature_female_graph, signature_gendered_graph
    
    
def main_signature(files):
    signature, random_signature, signature_male_graph, signature_female_graph,signature_gendered_graph = get_signature(files)
    export_signature_table(signature)
    export_graph_signature_table(random_signature, "random_graph_signatures")
    export_graph_signature_table(signature_male_graph, "male_graph_signatures")
    export_graph_signature_table(signature_female_graph, "female_graph_signatures")
    export_graph_signature_table(signature_gendered_graph, "gendered_graph_signatures")
    
if __name__ == '__main__':
    files = get_files_in_folder(PATH_BOOKS)
    main_signature(files)