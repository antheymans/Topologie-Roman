import numpy 
import matplotlib.pyplot as plt
import powerlaw
from scipy.optimize import curve_fit

from helpers import PATH_GRAPHS, PATH_PNG, PATH_CSV, PATH_BOOKS
from bookInputOutput import get_files_in_folder, CSV_COMMA

 
 
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
    return a*numpy.exp(b*x)
    
def power_law(x, a, b):
    return a*numpy.power(x , b)
    
def mean_distrib(files):
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
    plt.yscale("log") 
    plt.plot(x, degree_distribution, label=str('Novels: mean degree distributions'))   
    plt.plot(x, exponential(x, *pars), label=str('exponential fitting'))
    plt.plot(x[xmin:xmax], power_law(x_vec[xmin:xmax], *pars2), label=str('power-law fitting')) 
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree")    
    plt.legend()
    plt.show()
   
    
    
    #plt.loglog(x, degree_distribution, label=str('mean degree distributions'))
    plt.loglog(x, degree_distribution, label=str('Novels: mean degree distributions'))   
    plt.loglog(x, exponential(x, *pars), label=str('exponential fitting'))
    plt.loglog(x[xmin:xmax], power_law(x_vec[xmin:xmax], *pars2), label=str('power-law fitting')) 
    plt.legend()
    plt.ylabel("Number of nodes")
    plt.xlabel("Nodes Degree") 
    plt.show()


if __name__ == '__main__':
    files = get_files_in_folder(PATH_BOOKS)
    files2 = []
    for file in files:
        print(file[-10:-4])
        if file[-10:-4]=="SCRIPT":
            files2.append(file)
    mean_distrib(files2) 
    #for file in files:
    #    generate_graph_degree(file[:-4])


