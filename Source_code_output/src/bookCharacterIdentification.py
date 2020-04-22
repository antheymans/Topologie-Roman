#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Library handling the character identification

from collections import Counter

from helpers import uniques, extract_name_from_chunk
import book_character_table_construction




###############################################################
# Identification of speakers from chunk
###############################################################
                            
def alias_lookup(canonical_name,aliasTable, aliases):
    cnames = []
    for key in list(aliases.nodes()):
        if canonical_name == key:
            cnames.append(key)
    #isolate words from canonical name if node is not found
    if len(cnames) == 0 and len(canonical_name) > 5:#name of >= 3letters + a space + new name ->possibility to have >=2 words
        word_list = canonical_name.split()
        if len(word_list)>1:#More than one word
            for word in word_list:
                for key in list(aliases.nodes()):
                    if word == key:
                        cnames.append(key)
    for i in range(0, len(cnames)):
        if len(aliases[cnames[i]]) != 0:
            cnames[i] = list(aliases[cnames[i]])[0]
    
    if len(cnames) > 0:
        keyMentions = {key: len(aliasTable[key]) for key in cnames}    
        maxMentionAlias = max(keyMentions, key = keyMentions.get)
        print(maxMentionAlias)
        return maxMentionAlias
    else:
        return ""
        
def alias_chunk_lookup(chunk,aliasTable,aliases):
    #for name in extract_name_from_chunk(chunk):
    #    alias_lookup(name,aliasTable, aliases)
    print(chunk)
    return alias_lookup(chunk,aliasTable, aliases)
    
        
  

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
                pot_from.extend([alias_chunk_lookup(name,aliasTable, aliases) for s in sc for c in s.chunks if c.head.type.find('NNP')==0 for name in extract_name_from_chunk(c)])
        if neg_incr:
            sc = context_chunks.get(index-incr,[])
            if len(sc) == 0:
                neg_incr = False
            else:
                pot_from.extend([alias_chunk_lookup(name,aliasTable, aliases) for s in sc for c in s.chunks if c.head.type.find('NNP')==0 for name in extract_name_from_chunk(c)])
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
# Unused character filtering
###############################################################

def filter_alias_table(aliasTable, connectionsTable, aliases, current_context_dialogs):
    s_t = []
    for o in current_context_dialogs:
        s_t.append(o['from'])
        s_t.extend(o['to'])
    s_t = uniques(s_t)
    for name in list(aliasTable.keys()):
        if name not in s_t:
            #print("filtered ", name)
            bucket = [name]
            bucket.extend(aliases.predecessors(name))
            aliases.remove_nodes_from(bucket)
            connectionsTable.remove_nodes_from(bucket)
            aliasTable.pop(name)
            
###############################################################
# Main character identification function
###############################################################

def character_analysis(dialog_contexts, dialog_occurrences, chunks, oldAliasTable,oldConnectionsTable,oldAliases, speakers):
    #aliasTable, connectionsTable, aliases = book_character_table_construction.build_alias_table_script(chunks, oldAliasTable,oldConnectionsTable,oldAliases, speakers)
    aliasTable, connectionsTable, aliases = book_character_table_construction.build_alias_table(chunks, oldAliasTable,oldConnectionsTable,oldAliases)
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
    filter_alias_table(aliasTable, connectionsTable, aliases, dialog_occurrences)
    return aliasTable, connectionsTable, aliases #aliases: list with canonical names
    #alias_table, dict: canonical names -> chunk detected in context
    #connection table: link between canonical names and head_woord
    


 