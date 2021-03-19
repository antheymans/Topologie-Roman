import numpy 
import matplotlib.pyplot as plt
import powerlaw
from scipy.optimize import curve_fit

from helpers import PATH_GRAPHS, PATH_PNG, PATH_CSV, PATH_BOOKS
from bookInputOutput import get_files_in_folder, get_preferential_attachement, CSV_COMMA, build_last_png_graphs
import auxSignature

 
 
def generate_distrib(filename):
    file = open(PATH_CSV + filename +"/graph_degrees.csv", "r")
    Lines = file.readlines() [1:]
    degree = []
    for line in Lines:
        line = line.split(CSV_COMMA)
        degree.append(int(line[1][:-1]))
  
    x = range(0,max(degree)+1)    
    degree_distribution = numpy.zeros(len(x)).astype(int)
    for elem in degree:
        degree_distribution[int(elem)]+=1  
    return degree_distribution
    
    
def generate_graph_degree(filename): 
    import os
    if not os.path.exists(PATH_PNG + "degree"):
        os.mkdir(PATH_PNG + "degree")
    
    file = open(PATH_CSV + filename +"/graph_degrees.csv", "r")
    Lines = file.readlines() [1:]
    degree = []
    for line in Lines:
        line = line.split(CSV_COMMA)
        degree.append(int(line[1][:-1]))
  
    x = range(0,max(degree)+1)    
    degree_distribution = numpy.zeros(len(x)).astype(int)
    for elem in degree:
        degree_distribution[int(elem)]+=1  

    plt.plot(x, degree_distribution, label=str('Node Degree of ' + filename))    
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.savefig(PATH_PNG + "degree/" + filename,  bbox_inches = "tight")
    # # plt.show()
    plt.close()
    
    
    # # plt.loglog(x, degree_distribution, label=str('Node Degree of ' + filename))
    # # plt.legend()
    # # plt.ylabel("Number of nodes")
    # # plt.xlabel("Nodes Degree") 
    # # plt.show()
    
    # # mu = numpy.mean(degree)
    # # std = numpy.std(degree)
    
    # # fit = powerlaw.Fit(degree, xmin=4)
    # # xmin = int(fit.power_law.xmin)
    # mu = sum(degree_distribution[xmin:xmax])/len(degree_distribution[xmin:xmax])
    # # alpha = fit.power_law.alpha
    # # A = mu * (alpha - 2) / (xmin**(2 - alpha))
    # # plt.axvline(x=int(fit.xmin), color = 'r', label = "Xmin")
    # # print("alpha is ",fit.power_law.alpha, " and sigma is ", fit.power_law.sigma, ".")
    # fig2 = fit.plot_pdf(color='b', linewidth=2, label = " Power law fitting")
    # # degree_distribution_sum = sum(degree_distribution)
    # # degree_distribution = [elem / degree_distribution_sum for elem in degree_distribution]
    # # plt.plot(x[:], degree_distribution[:], 'g', label=' distribution')    

    # fit.power_law.plot_pdf(color='b', linestyle='--', ax=fig2, label = 'Powerlaw fitting')
    # # y = [(A * ((val)**(-alpha))) for val in x[xmin:xmax]]
    # # plt.loglog(x[xmin:xmax], y, 'r', label = " Power law fitting")

    # # bin_edges, probability = fit.pdf()
    # # R, p = fit.distribution_compare('power_law', 'stretched_exponential', normalized_ratio=True)
    # print("R is ",R," and p is ", p)
    # # plt.ylabel("Number of nodes")
    # # plt.xlabel("Nodes Degree")
    # # plt.title("Power law fitting of alpha :"+ str(round(fit.power_law.alpha,2)) + ", sigma :"+ str(round(fit.power_law.sigma,2)) + ", A :"+ str(round(A,2))+", Xmin :"+ str(round(fit.xmin,2)))
    # # plt.legend()
    # # plt.show()   
  
def exponential(x, a, b):
    if type(x) == list:
        x = numpy.array(x)
    return a*numpy.exp(b*x)
    
def loga(x, a, b):
    if type(x) == list:
        x = numpy.array(x)
    return a*numpy.log(x)+b
    
def logloga(x, a, b):
    if type(x) == list:
        x = numpy.array(x)
    return a*numpy.log(x)/numpy.log(numpy.log(x))+b
    
    
def power_law(x, a, b):
    return a*numpy.power(x , b)
    
