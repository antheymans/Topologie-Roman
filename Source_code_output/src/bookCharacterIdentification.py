#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Library handling the character identification and alias resolution

from collections import Counter
import networkx as nx
import pattern.text.en as pen

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
        sentence_chunks = c[2]
        for l in sentence_chunks:
            for s in l:
                chunks.extend(s.chunks)
        
    #First pass, isolate relevant proper nouns
    for c in chunks:
        if c.head.type.find('NNP')==0 and is_valid(c.head.string):
            name = c.head.string
            if aliasTable.get(name,0)==0:
                aliasTable[name]=[c.string]
                aliases.add_node(name)
            else:
                aliasTable[name].append(c.string)
    
    names = list(aliasTable.keys())
    #Second pass, make connections with the non-head words of a chunk
    for c in chunks:
        if c.head.type.find('NNP')==0 and is_valid(c.head.string): #Relevant chunks
            for w in c.words:
                if w != c.head:
                    name = w.string
                    if w.string in names:
                        aliasTable[name].append(c.string)
                        if connectionsTable.has_edge(name, c.head.string):
                            connectionsTable[name][c.head.string]["value"] += 1
                        else:
                            connectionsTable.add_edge(name, c.head.string, value=1, paired=False)
    
    for name in names:
        connectionsTable.add_node(name, length=len(aliasTable[name]))
    
    for key in list(aliasTable.keys()):
        if len(aliasTable[key]) == 0:
            aliasTable.pop(key)
    
    for n in connectionsTable.nodes():
        if n not in list(aliasTable.keys()):
            connectionsTable.remove_node(n)
            
    for n in aliases.nodes():
        if n not in list(aliasTable.keys()):
            aliases.remove_node(n)
    
    connectionNodes = {n[0]: n[1] for n in connectionsTable.nodes(data=True)}
    #Regroup entries of the dictionary corresponding to variations on the same name
    ##Via common references
    for e in list(connectionsTable.edges(data=True)):
        n1 = e[0]
        n2 = e[1]
        value = e[2]['value']
        l1 = connectionNodes[n1]['length'] 
        l2 = connectionNodes[n2]['length']
        if value > min(l1,l2)/3.0:
            e[2]["paired"] = True
                
    validate_aliases(aliases, aliasTable)
    validate_connections_table(connectionsTable, aliasTable)
    return aliasTable, connectionsTable, aliases

def alias_lookup(chunk,aliasTable):
    cnames = []
    for key in list(aliasTable.keys()):
        if chunk.string in aliasTable[key]:
            cnames.append(key)
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.get)
        return maxMentionAlias
    else:
        return ""

def filter_alias_table(aliasTable,occurrences):
    s_t = []
    for o in occurrences:
        s_t.append(o['from'])
        s_t.extend(o['to'])
    s_t = uniques(s_t)
    for name in list(aliasTable.keys()):
        if name not in s_t:
            aliasTable.pop(name)

def validate_connections_table(connectionsTable, aliasTable):
    pairGraph = nx.Graph()
    
    cT2 = nx.Graph()
    for e in list(connectionsTable.edges(data=True)) :
        if e[0] in list(aliasTable.keys()) and e[1] in list(aliasTable.keys()) and e[2]["paired"]:
            cT2.add_edge(e[0],e[1])
    
    pairGraph.add_edges_from([e for e in cT2.edges() if len(list(cT2.neighbors(e[0])))==1 and len(list(cT2.neighbors(e[1])))==1])
    
    used = {w : False for w in pairGraph.nodes()}
    
    for w in pairGraph.nodes():
        if not used[w] and len(list(pairGraph.neighbors(w))) > 0:
            subgraph = [w]
            subgraph.extend(pairGraph.neighbors(w))
            subAT= {s: len(aliasTable.get(s,[])) for s in subgraph}
            maxMentions = max(subAT, key=subAT.get)
            for w2 in [s for s in subgraph if s != maxMentions and not used[s]]:
                aliasTable[maxMentions].extend(aliasTable.pop(w2,[]))
                used[w2] = True
            used[maxMentions] = True
    
    toAppend = {}
    
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
    
    
def validate_aliases(aliases, aliasTable):
    names = list(aliasTable.keys())
    ##Via name similarity
    for name in names:
        for n in names[names.index(name)+1:]:
            if is_root(name,n):
                aliases.add_edge(name,n)
    
    used = {w : False for w in aliases.nodes()}
    
    for w in aliases.nodes():
        if not used[w] and len(list(aliases.neighbors(w))) > 0:
            subgraph = [w]
            subgraph.extend(aliases.neighbors(w))
            subAT= {s: len(aliasTable.get(s,[])) for s in subgraph}
            maxMentions = max(subAT, key=subAT.get)
            for w2 in [s for s in subgraph if s != maxMentions and not used[s]]:
                aliasTable[maxMentions].extend(aliasTable.pop(w2,[]))
                used[w2] = True
            used[maxMentions] = True
           
    

