#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Library handling the character identification and alias resolution

from collections import Counter
import networkx as nx
import pattern.text.en as pen
from pattern.en.wordlist import ACADEMIC, BASIC, PROFANITY, TIME
from copy import copy
import nltk
import nameparser

import ast

from helpers import is_root, uniques

###############################################################
# Alias table functions
###############################################################
def is_valid(word):
    if word[0] != word[0].upper() or word == word.upper():
        return False
    return True
def build_alias_table(dialog_contexts,oldAliasTable,oldConnectionsTable,oldAliases):
    aliasTable = oldAliasTable
    connectionsTable = oldConnectionsTable #Initialized at new graph if nothing is loaded
    aliases=oldAliases #Initialized at new graph if nothing is loaded
    chunks = []
    for c in dialog_contexts:
        context_chunks = c[2]
        for l in context_chunks:
            for s in l:
                chunks.extend(s.chunks)
    
    #First pass, isolate relevant proper nouns

    proper_nouns = {}
    locations = {}
    honorifics, female_honorifics, male_honorifics = get_honorifics()
    honorifics = nameparser.config.titles.TITLES
    for c in chunks:
        if c.head.type.find('NNP')==0 and is_valid(c.head.string):
            name = c.head.string
            if c.head.type == "NNP-LOC":
                if name not in locations:
                        locations[name] = 1
                    else:
                        locations[name] += 1
            else:
                if (c != c.sentence.chunk[0] or c.words[0].string != name) and name.lower() not in BASIC and name.lower() not  in ACADEMIC \
                    and name.lower() not in PROFANITY and name.lower() not in TIME and name not in honorifics:
                    if name not in proper_nouns:
                        proper_nouns[name] = 0
                    else:
                        proper_nouns[name] += 1
    
    for loc in locations:
        if loc in proper_nouns:
            print(loc)
            if locations[loc] >= proper_nouns[loc]:
                del proper_nouns[loc]
            else:
                del locations[loc]
    print("locations: ",locations)
            
    nicknames = get_nicknames()
    proper_names = list(proper_nouns)
    for name in names:
        for n in names[names.index(name)+1:]:
            nick = []
            if is_root(name,n):
                nick.add(n)
        if len(nick) > 0:
            nick.add(name)
            nicknames.add(nick)
    
    #create dict containing canonical name linked to each proper noun    
    canonical_names_dict = {}
    for proper_noun  in proper_names:
        canonical_names_dict[proper_noun] = []
        
    names_corpus = nltk.corpus.names
    male_names = names_corpus.words('male.txt')
    female_names = names_corpus.words('female.txt')
    
    #Second pass,check all canonical names from chunks headed by a proper name
    for c in chunks:
        if c.head.string in proper_names:
            detected = 0
            canonical_names_list = [] #list of canonical names
            wordlist = []# canonical name in a form of wordlist
            
            for w in c.words:
                if is_valid(w.string):
                    detected = 1
                    wordlist.append(w.string)
                elif detected == 1:
                    canonical_names_list.append(wordlist)
                    wordlist = []
                    detected = 0
                    
            if detected == 1:
                canonical_names_list.append(wordlist)
                    
            for wordlist in canonical_names_list:
                canonical_name = ' '.join(wordlist)
                
                if canonical_name not in connectionsTable:
                    aliasTable[canonical_name]=[c.string]
                    
                    for word in word_list:
                        if word in proper_names:
                            canonical_names_dict[word].append(canonical_name)
                    
                    name = nameparser.HumanName(canonical_name)
                    gender = 0
                    for honorific in name.title_list:
                        if honorific in female_honorifics:
                            gender -= 1
                        elif honorific in male_honorifics:
                            gender += 1
                    if name.firstname != "":
                        if name.firstname in male_names:
                            gender +=1
                        elif name.firstname in female_names:
                            gender -=1
                    if gender > 0:
                        gender = 1
                    elif gender < 0:
                        gender = -1
                    name_category = 5 #default 5: only first or lastname
                    if name.title != "" and name.firstname != "" and name.lastname != "":
                        name_category = 1
                    elif name.firstname != "" and name.lastname != "":
                        name_category = 2
                    elif name.title != "" and name.firstname != "":
                        name_category = 3
                    elif name.title != "" and name.lastname != "":
                        name_category = 4 
                    connectionsTable[canonical_name]["gender"] = gender
                    connectionsTable[canonical_name]["name_category"] = name_category
                    connectionsTable[canonical_name]["name"] = name
                    connectionsTable[canonical_name]["value"] = 1
                    
                else:
                    aliasTable[canonical_name].append(c.string)
                    connectionsTable[canonical_name]["value"] += 1 

    used = {w : False for w in proper_nouns}
    
    for proper_name in proper_nouns:
        if len(canonical_names_dict[proper_name]) == 0:
            del canonical_names_dict[proper_name]
            
    for canonical_name, data in connectionsTable.nodes(data = True):
        #Use all first_name, category 3 or 4 indicates that first_name/last name have not been separated properly
        if data["name"].category < 3: 
            firstname = data["name"].firstname
            if first_name != "" and used[first_name] == False:
                used[firstname] = True
                names_bucket = set()
                firstname_bucket = set()
                bucket.extend(canonical_names_dict[firstname])
                for cluster in nicknames:#check nickname associated
                    if first_name in cluster:
                        for nickname in cluster:
                            if nickname in proper_nouns:
                                names_bucket.extend(canonical_names_dict[nickname])
                                firstname_bucket.add(nickname)
                                used[nickname] = True
                if firstname[0] in proper_nouns:#check initial present
                    names_bucket.extend(canonical_names_dict[firstname[0]])
                    firstname_bucket.add(firstname[0])
                    used[firstname] = True
            for i in range(len(names_bucket)):
                for j in range(i+1, len(names_bucket)):    
                    if connectionsTable[bucket[i]]["gender"]*connectionsTable[bucket[j]]["gender"] != -1:#avoid to link male and female CN
                        if connectionsTable[bucket[i]]["name"].first in firstname_bucket and connectionsTable[bucket[j]]["name"].first in firstname_bucket:                        
                            if connectionsTable[bucket[i]]["name"].last == connectionsTable[bucket[i]]["name"].last:
                            
                                if connectionsTable[bucket[i]].gender == 0:
                                    connectionsTable[bucket[i]].gender = connectionsTable[bucket[j]].gender
                                elif connectionsTable[bucket[j]].gender == 0:
                                    connectionsTable[bucket[j]].gender = connectionsTable[bucket[i]].gender
                                    
                                connectionsTable.add_edge(bucket[i], bucket[j], "paired" = 1)                    
                            elif connectionsTable[bucket[i]]["name"].last == "" or connectionsTable[bucket[j]]["name"].last == "": 
                                connectionsTable.add_edge(bucket[i], bucket[j], "paired" = 2)
                                
                        elif connectionsTable[bucket[i]]["name"].first = "" or connectionsTable[bucket[j]]["name"].first = ""
                            connectionsTable.add_edge(bucket[i], bucket[j], "paired" = 2)
                        else:
                            print(connectionsTable[bucket[i]]["name"], connectionsTable[bucket[j]]["name"])
        
    for canonical_name, data in connectionsTable.nodes(data = True):
        lastname_list = data["name"].lastname_list
        for lastname in lastname_list:
            if lastname != "" and used[lastname] == False:
                bucket = set()
                bucket.extend(canonical_names_dict[lastname])
                if lastname[0] in proper_nouns:#check initial
                    bucket.extend(canonical_names_dict[lastname[0]])
                for i in range(len(bucket)):
                    for j in range(i+1, len(bucket)):
                        if connectionsTable[bucket[i]]["name"].first not in proper_names or connectionsTable[bucket[j]]["name"].firstnot in proper_names \
                            or connectionsTable[bucket[i]]["name"].last = "" or connectionsTable[bucket[j]]["name"].last = "":
                            connectionsTable.add_edge(bucket[i], bucket[j], "paired" = 2)
                        
    used = {w : False for w in connectionsTable.nodes}
    
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False and data["gender"] = 0:
            cluster = [canonical_name]
            candidates_edge = set()
            ## group paired nodes from the neutral cluster
            for edge, data2 in G.edges(canonical_name, data = True):
                if data2["paired"] == 1:
                    cluster.add(edge[1])
            ## group their non-neutral nbh using their edges
            for cn2 in cluster:    
                for edge, data2 in G.edges(canonical_name, data = True):                
                    if data2["paired"] == 2 and connectionsTable[edge[1]]["gender"] != 0 and edge[1]:
                        candidates.add(edge)
                        
            subAT= {s: connectionsTable[s[1]]["value"] for s in candidates}
            maxMentions = max(subAT, key=subAT.get)
            gender = connectionsTable[maxMentions[1]]["gender"]
            
            for edge in candidates_edge:
                if connectionsTable[edge[1]]["gender"] == gender:
                    connectionsTable[edge[0],edge[1]]["paired"] = 1
                else:
                    connectionsTable.remove_edge(edge[0],edge[1])
            for cn2 in cluster:
                connectionsTable[cn2]["gender"] = gender
                used[cn2] = True
        elif used[canonical_name] == False:
            gender = connectionsTable[canonical_name]["gender"]
            for nbh in connectionsTable.neighbors(canonical_name, data = True): 
                if connectionsTable[nbh]["gender"] * gender == -1:
                    connectionsTable.remove_edge(canonical_name,nbh)

    #directed graph containg arrow linked to main canonical name of a cluster
    aliases.add_nodes_from(connectionsTable.nodes(data = True))
    
    used = {w : False for w in connectionsTable.nodes}

    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False:  
            #add all neibhors and their neighbors recursively to our cluster
            cluster = []
            candidates = [canonical_name]
            while len(candidates) > 0:
                cluster.add(candidates[0])
                for nbh in connectionsTable.neighbors(canonical_name):
                    if nbh not in cluster:
                        candidates.add(nbh)
                        
            subAT= {s: connectionsTable[s]["value"] for s in cluster}
            maxMentions = max(subAT, key=subAT.get) 
            cluster.remove(maxMentions)
            for cn2 in cluster:
                aliases.add_edge(cn2, maxMentions)
                aliasTable[maxMentions].extend(aliasTable.pop(cn2,[]))
                used[cn2] = True
            used[maxMentions] = True
                
    return aliasTable, connectionsTable, aliases


    

            
