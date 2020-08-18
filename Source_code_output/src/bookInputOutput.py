#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

#Library handling all inputs and outputs

import pickle
import dill
import matplotlib.pyplot as plt
import networkx as nx
import json
from networkx.readwrite import json_graph
from networkx.algorithms.cluster import average_clustering
import os.path
import codecs

from helpers import PATH_BOOKS, PATH_BOOKS_OBJECT, PATH_GRAPHS, PATH_CSV, PATH_PNG, PATH_SERIALIZED
import bookPreProcessing as bPP

CSV_COMMA=";"
ALT_COMMA=","

###############################################################
# File reading methods
###############################################################

def get_files_in_folder(folder):
    """
    DESCRIPTION: Retrieve a (list) of the files present in a given folder (str).
    """
    liste = os.listdir(folder)
    files = []
    for l in liste:
        if l[0] != ".":
            files.append(l)
    return files

def load_book(filename):
    path = PATH_BOOKS_OBJECT+filename+".book"
    print(path)
    if os.path.isfile(path):
        print("FILE FOUND! Loading the collection...")
        book = get_object(path)
        print("Done !")
        return book
    else:
        print("NO FILE FOUND! Building the collection...")
        book = bPP.build_book(PATH_BOOKS+filename+".txt")        #book is: sentences, breaks, sentiments, chunks
        set_object(book, path)
        print("Done !")        
        return book


###############################################################
# Directory manipulation methods
###############################################################