def mean_distrib(files, isScript):
    story = "Novels"
    if isScript:
        story = "Scripts"

    distribution = []
    print(files)    
    for file in files:
        print(file)
        new_distr = generate_distrib(file[:-4])
        diff_size = len(new_distr) - len(distribution)
        while diff_size > 0:
            diff_size -= 1
            distribution.append(0)
        for i in range(len(new_distr)):
            distribution[i] += new_distr[i]
    x = range(0, len(distribution))
    x_vec = list(range(0, len(distribution)))
    for index in x:
        distribution[index] = distribution[index]/ len(files)
        x_vec[index] +=1

    degree_distribution = distribution
    
    xmin = 1
    xmax = len(x)
    pars, cov = curve_fit(f=exponential, xdata=x, ydata=degree_distribution, p0=[0, 0], bounds=(-numpy.inf, numpy.inf))    
    pars2, cov2 = curve_fit(f=power_law, xdata=x_vec[xmin:xmax], ydata=degree_distribution[xmin:xmax], p0=[0, 0], bounds=(-numpy.inf, numpy.inf))    
    xmax = len(x)
    res = sum(degree_distribution[xmin:xmax] - exponential(x[xmin:xmax], *pars))
    res2 = sum(degree_distribution[xmin:xmax] - power_law(x_vec[xmin:xmax], *pars2))
    print(pars, cov, res)#nov 25.13373576 -0.15795688] [[ 2.12875618e+00 -1.32679551e-02] #script[ 5.51683625 -0.11227941] [[ 1.06685611e-01 -2.16226351e-03]
    print(pars2, cov2, res2)#nov [147.23761823  -1.59962459] [[ 6.43356139e+00 -3.85331087e-02] #script [14.05704682 -0.96477256] [[ 2.32232473 -0.08762363]
    
    plt.plot(x, degree_distribution, label=str(story+': mean degree distribution'))   
    plt.plot(x, exponential(x, *pars), label=str('exponential fitting'))
    plt.plot(x[xmin:xmax], power_law(x_vec[xmin:xmax], *pars2), label=str('power-law fitting')) 
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.show()
    
    plt.yscale("log") 
    plt.plot(x, degree_distribution, label=str(story+': mean degree distribution'))   
    plt.plot(x, exponential(x, *pars), label=str('exponential fitting'))
    plt.plot(x[xmin:xmax], power_law(x_vec[xmin:xmax], *pars2), label=str('power-law fitting')) 
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.show()
   
    
    
    #plt.loglog(x, degree_distribution, label=str('mean degree distributions'))
    plt.loglog(x, degree_distribution, label=str(story+': mean degree distribution'))   
    plt.loglog(x, exponential(x, *pars), label=str('exponential fitting'))
    plt.loglog(x[xmin:xmax], power_law(x_vec[xmin:xmax], *pars2), label=str('power-law fitting')) 
    plt.legend()
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree") 
    plt.show()

def generate_mean_path_distrib(files, isScript = False, isAll = False):
    import auxSignature
    story = "novels"
    if isScript:
        story = "scripts"
    if isAll:
        story = " all stories"
    sizes = []
    mean_paths = []
    for file in files:
        graph = auxSignature.get_graph(file)
        mean_paths.append(auxSignature.get_mean_path_from_graph(graph))
        sizes.append(len(graph))
    #print(mean_paths, degree)

    xmin = 1
    xmax = len(sizes)
    pars, cov = curve_fit(f=loga, xdata=sizes, ydata=mean_paths, p0=[0, 0], bounds=(-numpy.inf, numpy.inf))    
    pars2, cov2 = curve_fit(f=logloga, xdata=sizes, ydata=mean_paths, p0=[0, 0], bounds=(-numpy.inf, numpy.inf))    
    res = sum(mean_paths - loga(sizes, *pars))
    res2 = sum(mean_paths - logloga(sizes, *pars2))
    
    print(pars, cov, res)
    print(pars2, cov2, res2)
    
    l1 = loga(sizes, pars[0], pars[1])
    l2 = logloga(sizes, pars2[0], pars2[1])

    
    plt.scatter(sizes, mean_paths, s = 2, label=str("Evolution of mean path lenth following graph size for all "+story))  
    plt.plot(sizes, l1, label=str('fitting of equation '+str(round(pars[0],3)) +"*log(x) +" + str(round(pars[1],3))))   
    plt.plot(sizes, l2, label=str('fitting of equation '+str(round(pars2[0],3)) +"*log(x)/log(log(x)) +" + str(round(pars2[1],3))))   

    plt.ylabel("Mean Path length")
    plt.xlabel("Size of the bigger component")    
    plt.legend()
    plt.show()
    
    plt.yscale("log") 
    plt.scatter(sizes, mean_paths, s = 2, label=str('Evolution of mean path lenth following graph size for all '+story))   
    plt.plot(sizes, loga(sizes, *pars), label=str('fitting of equation '+str(round(pars[0],3)) +"*log(x) +" + str(round(pars[1],3))))   
    plt.plot(sizes, logloga(sizes, *pars2), label=str('fitting of equation '+str(round(pars2[0],3)) +"*log(x)/log(log(x)) +" + str(round(pars2[1],3))))   
    plt.ylabel("Mean Path length")
    plt.xlabel("Size of the bigger component")    
    plt.legend()
    plt.show()
    
    plt.yscale("log") 
    plt.xscale("log") 
    plt.scatter(sizes, mean_paths, s = 2, label=str('Evolution of mean path lenth following graph size for all '+story))   
    plt.plot(sizes, loga(sizes, *pars), label=str('fitting of equation '+str(round(pars[0],3)) +"*log(x) +" + str(round(pars[1],3))))   
    plt.plot(sizes, logloga(sizes, *pars2), label=str('fitting of equation '+str(round(pars2[0],3)) +"*log(x)/log(log(x)) +" + str(round(pars2[1],3))))   
    plt.ylabel("Mean Path length")
    plt.xlabel("Size of the bigger component")    
    plt.legend()
    plt.show()
   
   
   
