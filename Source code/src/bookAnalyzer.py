#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import bookInputOutput as bIO
import bookDialogExtraction as bDE
import bookCharacterIdentification as bCID
import bookNetworkBuilding as bNB

from helpers import PATH_BOOKS, print_statistics, print_statistics_CID

###############################################################
# Main analysis functions
###############################################################

def bookAnalyze(file_txt):
    """
    DESCRIPTION: Main book analysis function
    INPUT: Filename in the PATH_BOOKS folder
    OUTPUT: .csv, .png and output files (no return statement) 
    """
    filename = file_txt[:-4]
    print "COMPUTING BOOK : ", filename
    bIO.create_folders(filename)
    sentences, breaks, sentiments, chunks = bIO.loadBook(filename)
    
    
    # Extracts the dialogs from the book
    print "Extracting dialogs..."
    dialog_spacing, dialog_occurrences, dialog_contexts, count, threshold = bDE.dialogExtraction(sentences, breaks, sentiments, chunks)
    print "Dialog extraction complete !"
    
    #Build the CSV spacing map
    bIO.build_csv_spacing_map(dialog_spacing, count, threshold, filename)
    
    #Print stats for character identification and output them to a file that is constantly updated.
    print_statistics(dialog_occurrences,filename)
    
    bIO.save_occurrences_contexts(filename,dialog_occurrences,dialog_contexts)
    
    #Load the name files
    previous_book = raw_input("Use a previous book? If so, enter its name.")
    oldAliasTable, oldConnectionsTable, oldAliases = bIO.loadAliasTables(previous_book)
    
    print "Character analysis..."
    aliasTable, connectionsTable, aliases = bCID.characterAnalysis(dialog_occurrences, dialog_contexts,oldAliasTable,oldConnectionsTable,oldAliases)
    print "Character analysis complete !"
    
    bIO.exportAliases(aliasTable, connectionsTable, aliases, filename)
    bIO.save_occurrences_CID(filename, dialog_occurrences)
    
    print_statistics_CID(dialog_occurrences,filename)
    
    # Network building
    iGraphs, graphs = bNB.build_networks(dialog_occurrences, len(dialog_contexts))
    
    bIO.output_graphs(filename, iGraphs, graphs)
    
    print "Analysis complete!"

def readAll():
    # Go through all the books
    files = bIO.get_files_in_folder(PATH_BOOKS)
    for f in files:
        bookAnalyze(f)
    
if __name__ == "__main__":
    title = raw_input("Enter the title of the .txt file to be analyzed ('all' for all files).\n")
    print title  ##debug
    if title == "all":
        readAll()
    elif title[-4:] == ".txt":
        bookAnalyze(title)
    else:
        print("the input is not valid")
