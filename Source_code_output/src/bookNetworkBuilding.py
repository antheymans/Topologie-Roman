#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import networkx as nx

from helpers import uniques
TIME_FACTOR = 0.9 #Factor by which the score decreases after each new mention during the incremental networks
NOTABILITY = 1 #Minimum number of conversations in which an agent must be present for relevance
    
###############################################################
# Subnetworks generation function
###############################################################

def build_context_networks(len_dialog_contexts,dialog_occurrences):
    """
    Build a list of graphs for each context
    """
    graphs = []
    nodeCount = {}
    
    for context in range(len_dialog_contexts):
        occurrences = [d for d in dialog_occurrences if d['context']==context]
        curGraph = nx.Graph()
        
        speakers = uniques([o['from'] for o in occurrences])
        curGraph.add_nodes_from(speakers)
        for o in occurrences:
            if len(o['from']) > 0:
                if len(o['to']) > 0:
                    for t in o['to']:
                        if len(t) > 0:
                            if curGraph.has_edge(o['from'], t):
                                curGraph[o['from']][t]["sentiment"] += o['sentiment']
                                curGraph[o['from']][t]["mentions"] += 1
                            else:
                                curGraph.add_edge(o['from'], t, sentiment=o['sentiment'], mentions=1)
                                
        
        for e in list(curGraph.edges()):
            curGraph[e[0]][e[1]]["sentiment"] /= curGraph[e[0]][e[1]]["mentions"]
        
        for n in curGraph.nodes():
            nodeCount[n] = nodeCount.get(n,0) + 1
        graphs.append(curGraph)
        
    return graphs, nodeCount

###############################################################
# Global network generation function
###############################################################

def build_inc_networks(graphs, nodeCount):
    """
    Build a global graph for the entire book
    """
    iGraphs = []
    G = nx.Graph()
    
    for g in graphs:
        for n in g.nodes():
            G.add_node(n)
        
        for e in list(g.edges(data=True)):
            if G.has_edge(e[0],e[1]):
                mentions =G[e[0]][e[1]]['mentions'] 
                G[e[0]][e[1]]['sentiment'] = G[e[0]][e[1]]['sentiment'] * TIME_FACTOR * (mentions-1)/mentions + e[2]['sentiment']
                G[e[0]][e[1]]['mentions'] += 1
            else:
                G.add_edge(e[0],e[1],mentions=e[2]['mentions'], sentiment=e[2]['sentiment'])

        for n in g.nodes():
            if nodeCount[n] < NOTABILITY:
                print(n , "node count is ", nodeCount[n])
                G.remove_node(n)
        #"" is null speaker and should not be considered as a node        
        if "" in G.nodes():
            G.remove_node("")
        iGraphs.append(G.copy())
        
    return iGraphs

###############################################################
# Main network generation function
###############################################################

def build_networks(dialog_occurrences, len_dialog_contexts, connectionsTable):
    graphs, nodeCount = build_context_networks(len_dialog_contexts, dialog_occurrences)
    iGraphs = build_inc_networks(graphs,nodeCount)
    for node in iGraphs[-1].nodes():
        if node in connectionsTable.nodes():
            gender = connectionsTable.nodes()[node]["gender"]
            iGraphs[-1].nodes()[node]["gender"] = gender            
        else:
            print("error graph construction: node " + str(iGraphs[-1].nodes(data = True)[node]) + " not in connectionsTable")
            iGraphs[-1].nodes()[node]["gender"] = 0
    return iGraphs, graphs


    