#############

def somme(tup):
    res = 0
    for n in tup:
        res += int(n)
    return res
    
def all_attachement_distribution(filenames, f):
    from itertools import zip_longest
    
    all_degree = [] 
    all_prob = []
    for filename in filenames:
        degree, count, total = get_preferential_attachement(filename)
        div = lambda l1,l2: [l1[k]/l2[k] if l2[k] != 0 else 0 for k in range(len(l1))]
        prob = div(count,total)
        all_degree.extend(degree)
        all_prob.extend(prob)
    
    a, b = numpy.polyfit(all_degree, all_prob, 1)
    x = range(1, max(all_degree)+1)
    linear = [a * k + b for k in x]

    plt.scatter(all_degree, all_prob, label=str(f+': preferential attachement'))   
    plt.plot(x, linear, 'r', label=str('linear fit of equation y = ' + str(round(a,3)) +"*x +(" + str(round(b,3))+")"))
    plt.ylabel('Probability')
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.savefig(PATH_PNG + "attachement/" + f,  bbox_inches = "tight")
    plt.close()
    
    
def attachement_distribution(filename):
    degree, count, total = get_preferential_attachement(filename)
    div = lambda l1,l2: [l1[k]/l2[k] if l2[k] != 0 else 0 for k in range(len(l1))]
    
    prob = div(count,total)
    
    a, b = numpy.polyfit(degree, prob, 1)
    x = range(1, max(degree)+1)
    linear = [a * k + b for k in x]

    plt.scatter(degree, prob, label=str(filename+': preferential attachement'))   
    plt.plot(x, linear, 'r', label=str('linear fit of equation y = ' + str(round(a,3)) +"*x +(" + str(round(b,3))+")"))
    plt.ylabel('Probability')
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.savefig(PATH_PNG + "attachement/" + filename,  bbox_inches = "tight")
    plt.close()



##################
# final graph 

def draw_final(files):
    for file in files:
        graph = auxSignature.get_graph(file)
        build_last_png_graphs(file, graph)
    
    
    
########################################
### Main

if __name__ == '__main__':
    files = get_files_in_folder(PATH_BOOKS)
    scripts = []
    novels = []
    files2 = []
    for file in files:
        #attachement_distribution(file[:-4])
        #print(file[-10:-4])
        if file[-10:-4]!="SCRIPT":
            #files2.append(file)
            scripts.append(file[:-4])    
        else: 
            novels.append(file[:-4])
        files2.append(file[:-4])
    draw_final(files2)
    #mean_distrib(files2) 
    #all_attachement_distribution(scripts, "Scripts")
    #all_attachement_distribution(novels, "Novels")
    #all_attachement_distribution(files2, "All")


    #for file in files:
    #    generate_graph_degree(file[:-4])
    #generate_mean_path_distrib(scripts, True)
    #generate_mean_path_distrib(novels, False)
    #generate_mean_path_distrib(files2, False, True)


    #generate_mean_path_distrib(files2)


