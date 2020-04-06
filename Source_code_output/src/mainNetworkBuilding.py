import bookInputOutput as bIO
import bookNetworkBuilding as bNB
from helpers import PATH_GRAPHS, PATH_SERIALIZED

def load_single_file():
    filename = input("Enter the title of the book to be analyzed \n")
    if filename == "":
        filename = "Harry_Potter_1"
    generate_graph(filename)

def load_all_files():   
    files = bIO.get_files_in_folder(PATH_GRAPHS)
    for f in files:
        if f[-4:]!="json": ##No need to use load book 2 times (json and gefx registered)
            filename = f[:-5]
            generate_graph(filename)

def generate_graph(filename):
        print("Loading occurrences...")
        dialog_occurrences = bIO.get_object(PATH_SERIALIZED + filename + "_occurrences_CID")
        dialog_contexts = bIO.get_object(PATH_SERIALIZED + filename+ "_contexts")
        aliasTable, connectionsTable, aliases = bIO.get_object(PATH_SERIALIZED+filename+"_alias")
        len_dialog_contexts = len(dialog_contexts)
        print("Loading OK. Graph building...")
        iGraphs, graphs = bNB.build_networks(dialog_occurrences, len_dialog_contexts, connectionsTable)
        print("OK, graph will be saved")
        bIO.output_graphs(filename, iGraphs, graphs)
        print("Output complete")
        
if __name__ == '__main__':
    load_single_file()