def alias_lookup(canonical_name,aliasTable, aliases):
    cnames = []
    for key in list(aliases.nodes()):
        if canonical_name == key:
            cnames.append(key)
    #isolate words from canonical name if can_name is not found
    if len(cnames) == 0 and len(canonical_name) > 5:#name of >= 3letters + a space + new name ->possibility to have >=2 words
        word_list = canonical_name.split()
        if len(word_list)>1:#More than one word
            for word in word_list:
                for key in list(aliasTable.keys()):
                    if word == key:
                        cnames.append(key)
    for i in range(0, len(cnames)):
        if len(aliases[cnames[i]]) != 0:
            cnames[i] = list(aliases[cnames[i]])[0]
    
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.gget)
        return maxMentionAlias
    else:
        return ""
        
def alias_chunk_lookup(chunk,aliasTable,aliases):
    cnames = []
    for key in list(aliasTable.keys()):
        if chunk.string in aliasTable[key] or chunk.string == key:
            cnames.append(key)
    for i in range(0, len(cnames)):
        if len(aliases[cnames[i]]) != 0:
            cnames[i] = list(aliases[cnames[i]])[0]
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.get)
        return maxMentionAlias
    else:
        return ""
        
  

def filter_alias_table(aliasTable,current_context_dialogs):
    s_t = []
    for o in current_context_dialogs:
        s_t.append(o['from'])
        s_t.extend(o['to'])
    s_t = uniques(s_t)
    for name in list(aliasTable.keys()):
        if name not in s_t:
            print("filtered ", name)
            aliasTable.pop(name)
    
