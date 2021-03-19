import os
from bookInputOutput import *
from helpers import *

def attachment():
    begin = "\\begin{figure} \ContinuedFloat \n \t\\centering\n"
    end = "\\end{figure}\n"
    str = ""

    liste = os.listdir("../../rapport/pictures/attachement")
    for index in range(len(liste)):
        image = liste[index]
        if index % 2 == 0: str += begin 
        str += "\t\\begin{subfigure}{.49\\textwidth}\n"
        str += "\t\t\\centering\n"
        str += "\t\t\\includegraphics[width=\\linewidth]{pictures/attachement/"+image+"}\n"
        str += "\t\t\\phantomcaption\n"
        str += "\t\\end{subfigure}\n"
        if index % 2 == 1: str += end 
    if len(liste)%2 == 1: str += end
    print(str)
    
def final():
    begin = "\\begin{figure} \ContinuedFloat \n \t\\centering\n"
    end = "\\end{figure}\n"
    str = ""

    liste = os.listdir("../../rapport/pictures/_final_graph")
    for index in range(len(liste)):
        image = liste[index]
        if index % 2 == 0: str += begin 
        str += "\t\\includegraphics[width=\\linewidth]{pictures/_final_graph/"+image+"}\n"
        str += "\t\\phantomcaption\n"
        if index % 2 == 1: str += end 
    if len(liste)%2 == 1: str += end
    print(str)
    
def gender_count(weighted = False):
    import auxSignature
    files = get_files_in_folder(PATH_BOOKS)
    csv = "Book" + CSV_COMMA + "Gendered Rate" + CSV_COMMA + "Male Rate" + CSV_COMMA +"Female Rate" + "\n"

    for file in files:
    
        filename = file[:-4]
        graph = auxSignature.get_graph(filename)
        for n, d in graph.nodes(data=True):
            print(d)
            exit()
        if weighted :
            all = [graph.degree(n) for n in graph.nodes]
            male = [graph.degree(n) for n, d in graph.nodes(data=True) if d['gender']==1]
            female = [graph.degree(n) for n, d in graph.nodes(data=True) if d['gender']==-1]
            gendered = [graph.degree(n) for n, d in graph.nodes(data=True) if d['gender']!=0]
        else:
            all = [1 for n in graph.nodes]
            male = [1 for n, d in graph.nodes(data=True) if d['gender']==1]
            female = [1 for n, d in graph.nodes(data=True) if d['gender']==-1]
            gendered = [1 for n, d in graph.nodes(data=True) if d['gender']!=0]
            
        rate = sum(gendered)/sum(all)
        male_rate = sum(male)/sum(all)
        female_rate = sum(female)/sum(all)
        
        csv += filename + CSV_COMMA + str(rate) + CSV_COMMA +str(male_rate) + CSV_COMMA + str(female_rate) + "\n" 
        
        
    filename = PATH_CSV+ "gender_weighted_rate" + ".csv" if weighted else PATH_CSV + "gender_rate" + ".csv"
    f = open(filename,"w+")
    f.write(csv)
    f.close()

gender_count(True)


def draw():
    import networkx as nx
    import matplotlib.pyplot as plt

    g = nx.read_gexf("../graphs/ASOIAF_1.gexf")
    edgesize=[float(edge[2]['mentions']) for edge in g.edges(data=True)]
    if len(edgesize) > 0:
        ms = max(edgesize)
        edgesize = [1+s*24/ms for s in edgesize] 
    edgecolor=[edge[2]['sentiment'] for edge in g.edges(data=True)]
    nodesize=[80*int(g.degree()[n]) for n in g.nodes()]
    cmap = plt.cm.get_cmap(name="RdYlGn")
    
    color_map = []
    for n, d in g.nodes(data=True):
        if d['gender']==1:
            color_map.append('b')
        elif d['gender']==0: 
            color_map.append('g') 
        else:
            color_map.append('r') 
            
    figure = plt.gcf()
    figure.set_size_inches(16, 12)
    ax = plt.gca()
    ax.set_title("Social network of ASOIAF_1", fontsize = 24) 
    nx.draw_spring(g,with_labels=True,font_size = 10, node_color=color_map ,alpha=0.8,node_size=nodesize,width=edgesize,edge_color=edgecolor,edge_cmap=cmap)
    #plt.show()
    plt.savefig("spring.png", dpi=100)
    plt.close()
    figure = plt.gcf()
    figure.set_size_inches(16, 12)
    nx.draw_kamada_kawai(g,with_labels=True,font_size = 10, node_color='#65a5cc',alpha=0.8,node_size=nodesize,width=edgesize,edge_color=edgecolor,edge_cmap=cmap)
    #plt.show()
    plt.savefig("kamada.png", dpi=100)
    plt.close()
    figure = plt.gcf()
    figure.set_size_inches(16, 12)
    nx.draw(g,with_labels=True,font_size = 10, node_color='#65a5cc',alpha=0.8,node_size=nodesize,width=edgesize,edge_color=edgecolor,edge_cmap=cmap)
    plt.savefig("draw.png", dpi=100)
    plt.close()
