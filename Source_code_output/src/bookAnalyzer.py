#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import helpers
import bookInputOutput as bIO
import bookDialogExtraction as bDE
import bookCharacterIdentification as bCID
import bookNetworkBuilding as bNB
import time 
import sys



from helpers import PATH_BOOKS, compute_statistics, compute_statistics_CID

###############################################################
# Main analysis functions
###############################################################

def book_analyze(file_txt):
    try: 
        tmps1=time.time()
        """
        DESCRIPTION: Main book analysis function
        INPUT: Filename in the PATH_BOOKS folder
        OUTPUT: .csv, .png and output files (no return statement) 
        """
        filename = file_txt[:-4]

        print("COMPUTING BOOK : ", filename)
        bIO.create_folders(filename)
        sentences, breaks, sentiments, chunks, speakers, script = bIO.load_book(filename)
        
        # Extracts the dialogs from the book
        print("Extracting dialogs...")
        dialog_spacing, dialog_occurrences, dialog_contexts, count, threshold = bDE.dialog_extraction(sentences, breaks, sentiments, chunks, speakers)
        print("Dialog extraction complete !")

        #Build the CSV spacing map
        bIO.build_csv_spacing_map(dialog_spacing, count, threshold, filename)
        
        #Print stats for character identification and output them to a file that is constantly updated.
        bIO.save_occurrences_contexts(filename,dialog_occurrences,dialog_contexts)
        stat = compute_statistics(dialog_occurrences)
        bIO.update_stats(filename,stat)
        
        #Load the name files
        previous_book = ""
        if False:
            previous_book = input("Use a previous book? If so, enter its name.")
        oldAliasTable, oldConnectionsTable, oldAliases = bIO.load_alias_table(previous_book)
        
        print("Character analysis...")
        aliasTable, connectionsTable, aliases = bCID.character_analysis(dialog_contexts, dialog_occurrences, chunks,oldAliasTable,oldConnectionsTable,oldAliases,speakers, script)
        print("Character analysis complete !")
        
        bIO.export_aliases(aliasTable, connectionsTable, aliases, filename)
        bIO.save_occurrences_CID(filename, dialog_occurrences)
        
        stat = compute_statistics_CID(dialog_occurrences)
        bIO.update_stats_CID(filename,stat)
        

        # Network building
        iGraphs, graphs = bNB.build_networks(dialog_occurrences, len(dialog_contexts), connectionsTable)
        
        bIO.output_graphs(filename, iGraphs, graphs, False)
        
        tmps2=time.time()-tmps1
        print("Temps d'execution = %f" %tmps2)
        print("Analysis complete!")
    except:
        print("Oops!", sys.exc_info()[0], "of value ",sys.exc_info()[1]," occurred at ",sys.exc_info()[2]," while processing file", file_txt)

def read_all():
    # Go through all the books
    files = bIO.get_files_in_folder(PATH_BOOKS)
    files_analyzed = bIO.get_files_in_folder(helpers.PATH_BOOKS_OBJECT)
    for index in range(len(files_analyzed)):
        files_analyzed[index] = files_analyzed[index][:-5]+".txt"
    print(files)
    print(files_analyzed)
    for f in files:
        if f not in files_analyzed and f[-4:] == ".txt":
            book_analyze(f)
            
def read_all2():
    # Go through all the books
    files = bIO.get_files_in_folder(PATH_BOOKS)
    for f in files:
        book_analyze(f)
    
if __name__ == "__main__":
    title = input("Enter the title of the .txt file to be analyzed ('all' for all files).\n")
    if title == "all":
        read_all2()
    elif title == "some": 
        read_all()
    elif title[-4:] == ".txt":
        book_analyze(title)
    else:
        book_analyze(title + ".txt")
