#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Library handling the character identification and alias resolution

from collections import Counter
import networkx as nx
import pattern.text.en as pen
import name_tools

from helpers import is_root, uniques

###############################################################
# Alias table functions
###############################################################
def is_valid(word):
    if word[0] != word[0].upper() or word == word.upper() or len(word) <= 2:
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

    from pattern.en.wordlist import ACADEMIC, BASIC, PROFANITY, TIME
    proper_nouns = {}
    for c in chunks:
        if c.head.type.find('NNP')==0 and c.head.type != "NNP-LOC" and is_valid(c.head.string):
            name = c.head.string
            if (c != c.sentence.chunk[0] or c.words[0].string != name) and name.lower() not in BASIC and name.lower() not  in ACADEMIC and name.lower() not in PROFANITY and name.lower() not in TIME:
                if name not in proper_nouns:
                    proper_nouns[name] = 1
                else:
                    proper_nouns[name] += 1

    
    proper_names = list(proper_nouns)
    connectionsTable.add_nodes_from(proper_names, proper_name = 1)
    #Second pass, make connections with the non-head words of a chunk
    for c in chunks:
        if c.head.string in proper_names:
            detected = 0
            chunk_name_list = []
            canonical_name_list = []#' '.join(canonical_name)
            
            for w in c.words:
                if is_valid(w.string):
                    detected = 1
                    canonical_name_list.append(w.string)
                elif detected == 1:
                    chunk_name_list.append(canonical_name_list)
                    canonical_name_list = []
                    detected = 0
                    
            if detected == 1:
                chunk_name_list.append(canonical_name_list)
                    
            for canonical_name_list in chunk_name_list:
                canonical_name = ' '.join(canonical_name_list)
                if aliasTable.get(canonical_name,0)==0:
                    aliasTable[canonical_name]=[c.string]
                else:
                    aliasTable[canonical_name].append(c.string)
                if len(canonical_name_list) > 1:    
                    for word in canonical_name_list:   
                        if word in proper_names:
                            if connectionsTable.has_edge(canonical_name, word):
                                connectionsTable[canonical_name][word]["value"] += 1
                            else:
                                connectionsTable.add_edge(canonical_name, word, value=1, paired=False)
                elif canonical_name not in connectionsTable:
                    connectionsTable.add_node(canonical_name)
    #update information in connection_table
    for name, data in connectionsTable.nodes(data = True):
        if "proper_name" not in data:
            connectionsTable.nodes(data=True)[name]["proper_name"] = 0
        if name in aliasTable:
            connectionsTable.nodes(data=True)[name]["canonical_name"] = 1
        else:
            connectionsTable.nodes(data=True)[name]["canonical_name"] = 0
              
    ##check that list are coherent, generate an error if not| OPTIONNAL
    for key in list(aliasTable.keys()):
        if len(aliasTable[key]) == 0:
            aliasTable.pop(key)
            print(key, "error key, no chunks associated")
    
    for n, data in connectionsTable.nodes(data = True):
        if data["canonical_name"] == 1 and n not in list(aliasTable.keys()):
            #connectionsTable.remove_node(n)
            print(n, "error canonical name in connection table")
        if data["proper_name"] == 1 and n not in proper_nouns:
            #connectionsTable.remove_node(n)
            print(n, "error proper name in connection table")
        if data["proper_name"] == 0 and data["canonical_name"] == 0:
            #connectionsTable.remove_node(n)
            print(n, "error useless name in connection table")

    #count the number of occurence of each canonical name
    for name, data in connectionsTable.nodes(data = True):
        if data["canonical_name"] == 1:
            connectionsTable.add_node(name, length=len(aliasTable[name])) 
        else:
            connectionsTable.add_node(name, length=0)
    ## add the node in an alias network        
    aliases.add_nodes_from(connectionsTable.nodes(data = True))

    ## note as pair the nodes being linked most of the time
    connectionNodes = {n[0]: n[1] for n in connectionsTable.nodes(data=True)}

    for e in list(connectionsTable.edges(data=True)):
        n1 = e[0]
        n2 = e[1]
        value = e[2]['value']
        l1 = connectionNodes[n1]['length'] 
        l2 = connectionNodes[n2]['length']
        if value > min(l1,l2)/3.0:
            e[2]["paired"] = True
            
    validate_connections_table(connectionsTable, aliasTable, aliases)
    exit()
    return aliasTable, connectionsTable, aliases