def create_folders(filename):
    check_dir(PATH_SERIALIZED, PATH_BOOKS_OBJECT, PATH_GRAPHS)
    directories = [PATH_CSV+filename, PATH_CSV+filename+"/Context/", PATH_CSV+filename+"/Incremental/", 
                   PATH_PNG+filename, PATH_PNG+filename+"/CONTEXT/", PATH_PNG+filename+"/INCREMENTAL/"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def check_dir(path_serialized, path_book_object, path_graphs):
    if not os.path.exists(path_serialized): ##check that the directory exist before creating file
        print("NO SERIALIZED DIRECTORY FOUND! Creating the directory")
        os.makedirs(path_serialized) 
    if not os.path.exists(path_book_object): ##check that the directory exist before creating file
        print("NO BOOKS DIRECTORY FOUND! Creating the directory")
        os.makedirs(path_book_object) 
    if not os.path.exists(path_graphs): ##check that the directory exist before creating file
        print("NO GRAPH DIRECTORY FOUND! Creating the directory")
        os.makedirs(path_graphs) 
        
        
###############################################################
# Serialization methods
###############################################################

def set_object(o, filename):
    """
    Set an object to a file
    """
    if os.path.exists(filename):
        f = open(filename,'wb+')
    else:
        f = open(filename,'ab+')
    pickle.dump(o, f)
    print(("Object set in "+filename))#deb




def get_object(filename):
    """
    Retrieve an object from a file
    """
    f = open(filename, "rb")
    return pickle.load(f)

###############################################################
# Serialize and loading functions
###############################################################
def update_stats(name, stat):
    resfilename = PATH_SERIALIZED+"speakerIDstats"
    if os.path.isfile(resfilename):
        resfile = get_object(resfilename)
        resfile[name] = stat
        set_object(resfile,resfilename)
    else:
        resfile = {name:stat}
        set_object(resfile,resfilename)
    csv_dialog_extr_stats(resfile)

def update_stats_CID(name,stat):
    resfilename = PATH_SERIALIZED+"speakerIDstats_postCID"
    
    if os.path.isfile(resfilename):
        resfile = get_object(resfilename)
        resfile[name] = stat
        set_object(resfile,resfilename)
    else:
        resfile = {name:stat}
        set_object(resfile,resfilename)
    csv_dialog_extr_stats_CID(resfile)


def save_occurrences_contexts(filename,dialog_occurrences,dialog_contexts):
    set_object(dialog_occurrences, PATH_SERIALIZED+filename+"_occurrences")
    csv_occurrences(dialog_occurrences,filename)
    set_object(dialog_contexts, PATH_SERIALIZED+filename+"_contexts")
    csv_contexts(dialog_contexts,filename)
    
def save_occurrences_CID(filename, dialog_occurrences):
    set_object(dialog_occurrences, PATH_SERIALIZED+filename+"_occurrences_CID")
    csv_occurrences_CID(dialog_occurrences,filename)

def export_aliases(aliasTable, connectionsTable, aliases, filename):
    aliasfilename = PATH_SERIALIZED+filename+"_alias"
    set_object((aliasTable, connectionsTable, aliases),aliasfilename)
    csv_aliases(aliasTable, connectionsTable, aliases, filename)

def load_alias_table(previous_book):
    aliasfilename = PATH_SERIALIZED+previous_book+"_alias"
    if previous_book == "" or not os.path.isfile(aliasfilename):
        print("New alias table created.")
        return {},nx.Graph(), nx.DiGraph()
    print("File found.")
    aT, cT, aliases = get_object(aliasfilename)
    aliasTable = {key: [] for key in list(aT.keys())}
    connectionsTable = cT.copy()
    for e in list(connectionsTable.nodes(data=True)):
        e[2]['value'] = 0 
    return aliasTable, connectionsTable, aliases

###############################################################
# CSV builder functions
###############################################################

def build_csv_spacing_map(dialog_spacing,count,threshold,filename):  
    """
    Copy the spacing map generated during book analysis to a .csv file
    """
    spacing = "Dialog #"+CSV_COMMA+"Spacing (#Lines between two lines)\n"
    for s in dialog_spacing:
        spacing += str(s[0])+CSV_COMMA+str(s[1])+"\n"
    
    f1 = open(PATH_CSV+filename+"/spacing.csv","w+")
    f1.write(spacing)
    f1.close()

    frequency = "Spacing"+CSV_COMMA+"Frequency" + CSV_COMMA+"Threshold="+str(threshold)+"\n"
    max_spacing = max(count.keys())
    for s in range(0,max_spacing):
        frequency += str(s)+CSV_COMMA+str(count.get(s,0))+"\n"
    
    f2 = open(PATH_CSV+filename+"/frequencies.csv","w+")
    f2.write(frequency)
    f2.close()

def csv_dialog_extr_stats(resfile):
    idStats = "Book" + CSV_COMMA + "%ID\n"
    for b in list(resfile.keys()):
        idStats += b + CSV_COMMA + str(resfile[b]) + "\n"
    
    f = codecs.open(PATH_CSV + "speakerIDstats.csv", "w+", encoding='utf-8')
    f.write(idStats)
    f.close()

def csv_dialog_extr_stats_CID(resfile):
    idStats = "Book" + CSV_COMMA + "%ID\n"
    for b in list(resfile.keys()):
        idStats += b + CSV_COMMA + str(resfile[b]) + "\n"
    
    f = codecs.open(PATH_CSV + "speakerIDstats_postCID.csv", "w+", encoding='utf-8')
    
    f.write(idStats)
    f.close()

def csv_occurrences(dialog_occurrences,filename):
    do = "Occurrence" + CSV_COMMA + "From" + CSV_COMMA + "To" + CSV_COMMA + "Sentiment" + CSV_COMMA + "Index" + CSV_COMMA + "Context"
    for o in dialog_occurrences:
        do += "\n" + o['sentence'] + CSV_COMMA
        for f in o['from']:
            do += f + ALT_COMMA 
        do += CSV_COMMA 
        for t in o['to']:
            do += t + ALT_COMMA  
        do += CSV_COMMA + str(o['sentiment']) + CSV_COMMA + str(o['index']) + CSV_COMMA + str(o['context']) 
    
    f = codecs.open(PATH_CSV + filename+"/occurrences.csv", "wb+", encoding='utf-8')
    f.write(do)
    f.close()

def csv_occurrences_CID(dialog_occurrences,filename):
    do = "Occurrence" + CSV_COMMA + "From" + CSV_COMMA + "To" + CSV_COMMA + "Sentiment" + CSV_COMMA + "Index" + CSV_COMMA + "Context"
    for o in dialog_occurrences:
        do += "\n" + o['sentence'] + CSV_COMMA + o['from'] + CSV_COMMA 
        for t in o['to']:
            do += t + ALT_COMMA  
        do += CSV_COMMA + str(o['sentiment']) + CSV_COMMA + str(o['index']) + CSV_COMMA + str(o['context']) 
    
    f = codecs.open(PATH_CSV + filename+"/occurrences_CID.csv", "wb+", encoding='utf-8')
    f.write(do)
    f.close()

def csv_contexts(dialog_contexts,filename):
    dc = "Context" + CSV_COMMA + "Start" + CSV_COMMA + "End" + CSV_COMMA
    for c in range(len(dialog_contexts)):
        dc += "\n" + str(c) + CSV_COMMA + str(dialog_contexts[c][0]) + CSV_COMMA + str(dialog_contexts[c][1])
    f = open(PATH_CSV + filename+"/contexts.csv", "w+")
    f.write(dc)
    f.close()

def csv_aliases(aliasTable, connectionsTable, aliases, filename):
    alias_table_string = "Key"+CSV_COMMA+"Expressions"
    for key in list(aliasTable.keys()):
        alias_table_string+= "\n" + key
        for c in aliasTable[key]:
            alias_table_string += CSV_COMMA + c
            
    f1 = codecs.open(PATH_CSV + filename + "/alias_table.csv", "wb+", encoding='utf-8')
    f1.write(alias_table_string)
    f1.close()
    
    ct_string = "Name 1" + CSV_COMMA + "Length 1" + CSV_COMMA + "Gender 1" + CSV_COMMA + "Name 2" + CSV_COMMA + "Length 2" + CSV_COMMA + "Gender 2" + CSV_COMMA + "Paired"
    nodes = {n[0]: n[1] for n in connectionsTable.nodes(data=True)}
    for n in list(nodes.keys()):
        for end in list(connectionsTable[n].keys()):
            ct_string += "\n" + n + CSV_COMMA + str(nodes[n]["value"]) + CSV_COMMA + str(nodes[n]["gender"]) + CSV_COMMA + end + CSV_COMMA + str(nodes[end]["value"]) + CSV_COMMA + str(nodes[end]["gender"]) + CSV_COMMA + str(connectionsTable[n][end]["paired"])  
    
    f2 = codecs.open(PATH_CSV + filename + "/connection_table.csv", "wb+", encoding='utf-8')
    f2.write(ct_string)
    f2.close()
    
    alias_pairs_string = "Cluster mentions" + CSV_COMMA + "Gender" + CSV_COMMA +  "Main Name" + CSV_COMMA + "Other names" + "\n"
    for node in aliases.nodes():
        if list(aliases.successors(node)) == []:
            mentions = connectionsTable.nodes[node]["value"]
            cluster_string = str(connectionsTable.nodes[node]["gender"]) + CSV_COMMA + node
            for predecessor in aliases.predecessors(node):
                mentions += connectionsTable.nodes[predecessor]["value"]
                cluster_string += CSV_COMMA + predecessor
            alias_pairs_string += str(mentions) + CSV_COMMA + cluster_string + "\n" 
    f4 = codecs.open(PATH_CSV + filename + "/alias_cluster.csv", "wb+", encoding='utf-8')
    f4.write(alias_pairs_string)
    f4.close()
    
    name_string = "Canonical Name" + CSV_COMMA + "Honorifics" + CSV_COMMA + "Firstname" + CSV_COMMA + "MiddleName" + CSV_COMMA \
        + "LastName"  +  CSV_COMMA + "Name_category"  +  CSV_COMMA + "Gender" + CSV_COMMA + "Value"
    for node, data in connectionsTable.nodes(data = True):
        name_string += "\n" + node + CSV_COMMA + data["name"].title + CSV_COMMA + data["name"].first + CSV_COMMA +\
            data["name"].middle +\
            CSV_COMMA + data["name"].last +  \
            CSV_COMMA + str(data["name_category"]) + \
            CSV_COMMA + str(data["gender"]) + \
            CSV_COMMA + str(data["value"])
    f3 = codecs.open(PATH_CSV + filename + "/names.csv", "wb+", encoding='utf-8')
    f3.write(name_string)

def csv_degree_incremental(filename,G):
    csv="Node"+CSV_COMMA+"Degree\n"
    for n in G.nodes():
        csv += n + CSV_COMMA + str(G.degree(n)) + "\n"
    
    f = codecs.open(PATH_CSV+filename+"/graph_degrees.csv","wb+", encoding='utf-8')
    f.write(csv)
    f.close

"""
Deprecated
def build_csv_node_analysis_single(filename,analysis,graphs):
    csv = ""
    csv += "Characteristics of nodes : "+analysis+"\n"
    csv += analysis+"\n"
    csv += analysis+" of the node"+"\n"

    G = nx.Graph()
    for g in range(len(graphs)):
        H = graphs[g].copy()
        G.add_edges_from(H.edges())

    for node in sorted(G.nodes(), key=G.degree, reverse=True):
    #for node in G.nodes():
        data = G.degree(node)
        csv += str(node) + CSV_COMMA + str(data)+ "\n"
    f = open(PATH_CSV+filename+"/"+analysis.replace(" ","_")+"_single.csv","wb+")
    f.write(csv)
    f.close()
"""

def csv_clustering(filename,graphs,mode):
    csv="Context"+CSV_COMMA+mode+" clustering coefficient\n"
    for context in range(len(graphs)):
        g = graphs[context]
        csv += str(context)+CSV_COMMA 
        if len(g.edges()) > 0:
            csv+= str(average_clustering(g)) + "\n"
        else:
            csv+= "N/A\n"
    
    f = open(PATH_CSV+filename+"/clustering_"+mode.lower()+".csv","w+")
    f.write(csv)
    f.close

def csv_new_characters(filename,iGraphs):
    csv="New character" + CSV_COMMA+"Link to\n"
    registered = []
    for g in iGraphs:
        for n in g.nodes():
            if n not in registered:
                registered.append(n)
                csv+= n + CSV_COMMA
                for m in g.neighbors(n):
                    csv += m + CSV_COMMA
                csv+= "\n" 
    
    f = codecs.open(PATH_CSV+filename+"/new_characters.csv","wb+", encoding='utf-8')
    f.write(csv)
    f.close()

"""
Deprecated
def build_csv_graph_analysis_single(filename,analysis,graphs,f):
    csv = ""
    csv += "Evolution of the "+analysis+"\n"
    csv += "Number of dialogs"+"\n"
    csv += analysis+"\n"
    csv += analysis+" of the 'n' first dialogs"+"\n"
    for g in range(len(graphs)):
        G = nx.Graph()
        if g == 0:
            H = graphs[g].copy()
            G.add_edges_from(H.edges())
        for sub in range(0,g):
            H = graphs[sub].copy()
            G.add_edges_from(H.edges())
        if len(G.edges()) > 0:
            clustering = f(G)
        else:
            clustering = "N/A"
        csv += str(g) + CSV_COMMA + str(clustering)+ "\n"
    f = open(PATH_CSV+filename+"/"+analysis.replace(" ","_")+"_single.csv","wb+")
    f.write(csv)
    f.close()


def build_csv_graph_analysis_double(filename,analysis,graphs,f):
    csv = ""
    csv += "Evolution of the "+analysis+"\n"
    csv += "Number of dialogs"+"\n"
    csv += analysis+"\n"
    csv += analysis+" of the 'n' first dialogs"+"\n"
    for g in range(len(graphs)):
        curGraph = graphs[g]
        if len(curGraph.edges()) > 0:
            clustering = f(curGraph)
        else :
            clustering="N/A"
        csv += str(g) + CSV_COMMA + str(clustering) + "\n"
    f = open(PATH_CSV+filename+"/"+analysis.replace(" ","_")+"_double.csv","wb+")
    f.write(csv)
    f.close()
"""
###############################################################
# Graph export functions
###############################################################

def build_png_graphs(filename,graphs,mode):
    for context in range(len(graphs)):
        g = graphs[context]
        edgesize=[float(edge[2]['mentions']) for edge in g.edges(data=True)]
        if len(edgesize) > 0:
            ms = max(edgesize)
            edgesize = [1+s*24/ms for s in edgesize] 
        edgecolor=[edge[2]['sentiment'] for edge in g.edges(data=True)]
        nodesize=[100*int(g.degree()[n]) for n in g.nodes()]
        cmap = plt.cm.get_cmap(name="RdYlGn")
        #nx.draw(g,with_labels=True,node_color='#65a5cc',alpha=0.8,node_size=nodesize,font_size=7,width=edgesize,edge_color=edgecolor,edge_cmap=cmap) #update this line to avoid depreciation messahe
        nx.draw_networkx(g,with_labels=True,node_color='#65a5cc',alpha=0.8,node_size=nodesize,font_size=7,width=edgesize,edge_color=edgecolor,edge_cmap=cmap)
        plt.savefig(PATH_PNG+filename+"/"+mode.lower()+"/Context_"+str(context)+".png")
        plt.close()

def output_csv_graphs(filename,graphs,mode):
    for i in range(len(graphs)):
        degrees = "Name" + CSV_COMMA+"Degree\n"
        csv = "Node 1" + CSV_COMMA + "Node 2" + CSV_COMMA + "Sentiment" + CSV_COMMA + "Mentions\n"
        g = graphs[i]
        for (node, adj_dic) in list(g.adjacency()):
            degrees += node + CSV_COMMA + str(g.degree()[node])+"\n"
            for node2 in list(adj_dic.keys()):
                csv+= node + CSV_COMMA + node2 + CSV_COMMA + str(adj_dic[node2]['sentiment']) + CSV_COMMA + str(adj_dic[node2]['mentions']) + "\n"
        f = codecs.open(PATH_CSV+filename+"/"+mode+"/graph_"+mode+"_"+str(i)+".csv", "wb+", encoding='utf-8')
        f.write(csv)
        f.close()
        f2 = codecs.open(PATH_CSV+filename+"/"+mode+"/degrees_"+mode+"_"+str(i)+".csv", "wb+", encoding='utf-8')
        f2.write(degrees)
        f2.close()

"""
DEPRECATED
def build_png_graph_single(filename,graphs):
    for g in range(len(graphs)):
        G = nx.Graph()
        if g == 0:
            H = graphs[g].copy()
            G.add_edges_from(H.edges(data=True))
        for sub in range(0,g):
            H = graphs[sub].copy()
            G.add_edges_from(H.edges(data=True))
        edgesize=[100*float(edge[2]['weight']) for edge in G.edges(data=True)]
        nodesize=[300*int(v) for v in G.degree().values()]
        cmap = plt.cm.get_cmap(name="RdYlGn")
        nx.draw(G,with_labels=True,node_color='#65a5cc',alpha=0.8,node_size=nodesize,font_size=7,width=edgesize,edge_color=edgesize,edge_cmap=cmap)
        plt.savefig(PATH_PNG+filename+"/SINGLE/"+str(g)+"_"+"single"+".png")
        plt.close()

def build_png_graph_double(filename,graphs):
    for g in range(len(graphs)):
        G = graphs[g]        
        edgesize=[100*float(edge[2]['weight']) for edge in G.edges(data=True)]
        nodesize=[300*int(v) for v in G.degree().values()]
        cmap = plt.cm.get_cmap(name="RdYlGn")
        nx.draw(G,with_labels=True,node_color='#65a5cc',alpha=0.8,node_size=nodesize,font_size=7,width=edgesize,edge_color=edgesize,edge_cmap=cmap)
        plt.savefig(PATH_PNG+filename+"/DOUBLE/"+str(g)+"_"+"double"+".png")
        plt.close()
"""

def write_graph(G,filename):   
    nx.write_gexf(G, PATH_GRAPHS+filename+".gexf")
    data2 = json_graph.node_link_data(G)
    json.dumps(data2)
    f2 = open(PATH_GRAPHS+filename+'.json','w+')
    json.dump(data2,f2) 

###############################################################
# All graphs outputting function
###############################################################

def output_graphs(filename, iGraphs, graphs, png = True):
    csv_clustering(filename,graphs,"Context")
    csv_clustering(filename,iGraphs,"Incremental")
    csv_degree_incremental(filename,iGraphs[-1])
    csv_new_characters(filename,iGraphs)
    output_csv_graphs(filename,graphs,"Context")
    output_csv_graphs(filename,iGraphs,"Incremental")
    print("csv saved")
    write_graph(iGraphs[-1], filename)
    print("json saved")
    if png:
        build_png_graphs(filename,graphs,"Context")
        build_png_graphs(filename,iGraphs,"Incremental")
        print("png saved")
    
