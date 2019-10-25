'''
Created on 27 janv. 2015

@author: thibautnicodeme
'''

from bookNetworkBuilding import build_inc_networks
from helpers import PATH_CSV, PATH_BOOKS
from bookInputOutput import get_files_in_folder, output_csv_graphs, CSV_COMMA
import os.path
import networkx as nx


#build incremental
def recover_context_networks (filename):
    folder= PATH_CSV+filename+"/Context/"
    contents = get_files_in_folder(folder)
    graphs = []
    nodeCount = {}
    for graph in contents:
        if "graph_context_" in graph:
            csv = open(folder+graph)
            new_graph = nx.Graph()
            for l in csv.read().decode("UTF-8").split("\n")[1:]:
                n = l.split(CSV_COMMA)
                if len(n) == 4:
                    new_graph.add_edge(n[0], n[1], weight=float(n[2]), mentions=int(n[3]))
            for n in new_graph.nodes():
                nodeCount[n] = nodeCount.get(n,0) + 1
            graphs.append(new_graph)
    return graphs, nodeCount

if __name__ == '__main__':
    files = get_files_in_folder(PATH_BOOKS)
    #series = ["Harry_Potter", "ASOIAF", "His_Dark_Materials", "TLC", "TLT", "TMI", "TRWC", "TWOT"]
    series = ["Harry_Potter"]
    for s in series:
        print("Series", s)
        graphs = []
        nodeCount = {}
        for f in files:
            if s in f:
                filename = f[:-4]
                print("Book", filename)
                my_graphs, my_nodeCount = recover_context_networks(filename)
                graphs.extend(my_graphs)
                for n in list(my_nodeCount.keys()):
                    if nodeCount.get(n,'') == '':
                        nodeCount[n] = my_nodeCount[n]
                    else:
                        nodeCount[n] += my_nodeCount[n]
                print("Book", filename, "done", len(my_graphs), len(graphs))
        iGraphs = build_inc_networks(graphs,nodeCount)
        print("Series incremental graphs done")
        directories = [PATH_CSV+s+"_series",PATH_CSV+s+"_series/Incremental/",]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
        output_csv_graphs(s+"_series",iGraphs,"Incremental")
