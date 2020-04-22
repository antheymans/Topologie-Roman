import bookInputOutput as bIO
import bookNetworkBuilding as bNB
from helpers import PATH_GRAPHS, PATH_SERIALIZED

if __name__ == '__main__':
    '''
    filename="Harry_Potter_1"
    print "Loading occurrences..."
    dialog_occurrences = bIO.get_object("../serialized/"+filename+"_occurrences_CID")
    len_dialog_contexts = 135
    print "Loading OK. Graph building..."
    iGraphs, graphs = build_networks(dialog_occurrences, len_dialog_contexts)
    print "OK, graph will be saved"
    bIO.output_graphs(filename, iGraphs, graphs)
    '''
    files = bIO.get_files_in_folder(PATH_GRAPHS)
    for f in files:
        if f[-4:]!="json": ##No need to use load book 2 times (json and gefx registered)
            filename = f[:-5]

            print filename
            print "Loading occurrences..."
            dialog_occurrences = bIO.get_object(PATH_SERIALIZED + filename + "_occurrences_CID")
            dialog_contexts = bIO.get_object(PATH_SERIALIZED + filename+ "_contexts")
            len_dialog_contexts = len(dialog_contexts)
            print "Loading OK. Graph building..."
            iGraphs, graphs = bNB.build_networks(dialog_occurrences, len_dialog_contexts)
            print "OK, graph will be saved"
            bIO.output_graphs(filename, iGraphs, graphs)
            print "Output complete"