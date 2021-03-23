import bookInputOutput as bIO
import bookCharacterIdentification as bCI
import networkx as nx
import helpers

if __name__ == "__main__":
    filename = input("Enter the title of the .txt file to be analyzed \n")
    if filename == "":
        filename = "Harry_Potter_1"
     
    print("Loading book...")
    sentences, breaks, sentiments, chunks, speakers, script = bIO.load_book(filename)    
    print("Loading occurrences...")
    dialog_occurrences = bIO.get_object("../serialized/"+filename+"_occurrences")
    print("Loading contexts...")
    dialog_contexts = bIO.get_object("../serialized/"+filename+"_contexts")
    print("Loading OK. Analysis...")
    aliasTable, connectionsTable, aliases = bCI.character_analysis(dialog_contexts, dialog_occurrences, chunks, {}, nx.Graph(), nx.DiGraph(), speakers, False)
    print("Complete!")
    
    helpers.compute_statistics_CID(dialog_occurrences)
    bIO.save_occurrences_CID(filename,dialog_occurrences)
    bIO.export_aliases(aliasTable,connectionsTable, aliases,filename)


