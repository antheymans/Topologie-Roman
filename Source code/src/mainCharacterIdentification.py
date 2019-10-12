import bookInputOutput as bIO
import bookCharacterIdentification as bCI

if __name__ == "__main__":
    filename = "Harry_Potter_1"
    print "Loading occurrences..."
    dialog_occurrences = bIO.get_object("../serialized/"+filename+"_occurrences")
    print "Loading contexts..."
    dialog_contexts = bIO.get_object("../serialized/"+filename+"_contexts")
    print "Loading OK. Analysis..."
    aliasTable, connectionsTable, aliases = bCI.characterAnalysis(dialog_occurrences,dialog_contexts,{}, nx.Graph(), nx.Graph())
    print "Complete!"
    
    /.compute_statistics_CID(dialog_occurrences,filename)
    bIO.save_occurrences_CID(filename,dialog_occurrences)
    bIO.export_aliases(aliasTable,connectionsTable, aliases,filename)