def get_honorifics():
    f = open("honorifics.txt", "r")
    string  = f.read()
    honorifics, female_honor, male_honor = ast.literal_eval(string)
    return honorifics, female_honor, male_honor
           
def get_nicknames():
    f = open("nicknames.txt, "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        strings.append(line.split())
    return strings

###############################################################
# Extraction of speakers
###############################################################

def get_speakers_from_nearby_context(index,context_chunks,dialog_indices,aliasTable, aliases):
    #Find the nearest sentence of narration that can provide potential information on the speaker
    pot_from = []
    pos_incr = True
    neg_incr = True
    
    incr = 0
    while (pos_incr or neg_incr) and len(pot_from) == 0:
        incr += 1
        if index+incr in dialog_indices:
            pos_incr = False
        if index-incr in dialog_indices:
            neg_incr = False
        if pos_incr:
            sc = context_chunks.get(index+incr,[])
            if len(sc) == 0:
                pos_incr = False
            else:
                pot_from.extend([alias_chunk_lookup(c,aliasTable, aliases) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
        if neg_incr:
            sc = context_chunks.get(index-incr,[])
            if len(sc) == 0:
                neg_incr = False
            else:
                pot_from.extend([alias_chunk_lookup(c,aliasTable, aliases) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
    return pot_from


def update_speakers(new_from):
    #Update the speakers list
    speakers = [nf[0] for nf in new_from if len(nf) > 0]
    speakersMention = Counter(speakers)
    speakers = uniques(speakers)
    return speakers, speakersMention


def trim_new_from(new_from):
    speakersMention = update_speakers(new_from)[1]
    
    #Trim from lists to only keep one speaker each
    for index in range(len(new_from)):
        if len(new_from[index]) > 1:
            subSpeakers = {key:speakersMention[key] for key in new_from[index]}
            max_refs = max(subSpeakers, key=subSpeakers.get)
            new_from[index] = [max_refs]

def uniformize_speakers(current_context_dialogs,aliasTable,aliases,context_chunks,dialog_indices):
    #Lookups in the alias table
    new_from = []
    new_to = []
    for o in current_context_dialogs:
        nf = []#new_from
        nt = []
        for f in o['from']:
            fl = alias_lookup(f,aliasTable, aliases)
            if len(fl) > 0:
                nf.append(fl)
                o['from'].remove(f)
        for t in o['to']:
            tl = alias_lookup(t,aliasTable, aliases)
            if len(tl) > 0:
                nt.append(tl)
                o['to'].remove(t)
        new_from.append(nf)
        new_to.append(nt)
    
    for index in range(len(current_context_dialogs)):
        neighbors = []
        if index > 0:
            neighbors.append(index-1)
        if index < len(current_context_dialogs)-1:
            neighbors.append(index+1)
        if len(new_from[index]) == 0 and all ([len(new_from[i]) == 0 for i in neighbors]):#no speaker identified in dialog or ngb
            new_from[index] = get_speakers_from_nearby_context(current_context_dialogs[index]['index'],context_chunks,dialog_indices,aliasTable, aliases)
    
    trim_new_from(new_from)
    
    #List of all speakers within the context
    speakers, speakersMention = update_speakers(new_from)
    
    for index in range(len(current_context_dialogs)):
        if len(new_from[index]) == 0:
            if len(speakers) == 0:
                new_from[index] = get_speakers_from_nearby_context(current_context_dialogs[index]['index'],context_chunks,dialog_indices,aliasTable, aliases)
                speakers, speakersMention = update_speakers(new_from)
            elif len(speakers) == 1:
                new_from[index].append(speakers[0])
            elif len(speakers) == 2:
                other_s = []
                if index > 0:
                    other_s.append(new_from[index-1])
                if len(other_s) == 0 and index < len(current_context_dialogs):
                    other_s.append(new_from[index+1])
                new_from[index] = [s for s in speakers if s not in other_s]
            else :
                exclKeys = []
                if index > 0:
                    exclKeys.extend(new_from[index-1])
                if index < len(current_context_dialogs)-1:
                    exclKeys.extend(new_from[index+1])
                subSpeakers = {key: speakersMention[key] for key in speakers if key not in exclKeys}
                max_refs = max(subSpeakers,key=subSpeakers.get)
                new_from[index].append(max_refs)
    
    trim_new_from(new_from)
    
    for index in range(len(current_context_dialogs)):
        if len(new_from[index]) > 0:
            current_context_dialogs[index]['from'] = new_from[index][0]
        else:
            current_context_dialogs[index]['from'] = ''
        if len(new_to[index]) == 0:
            new_to[index].extend([s for s in speakers if s not in new_from[index]])
        current_context_dialogs[index]['to'] = uniques(new_to[index])
    
    return current_context_dialogs

###############################################################
# Main character identification function
###############################################################

def character_analysis(dialog_occurrences, dialog_contexts, oldAliasTable,oldConnectionsTable,oldAliases):
    aliasTable, connectionsTable, aliases = build_alias_table(dialog_contexts,oldAliasTable,oldConnectionsTable,oldAliases)
    print("Alias table created.")
    for index in range(len(dialog_contexts)):
        if index==0 or index*10//len(dialog_contexts) > (index-1)*10//len(dialog_contexts):
            print("Character analysis:", index*10//len(dialog_contexts)*10, "% completed...")
        
        context = dialog_contexts[index]#[start,end,chunks[start:end]]
        current_context_dialogs = [d for d in dialog_occurrences if d['context']==index]#load dialogue of the actual context
        #Each element = list of chunks
        context_chunks = {(i+context[0]):context[2][i] for i in range(len(context[2]))}#dict: index: chunks of context

        dialog_indices = [o['index'] for o in current_context_dialogs]#index of the context chunks
        
        #Use the alias table to replace chunk objects by keys of the alias table
        current_context_dialogs = uniformize_speakers(current_context_dialogs, aliasTable, aliases, context_chunks,dialog_indices)
    
    print("Character analysis: 100 % completed...")
    filter_alias_table(aliasTable,dialog_occurrences)
    return aliasTable, connectionsTable, aliases #aliases: list with canonical names
    #alias_table, dict: canonical names -> chunk detected in context
    #connection table: link between canonical names and head_woord
    


    """             
    #import nltk.corpus as corpus
    #dict2 = corpus.brown.words()
    from nltk.corpus import wordnet

    #dict_name = corpus.names.words()    
    for c in chunks:
        if c.head.type.find('NNP')==0 and c.head.type != "NNP-LOC" and is_valid(c.head.string):
            #print(c.type,c.head, c.head.type, c.relations, c)            
            name = c.head.string
            #if (c.words[0].string == name):
            #    print(name, c.start, c.string, c.sentence.chunk[0].start)
            if (c != c.sentence.chunk[0] or c.words[0].string != name) and name.lower() not in BASIC and name.lower() not  in ACADEMIC and name.lower() not in PROFANITY and name.lower() not in TIME:
                if aliasTable2.get(name,0)==0:
                    aliasTable2[name]=[c.string]
                    aliasTable2[name]=[c.string]
                    
    names2 = list(aliasTable2.keys())
    for elem in names:
        if elem not in names2:
            print(elem)
    """