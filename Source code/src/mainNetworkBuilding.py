import bookInputOutput as bIO
import bookNetworkBuilding as bNB

if __name__ == '__main__':
    '''
    filename="Harry_Potter_1"
    print "Loading occurrences..."
    dialog_occurrences = bIO.get_object("../serialized/"+filename+"_occurrences_CID")
    len_dialog_contexts = 135
    print "Loading OK. Graph building..."
    iGraphs, graphs = build_networks(dialog_occurrences, len_dialog_contexts)
    print "OK"
    bIO.output_graphs(filename, iGraphs, graphs)
    '''
    files = bIO.get_files_in_folder("../books_analyzed")
    for f in files:
        filename = f[:-4]
        print filename
        print "Loading occurrences..."
        dialog_occurrences = bIO.get_object("../serialized/"+filename+"_occurrences_CID")
        dialog_contexts = bIO.get_object("../serialized/"+filename+"_contexts")
        len_dialog_contexts = len(dialog_contexts)
        print "Loading OK. Graph building..."
        iGraphs, graphs = bNB.build_networks(dialog_occurrences, len_dialog_contexts)
        print "OK"
        bIO.output_graphs(filename, iGraphs, graphs)
        print "Output complete"