def validate_connections_table(connectionsTable, aliasTable, aliases):
    pairGraph = nx.Graph()
    cT2 = nx.Graph()
    
    names = list(aliases.nodes())
    ##Via name similarity
    for name in names:
        for n in names[names.index(name)+1:]:
            if is_root(name,n):
                pairGraph.add_edge(name,n)
    
    for e in list(connectionsTable.edges(data=True)) :
        if e[0] in list(aliasTable.keys()) and e[1] in list(aliasTable.keys()) and e[2]["paired"]:
            cT2.add_edge(e[0],e[1])
    
    pairGraph.add_edges_from([e for e in cT2.edges() if len(list(cT2.neighbors(e[0])))==1 and len(list(cT2.neighbors(e[1])))==1])
    
    used = {w : False for w in pairGraph.nodes()}
    for w in pairGraph.nodes():
        if not used[w] and len(list(pairGraph.neighbors(w))) > 0:#look at ngbhr from unmarked node
            subgraph = [w]
            subgraph.extend(pairGraph.neighbors(w))
            subAT= {s: aliases.nodes(data = True)[s]["length"] for s in subgraph}
            maxMentions = max(subAT, key=subAT.get)
            for w2 in [s for s in subgraph if s != maxMentions and not used[s]]:
                aliases.add_edge(w2, maxMentions)
                if w2 in cT2:
                    cT2.remove_node(w2)
                used[w2] = True
            used[maxMentions] = True
            
    #try to takes "clusters" or pair each with his max nbgh ?
    used = {w : False for w in cT2.nodes()}
    for w in cT2.nodes():
        if not used[w] and len(list(cT2.neighbors(w))) > 0:#look at ngbhr from unmarked node
            subgraph = [w]
            subgraph.extend(cT2.neighbors(w))
            subAT= {s: aliases.nodes(data = True)[s]["length"] for s in subgraph}
            maxMentions = max(subAT, key=subAT.get)
            for w2 in [s for s in subgraph if s != maxMentions and not used[s]]:
                aliases.add_edge(w2, maxMentions)
                used[w2] = True
            used[maxMentions] = True
            
    ## takes shortcut
    
"""        
    for n in cT2.nodes():
        if cT2.degree()[n] > 1 :
            for ref in aliasTable[n]:
                tags = pen.tag(ref, model=None)
                otherRef= False
                for tag in tags:
                    if tag[0] != n and tag[1] == 'NNP':
                        otherRef = True
                        if tag[0] in list(aliasTable.keys()):
                            pass #already in the other entry by construction
                        elif tag[0] in list(toAppend.keys()):
                            toAppend[tag[0]].append(ref)
                        else:
                            toAppend[tag[0]] = [ref]
                if otherRef:
                    aliasTable[n].remove(ref)
            if len(aliasTable[n]) == 0:
                aliasTable.pop(n)
    
    for newName in list(toAppend.keys()):
        noAliases = True
        for n in list(aliasTable.keys()):
            if is_root(newName,n):
                aliasTable[n].extend(toAppend[newName])
                noAliases = False
        if noAliases:
            aliasTable[newName]= toAppend[newName]
"""    
    

            
def alias_lookup(canonical_name,aliasTable):
    cnames = []
    for key in list(aliasTable.keys()):
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
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.get)
        return maxMentionAlias
    else:
        return chunk
        
def alias_chunk_lookup(chunk,aliasTable):
    cnames = []
    for key in list(aliasTable.keys()):
        if chunk.string in aliasTable[key] or chunk.string == key:
            cnames.append(key)
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.get)
        return maxMentionAlias
    else:
        return chunk
        
  

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
   


           
    

###############################################################
# Extraction of speakers
###############################################################

def get_speakers_from_nearby_context(index,context_chunks,dialog_indices,aliasTable):
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
                pot_from.extend([alias_chunk_lookup(c,aliasTable) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
        if neg_incr:
            sc = context_chunks.get(index-incr,[])
            if len(sc) == 0:
                neg_incr = False
            else:
                pot_from.extend([alias_chunk_lookup(c,aliasTable) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
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

def uniformize_speakers(current_context_dialogs,aliasTable,context_chunks,dialog_indices):
    #Lookups in the alias table
    new_from = []
    new_to = []
    for o in current_context_dialogs:
        nf = []#new_from
        nt = []
        for f in o['from']:
            fl = alias_lookup(f,aliasTable)
            if len(fl) > 0:
                nf.append(fl)
                o['from'].remove(f)
        for t in o['to']:
            tl = alias_lookup(t,aliasTable)
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
            new_from[index] = get_speakers_from_nearby_context(current_context_dialogs[index]['index'],context_chunks,dialog_indices,aliasTable)
    
    trim_new_from(new_from)
    
    #List of all speakers within the context
    speakers, speakersMention = update_speakers(new_from)
    
    for index in range(len(current_context_dialogs)):
        if len(new_from[index]) == 0:
            if len(speakers) == 0:
                new_from[index] = get_speakers_from_nearby_context(current_context_dialogs[index]['index'],context_chunks,dialog_indices,aliasTable)
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
        current_context_dialogs = uniformize_speakers(current_context_dialogs, aliasTable,context_chunks,dialog_indices)
    
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