#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Library handling the character extraction and alias resolution

import networkx as nx
import pattern.text.en as pen
from pattern.en.wordlist import ACADEMIC, BASIC, PROFANITY, TIME
import ast
import nameparser
import nltk
import csv


from helpers import is_root

###############################################################
# Alias table functions
###############################################################
def is_valid(word):
    if word[0] != word[0].upper() or word == word.upper():
        return False
    return True
    
def build_alias_table(sentences, oldAliasTable,oldConnectionsTable,oldAliases):
    aliasTable = oldAliasTable
    connectionsTable = oldConnectionsTable #Initialized at new graph if nothing is loaded
    aliases=oldAliases #Initialized at new graph if nothing is loaded
    chunks = []

    for l in sentences:
        for s in l:
            if isinstance(s, pen.Sentence):
                chunks.extend(s.chunks)
            else:
               print("error, wrong type ", type(s), type(l))
    
    #Load all set of words used help the classification between names and non-names words
    honorifics, female_honorifics, male_honorifics = get_honorifics()
    for honorific in honorifics:
        if honorific not in nameparser.config.CONSTANTS.titles:
            nameparser.config.CONSTANTS.titles.add(honorific)
            nameparser.config.CONSTANTS.titles.add(honorific.lower())
           
    honorifics = nameparser.config.titles.TITLES
    stop_words = get_stop_list()
    countries, nationalities = get_nationality_country()
    #First pass, isolate relevant proper nouns
    proper_nouns = {}
    locations = {}
    
    #import spacy 
    #nlp = spacy.load('en_core_web_sm',disable=['parser', 'tagger', 'textcat'])   
    #for chunk in chunks:
    #    for ent in nlp(chunk.string).ents:
    #        if ent.label_ == "PERSON":
    #            print(ent.text)
    #            if ent.text not in proper_nouns:
    #                proper_nouns[ent.text] = 0
    #            else:
    #                proper_nouns[ent.text] += 1
    
    #print(proper_nouns)
    #exit()
    for c in chunks:
        if c.head.type.find('NNP')==0 and is_valid(c.head.string):
            name = c.head.string
            if c.head.type == "NNP-LOC":
                if name not in locations:
                    locations[name] = 1
                else:
                    locations[name] += 1
            else:
                if c.head != c.sentence.chunk[0].words[0] and name.lower() not  in ACADEMIC \
                    and name.lower() not in PROFANITY and name.lower() not in TIME\
                    and name.lower() not in stop_words and name not in honorifics and name not in nationalities:
                    if name not in proper_nouns:
                        proper_nouns[name] = 0
                    else:
                        proper_nouns[name] += 1
    

    #country name are locations                        
    deleted_names = []
    for name in proper_nouns:
        if name in countries:
            if name in locations:
                locations[name] += proper_noun[name]
            else:
                locations[name] = proper_nouns[name]
                deleted_names.append(name)
    for name in deleted_names:
        del proper_nouns[name]  
    #for all names that are both classified as proper name and locations following context, choose the dominant use                            
    deleted_locations = []    
    for loc in locations:
        if loc in proper_nouns:
            print(loc)
            if locations[loc] >= proper_nouns[loc]// 4:
                print("confirmed")
                del proper_nouns[loc]
            else:
                print("proper name")
                deleted_locations.append(loc)
    for loc in deleted_locations:
        del locations[loc]        
    #print("locations: ",locations)
            
    
    #create dict containing canonical name linked to each proper noun    
    canonical_names_dict = {}
    proper_names = list(proper_nouns)
    for proper_noun  in proper_names:
        canonical_names_dict[proper_noun] = []
    names_corpus = nltk.corpus.names
    
    male_names = names_corpus.words('male.txt')
    female_names = names_corpus.words('female.txt')
    
    #Second pass,check all canonical names from chunks headed by a proper name
    for c in chunks:
        if c.head.string in proper_names:
            canonical_names_list = canonical_names_from_chunk(c, proper_names)        
            for wordlist in canonical_names_list:
                canonical_name = ' '.join(wordlist)
                if canonical_name not in connectionsTable:        
                    gender, name_category, name =categorize_name(canonical_name, male_honorifics, female_honorifics, male_names, female_names, connectionsTable)
                    
                    if name.first != "" and name.first not in proper_names:
                        if name.first.lower() not in BASIC and name.first.lower() not in ACADEMIC and name.first.lower() not in PROFANITY \
                            and name.first.lower() not in TIME and name.first not in locations and name.first.capitalize() not in nationalities \
                            and len(name.first.split()) == 1:
                            proper_names.append(name.first)
                            if c != c.sentence.chunk[0] or gender != 0:
                                #if begin of a sentence, firstname could be wrongly added
                                #but gender added mean that the name is well-labelled
                                proper_names.append(name.first)
                        else:
                            name_category = 6
                            
                    if name_category < 6:
                        connectionsTable.add_node(canonical_name)
                        connectionsTable.add_node(canonical_name)
                        connectionsTable.nodes[canonical_name]["gender"] = gender
                        connectionsTable.nodes[canonical_name]["name_category"] = name_category
                        connectionsTable.nodes[canonical_name]["name"] = name
                        connectionsTable.nodes[canonical_name]["value"] = 1                        
                        aliasTable[canonical_name]=[c.string]
                        for word in wordlist:
                            if word in canonical_names_dict:
                                canonical_names_dict[word].append(canonical_name)
                            else:
                                canonical_names_dict[word] = [canonical_name]
                    if name.first in proper_names and name.first not in canonical_names_dict.keys():
                        print("error proper name: ",name, name_category, name.first, wordlist, " chunk: ", c.words)
                    #else: #DEBUG 
                        #print(name_category, name.title,", first =", name.first,",last = ", name.last,"|", name)
                else:
                    aliasTable[canonical_name].append(c.string)
                    connectionsTable.nodes[canonical_name]["value"] += 1 
                    
    #del all name detected as proper but not related not any canonical name
    index = 0
    while index < len(proper_names):
        if len(canonical_names_dict[proper_names[index]]) == 0:
            del canonical_names_dict[proper_names[index]]
            proper_names.pop(index)
            #print("pop: ", proper_names.pop(index))
        index +=1
    #del all non proper name in the cnn dictionnary
    index = 0
    key_list = list(canonical_names_dict.keys())
    while index < len(key_list):
        if key_list[index] not in proper_names:
            del canonical_names_dict[key_list[index]]
        index +=1

    nicknames = get_nicknames()
    for name in proper_names:
        nick = []
        for n in proper_names[proper_names.index(name)+1:]:
            if is_root(name,n):
                nick.append(n)
        if len(nick) > 0:
            nick.append(name)
            nicknames.append(nick)        
    #link between them canonical names sharing firstname
    #name sharing a 1-value edge are considered as the same character while 2-value edge means a potential selection    
    used = {w : False for w in proper_names}
    for canonical_name, data in connectionsTable.nodes(data = True):
        #Use all firstname, category 3 or 4 indicates that firstname/last name have not been separated properly
        if data["name_category"] < 3: 
            firstname = data["name"].first
            if firstname != "" and used[firstname] == False:
                used[firstname] = True
                names_bucket = set()
                firstname_bucket = set()
                firstname_bucket.add(firstname)
                names_bucket.update(canonical_names_dict[firstname])
                for cluster in nicknames:#check nickname associated
                    if firstname in cluster:
                        for nickname in cluster:
                            if nickname in proper_names:
                                names_bucket.update(canonical_names_dict[nickname])
                                firstname_bucket.add(nickname)
                                used[nickname] = True
                if firstname[0] in proper_names:#check initial present
                    names_bucket.update(canonical_names_dict[firstname[0]])
                    firstname_bucket.add(firstname[0])
                    used[firstname] = True                
            names_bucket = list(names_bucket)
            for i in range(len(names_bucket)):
                for j in range(i+1, len(names_bucket)): 
                    node1 = connectionsTable.nodes[names_bucket[i]]
                    node2 = connectionsTable.nodes[names_bucket[j]]
                    if node1["gender"]*node2["gender"] != -1:#avoid to link male and female CN
                        if node1["name"].first in firstname_bucket and node2["name"].first in firstname_bucket:                        
                            if node1["name"].last == node2["name"].last:
                                equalize_gender(names_bucket[i], names_bucket[j], connectionsTable)
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)  
                            elif node1["name"].last == "" or node2["name"].last == "": 
                                if node1["name"].last == "" and node2["name"].last == "":
                                    equalize_gender(names_bucket[i], names_bucket[j], connectionsTable)
                                    connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)
                                else:
                                    connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 2)
                        elif node1["name"].first == "" or node2["name"].first == "" :
                            if (node1["name"].first == "" or node1["name"].last == "")  and (node2["name"].first == "" or node2["name"].last == "") :
                                equalize_gender(names_bucket[i], names_bucket[j], connectionsTable)
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)
                            else:
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 2)
    for edge in connectionsTable.edges(data = True):
        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print("error first binding")
            print(edge,connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"])
            exit() 
    #link name sharing only lastname
    for canonical_name, data in connectionsTable.nodes(data = True):
        lastname_list = data["name"].last_list
        if data["name"].first != "" and not used[data["name"].first] :
            lastname_list.append(data["name"].first)
            data["name"].first = None
        for lastname in lastname_list:
            if lastname in proper_names and used[lastname] == False:
                used[lastname] = True
                bucket = []
                bucket.extend(canonical_names_dict[lastname])            
                if lastname[0] in proper_nouns:#check initial
                    for cn2 in canonical_names_dict[lastname[0]]:
                        if cn2 not in bucket:
                            bucket.append(cn2)
                for cluster in nicknames:#check nickname associated
                    if lastname in cluster:
                        for nickname in cluster:
                            if nickname in proper_names:
                                for cn2 in canonical_names_dict[nickname]:
                                    if cn2 not in bucket:
                                        bucket.append(cn2)                               
                                used[nickname] = True
                for i in range(len(bucket)):
                    for j in range(i+1, len(bucket)):
                        node1 = connectionsTable.nodes[bucket[i]]
                        node2 = connectionsTable.nodes[bucket[j]]
                        if node1["gender"] * node2["gender"] != -1:
                            if node1["name"].first == "" and node2["name"].first == "":
                                connectionsTable.add_edge(bucket[i], bucket[j], paired = 1)
                                equalize_gender(bucket[i], bucket[j], connectionsTable)
                            elif (bucket[i], bucket[j]) not in connectionsTable.edges() :
                                connectionsTable.add_edge(bucket[i], bucket[j], paired = 2)
    for edge in connectionsTable.edges(data = True):
        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print("error begin")
            print(edge)
            exit() 
            
    #during the first phase, some inconsistent 2-paired conenction could have been made 
    #if a neutral name change its gender after a connection have been made
    for edge in connectionsTable.edges():
        if connectionsTable.nodes[edge[0]]["gender"] * connectionsTable.nodes[edge[1]]["gender"] == -1:        
            connectionsTable.remove_edge(edge[0],edge[1])
                            
    #link neutral noun with the most used nouns among their potential partner
    used = {w : False for w in connectionsTable.nodes}    
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False and data["gender"] == 0 and data["name_category"] <= 2:
            cluster = [canonical_name]
            ## group paired nodes from the neutral cluster
            #print("init", connectionsTable.edges(canonical_name, data = True))
            cluster_1_pair(connectionsTable, used, cluster)

            ## group their non-neutral nbh using their edges
            candidates_edge = []
            for cn2 in cluster:    
                for edge in connectionsTable.edges(canonical_name, data = True):  
                    if edge[2]["paired"] == 2 and edge not in candidates_edge:
                        candidates_edge.append(edge)
            if len(candidates_edge) > 0:     
                subAT= {s[1]: connectionsTable.nodes[s[1]]["value"] for s in candidates_edge}
                while len(subAT.keys()) != 0:
                    maxMentions = max(subAT, key=subAT.get)
                    gender = connectionsTable.nodes[maxMentions]["gender"]
                    del subAT[maxMentions]
                    connectionsTable.add_edge(canonical_name, maxMentions, paired = 1)
                    if gender != 0:

                        for cn2 in cluster:
                            connectionsTable.nodes[cn2]["gender"] = gender  
                            
                        #for cn2 in cluster:
                        #    for edge in connectionsTable.edges(cn2, data = True):
                        #        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
                        #            print(edge, connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"], "error neutral")
                        #            print(cluster, used[cn2], used[edge[1]])
                        #            exit()
                        for cn2 in cluster:
                            used[cn2] = True
                        #print("finished", cluster)

                        #remove edge genderly incorrect
                        for edge in candidates_edge:
                            if connectionsTable.nodes[edge[0]]["gender"] * connectionsTable.nodes[edge[1]]["gender"] == -1:        
                                connectionsTable.remove_edge(edge[0],edge[1])
                        break                  
                    elif not used[maxMentions]:
                        cluster.append(maxMentions)
                        cluster_1_pair(connectionsTable, used, cluster, index = len(cluster)-1)
     
    for edge in connectionsTable.edges(data = True):
        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print(used[edge[0]], used[edge[1]])
            print(edge, connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"], "error neutral end")
            exit()

    used = {w : False for w in connectionsTable.nodes} 
    #link nouns from 3+ categories noun with the most used nouns 1-2 category noun among their potential partner        
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False and data["name_category"] > 2:
            cluster = [canonical_name]
            cluster_1_pair_without_used(connectionsTable, cluster)
            found = 0
            for node in cluster:
                if connectionsTable.nodes[node]["name_category"] <= 2: #complete name found among nghs
                    found = 1
            if found  == 1:
                for node in cluster:
                    if connectionsTable.nodes[node]["name_category"] > 2:
                        used[node] = True
                    break
            ## group their further nbhs using their 2-values edges
            else:
                candidates_edge = []
                for cn2 in cluster:    
                    for edge in connectionsTable.edges(cn2, data = True):                
                        if edge[2]["paired"] == 2 and connectionsTable.nodes[edge[1]]["gender"] * \
                            connectionsTable.nodes[cn2]["gender"] != -1 and edge not in candidates_edge\
                            and connectionsTable.nodes[edge[1]] not in cluster:
                            candidates_edge.append(edge)
                if len(candidates_edge) > 0: 
                    subAT= {s[1]: connectionsTable.nodes[s[1]]["value"] for s in candidates_edge}
                    first_mention =  max(subAT, key=subAT.get)
                    while True:
                        maxMentions = max(subAT, key=subAT.get)
                        del subAT[maxMentions]
                        if connectionsTable.nodes[maxMentions]["name_category"] < 3:
                            connectionsTable.add_edge(maxMentions, canonical_name, paired = 1)
                            if connectionsTable.nodes[canonical_name]["gender"] == 0 and connectionsTable.nodes[maxMentions]["gender"] != 0:
                                for node in cluster:
                                    connectionsTable.nodes[node]["gender"] = connectionsTable.nodes[maxMentions]["gender"]
                            elif connectionsTable.nodes[canonical_name]["gender"] != 0 and connectionsTable.nodes[maxMentions]["gender"] == 0:
                                    cluster = [maxMentions]
                                    used2 = {w : False for w in connectionsTable.nodes}
                                    cluster_1_pair_without_used(connectionsTable, cluster) 
                                    for node in cluster:
                                        connectionsTable.nodes[node]["gender"] = connectionsTable.nodes[canonical_name]["gender"]
                            for node in cluster:
                                used[node] = True
                            #remove useless edge            
                            for edge in candidates_edge:
                                if connectionsTable.nodes[edge[0]]["gender"] * connectionsTable.nodes[edge[1]]["gender"] == -1:        
                                    connectionsTable.remove_edge(edge[0],edge[1])   
                            break
                        elif len(subAT.keys()) == 0:
                            break
    for edge in connectionsTable.edges(data = True):
        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print("error 3+ names binding")
            print(edge, connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"])
            exit()     
            
    #link between them 3+ names that have not been link with 2- names
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False and data["name_category"] > 2:
            cluster = [canonical_name]
            cluster_1_pair_without_used(connectionsTable, cluster)
            index = 0
            while index < len(cluster):
                cn2 = cluster[index]
                used[cn2] = True
                for edge in connectionsTable.edges(cn2, data = True):                
                    if edge[2]["paired"] == 2 and connectionsTable.nodes(data = True)[edge[1]]["gender"] * \
                        connectionsTable.nodes(data = True)[cn2]["gender"] != -1 and edge[1] not in cluster:
                        equalize_gender(canonical_name, edge[1], connectionsTable)
                        #if connectionsTable.nodes(data = True)[edge[1]]["gender"] == 0:
                        #    equalize_gender(canonical_name, edge[1], connectionsTable)
                        #elif connectionsTable.nodes(data = True)[cn2]["gender"] == 0:
                        #    for node in cluster:
                        #        connectionsTable.nodes(data = True)[node]["gender"] = connectionsTable.nodes(data = True)[edge[1]]["gender"]
                        cluster.append(edge[1])
                        cluster_1_pair_without_used(connectionsTable, cluster, index = len(cluster)-1)
                        connectionsTable.add_edge(edge[1], canonical_name, paired = 1)
                index +=1
                    
    for edge in connectionsTable.edges(data = True):
        if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print("error 3+ names binding between them")
            print(edge, connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"])
            exit()     
            
    #directed graph containg arrow linked to main canonical name of a cluster
    aliases.add_nodes_from(connectionsTable.nodes(data = True))
    print("connection established")
    used = {w : False for w in connectionsTable.nodes}

    #creates cluster of names related to every character
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False:  
            used[canonical_name] = True
            #add all neibhors and their neighbors recursively to our cluster
            cluster = []
            candidates = [canonical_name]
            while len(candidates) > 0:
                cn2 = candidates.pop()
                cluster.append(cn2)
                for edge in connectionsTable.edges(cn2, data = True):                
                    if edge[2]["paired"] == 1 and not used[edge[1]]:
                        used[edge[1]] = True
                        candidates.append(edge[1])                   
            subAT= {s: connectionsTable.nodes[s]["value"] for s in cluster}
            maxMentions = max(subAT, key=subAT.get) 
            cluster.remove(maxMentions)
            for cn2 in cluster:
                aliases.add_edge(cn2, maxMentions)
                aliasTable[maxMentions].extend(aliasTable.pop(cn2,[]))
    print("graph made")        
    
    for edge in aliases.edges():
        if connectionsTable.nodes[edge[0]]["gender"] != connectionsTable.nodes[edge[1]]["gender"]:
            print("error incorect gender for :" , edge, connectionsTable.nodes[edge[0]]["gender"], connectionsTable.nodes[edge[1]]["gender"])
    return aliasTable, connectionsTable, aliases

        
#from chunk, extract canonical name in a wordlist form
def canonical_names_from_chunk(chunk, proper_names):
    detected = 0
    canonical_names_list = [] #list of canonical names
    wordlist = []# canonical name in a form of wordlist      
    for w in chunk.words:
        if is_valid(w.string):
            detected = 1
            wordlist.append(w.string)
        elif detected == 1:
            canonical_names_list.append(wordlist)
            wordlist = []
            detected = 0
            
    if detected == 1:
        canonical_names_list.append(wordlist)
    
    #if multiple names in chunk, check that all of them contain a proper name
    if len(canonical_names_list) > 1:
        index = 0
        while index < len(canonical_names_list):
            wordlist = canonical_names_list[index]
            correct = 0
            for word in wordlist:
                if word in proper_names:
                    correct = 1
                    break
            if not correct:
                canonical_names_list.pop(index)
            else:
                index +=1
    return canonical_names_list
    
def equalize_gender(name1, name2, connectionsTable):
    node1 = connectionsTable.nodes[name1]
    node2 = connectionsTable.nodes[name2]
    if node1["gender"] == 0 and node2["gender"] != 0:
        node1["gender"] = node2["gender"]
        for edge in connectionsTable.edges(name1, data = True):
            if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[1]]["gender"] == 0:
                equalize_gender(name1, edge[1], connectionsTable)
    elif node2["gender"] == 0 and node1["gender"] != 0:
        node2["gender"] = node1["gender"]
        for edge in connectionsTable.edges(name2, data = True):
            if edge[2]["paired"] == 1 and connectionsTable.nodes[edge[1]]["gender"] == 0:
                equalize_gender(name2, edge[1], connectionsTable)
                
#cluster unused nodes linked by an 1-value edge
def cluster_1_pair(connectionsTable, used, cluster, index = 0):
    while index < len(cluster):
        for edge in connectionsTable.edges(cluster[index], data = True):
            if edge[2]["paired"] == 1 and not used[edge[1]] and edge[1] not in cluster:
                cluster.append(edge[1])
        index+=1
#cluster nodes linked by an 1-value edge
def cluster_1_pair_without_used(connectionsTable, cluster, index = 0):
    while index < len(cluster):
        for edge in connectionsTable.edges(cluster[index], data = True):
            if edge[2]["paired"] == 1 and edge[1] not in cluster:
                cluster.append(edge[1])
        index+=1
        

def get_honorifics():
    f = open("text_file\honorifics.txt", "r")
    string  = f.read()
    honorifics, female_honor, male_honor = ast.literal_eval(string)
    f.close()
    return honorifics, female_honor, male_honor
    
def get_nationality_country():
    country_list = []
    nationality_list = []
    with open("text_file\\nationality.csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            country_list.append(row[3])
            nationality_list.append(row[4])
    nationality_list.extend(["Black", "White"])
    return country_list, nationality_list

def get_stop_list():
    f = open("text_file\stop-list.txt", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        strings.append(line)
    f.close()
    return strings
    
def get_nicknames():
    f = open("text_file\hypocorisms.txt", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        strings.append(line.split())
    f.close()
    return strings
    
def get_verb_dependency():
    f = open("text_file\character-verb-predicates.tsv", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        string = line.split()
        if len(string) > 0:
            strings.append(string)
    f.close()
    return strings

def build_alias_table_script(sentences, oldAliasTable,oldConnectionsTable,oldAliases, speakers):
    aliasTable = oldAliasTable
    connectionsTable = oldConnectionsTable #Initialized at new graph if nothing is loaded
    aliases=oldAliases #Initialized at new graph if nothing is loaded
    honorifics, female_honorifics, male_honorifics = get_honorifics()
    for honorific in honorifics:
        if honorific not in nameparser.config.CONSTANTS.titles:
            nameparser.config.CONSTANTS.titles.add(honorific)
            nameparser.config.CONSTANTS.titles.add(honorific.lower())
    honorifics = nameparser.config.titles.TITLES
    names_corpus = nltk.corpus.names
    male_names = names_corpus.words('male.txt')
    female_names = names_corpus.words('female.txt')
        
    #Second pass,check all canonical names from chunks headed by a proper name

    for i in range(len(speakers)):
        for canonical_name in speakers[i]:
            if canonical_name != "":
                if canonical_name not in connectionsTable:        
                    gender, name_category, name =categorize_name(canonical_name, male_honorifics, female_honorifics, male_names, female_names, connectionsTable)
                    connectionsTable.add_node(canonical_name)
                    connectionsTable.nodes[canonical_name]["gender"] = gender
                    connectionsTable.nodes[canonical_name]["name_category"] = name_category
                    connectionsTable.nodes[canonical_name]["name"] = name
                    connectionsTable.nodes[canonical_name]["value"] = 1 
                    #if name is composed, keep all the component in the database to identify aliases
                    if len(canonical_name.split()) >0:
                        for alias in canonical_name.split():
                            if alias not in connectionsTable:
                                gender, name_category, name =categorize_name(alias, male_honorifics, female_honorifics, male_names, female_names, connectionsTable)
                                connectionsTable.add_node(alias)
                                connectionsTable.nodes[alias]["gender"] = gender
                                connectionsTable.nodes[alias]["name_category"] = name_category
                                connectionsTable.nodes[alias]["name"] = name
                                connectionsTable.nodes[alias]["value"] = 0
                                connectionsTable.add_edge(canonical_name, alias, paired = 2  )
                else:
                    connectionsTable.nodes[canonical_name]["value"] += 1 
                    
    aliases.add_nodes_from(connectionsTable.nodes())
    for name, data in connectionsTable.nodes(data = True):
        if data["value"] == 0:
            subAT= {s: connectionsTable.nodes[s]["value"] for s in connectionsTable.neighbors(name)}
            maxMentions = max(subAT, key=subAT.get)
            aliases.add_edge(name, maxMentions)
            connectionsTable.add_edge(name, maxMentions, paired = 1)

    print("graph made")            
    return aliasTable, connectionsTable, aliases

def categorize_name(canonical_name, male_honorifics, female_honorifics, male_names, female_names, connectionsTable):
    name = nameparser.HumanName(canonical_name)                    
    gender = 0
    for i in range(len(name.title_list)):
        honorific = name.title_list[i]
        if honorific[-1] == ".":
            honorific = honorific[:-1]
        if honorific in female_honorifics:
            gender -= 1
        elif honorific in male_honorifics:
            gender += 1
    if name.first != "":
        if name.first in male_names:
            gender +=1
        elif name.first in female_names:
            gender -=1
    if gender > 0:
        gender = 1
    elif gender < 0:
        gender = -1
    name_category = 6 #default 6: only title
    if name.title != "" and name.first != "" and name.last != "":
        name_category = 1
    elif name.first != "" and name.last != "":
        name_category = 2
    elif name.title != "" and name.first != "":
        name_category = 3
    elif name.title != "" and name.last != "":
        name_category = 4 
    elif name.first != "" or name.last != "" :
        name_category = 5
    return gender, name_category, name
 