###############################################################
# Extraction of speakers
###############################################################

def get_speakers_from_nearby_context(index,sentence_chunks,dialog_indices,aliasTable):
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
            sc = sentence_chunks.get(index+incr,[])
            if len(sc) == 0:
                pos_incr = False
            else:
                pot_from.extend([alias_lookup(c,aliasTable) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
        if neg_incr:
            sc = sentence_chunks.get(index-incr,[])
            if len(sc) == 0:
                neg_incr = False
            else:
                pot_from.extend([alias_lookup(c,aliasTable) for s in sc for c in s.chunks if c.head.type.find('NNP')==0])
        
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

def uniformize_speakers(occurrences,aliasTable,sentence_chunks,dialog_indices):
    #Lookups in the alias table
    new_from = []
    new_to = []
    for o in occurrences:
        nf = []
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
    
    for index in range(len(occurrences)):
        neighbors = []
        if index > 0:
            neighbors.append(index-1)
        if index < len(occurrences)-1:
            neighbors.append(index+1)
        
        if len(new_from[index]) == 0 and all ([len(new_from[i]) == 0 for i in neighbors]):
            new_from[index] = get_speakers_from_nearby_context(occurrences[index]['index'],sentence_chunks,dialog_indices,aliasTable)
    
    trim_new_from(new_from)
    
    #List of all speakers within the context
    speakers, speakersMention = update_speakers(new_from)
    
    for index in range(len(occurrences)):
        if len(new_from[index]) == 0:
            if len(speakers) == 0:
                new_from[index] = get_speakers_from_nearby_context(occurrences[index]['index'],sentence_chunks,dialog_indices,aliasTable)
                speakers, speakersMention = update_speakers(new_from)
            elif len(speakers) == 1:
                new_from[index].append(speakers[0])
            elif len(speakers) == 2:
                other_s = []
                if index > 0:
                    other_s.append(new_from[index-1])
                if len(other_s) == 0 and index < len(occurrences):
                    other_s.append(new_from[index+1])
                new_from[index] = [s for s in speakers if s not in other_s]
            else :
                exclKeys = []
                if index > 0:
                    exclKeys.extend(new_from[index-1])
                if index < len(occurrences)-1:
                    exclKeys.extend(new_from[index+1])
                subSpeakers = {key: speakersMention[key] for key in speakers if key not in exclKeys}
                max_refs = max(subSpeakers,key=subSpeakers.get)
                new_from[index].append(max_refs)
    
    trim_new_from(new_from)
    
    for index in range(len(occurrences)):
        if len(new_from[index]) > 0:
            occurrences[index]['from'] = new_from[index][0]
        else:
            occurrences[index]['from'] = ''
        if len(new_to[index]) == 0:
            new_to[index].extend([s for s in speakers if s not in new_from[index]])
        occurrences[index]['to'] = uniques(new_to[index])
    
    return occurrences

###############################################################
# Main character identification function
###############################################################

def character_analysis(dialog_occurrences, dialog_contexts, oldAliasTable,oldConnectionsTable,oldAliases):
    aliasTable, connectionsTable, aliases = build_alias_table(dialog_contexts,oldAliasTable,oldConnectionsTable,oldAliases)
    print("Alias table created.")
    for index in range(len(dialog_contexts)):
        if index==0 or index*10//len(dialog_contexts) > (index-1)*10//len(dialog_contexts):
            print("Character analysis:", index*10//len(dialog_contexts)*10, "% completed...")
        
        context = dialog_contexts[index]
        occurrences = [d for d in dialog_occurrences if d['context']==index]
        #Each element = list of chunks
        sentence_chunks = {(i+context[0]):context[2][i] for i in range(len(context[2]))}
        dialog_indices = [o['index'] for o in occurrences]
        
        #Use the alias table to replace chunk objects by keys of the alias table
        occurrences = uniformize_speakers(occurrences, aliasTable,sentence_chunks,dialog_indices)
    
    print("Character analysis: 100 % completed...")
    filter_alias_table(aliasTable,dialog_occurrences)
    return aliasTable, connectionsTable, aliases
    
