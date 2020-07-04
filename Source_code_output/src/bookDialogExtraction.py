#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import pattern.text.en as pen
from collections import Counter

from helpers import extract_name_from_chunk
###############################################################
# Build the dialog_spacing map 
# (has to be done independently to extract the threshold value)
###############################################################

def spacing_map(sentences,breaks):
    dialog_spacing = []    
    previousIndex = 0
    sceneBreak = True
    for index in range(len(sentences)):
        if breaks[index]:
            sceneBreak = True
        elif '"' in sentences[index]:
            if (sceneBreak): #First dialog after a scene break
                dialog_spacing.append((index,0))
            else:
                dialog_spacing.append((index,index-previousIndex))
            sceneBreak = False
            previousIndex = index     
    return dialog_spacing

#TODO: Make sure best option
def compute_threshold(dialog_spacing):
    count = Counter([s[1] for s in dialog_spacing])
    max_spacing = max(count.keys())
    first_zero = max_spacing+1
    for i in range(1,max_spacing):
        if count.get(i,0)==0:
            first_zero=i
            break
    m = 0
    for i in reversed(list(range(1,first_zero))):
        if count.get(i,0) > m:
            m =  count.get(i,0) 
            threshold = i
    for i in reversed(list(range(1,first_zero))):
        currCount = count.get(i,0)
        if currCount >= 100 or (currCount >=max(10,count.get(i+1,0)*2) and all ([count.get(j,0) > currCount for j in range(1,i)])):
            threshold = i
            break
    print("Threshold =",threshold)
    return threshold, count

###############################################################
# Context generation
###############################################################
def build_context(chunks, start, end):
    return [start,end,chunks[start:end]]

def get_contexts(chunks, breaks,dialog_spacing,threshold,length):
    dialog_contexts = []
    
    dialog_indices = [s[0] for s in dialog_spacing]
    
    d_start = 0
    
    for index in range(len(dialog_spacing)):
        space = dialog_spacing[index]
        if index == 0:
            prevSpace = 0
        else:
            prevSpace = dialog_indices[index-1]
        if space[1] == 0:#first sentence of a dialog
            for brIndex in reversed(list(range(space[0]))):
                if breaks[brIndex]:
                    break
            if len([i for i in range(d_start,brIndex) if i in dialog_indices]) > 0:
                dialog_contexts.append(build_context(chunks,d_start,brIndex))
            d_start = brIndex +1
            
        elif space[1] > threshold:
            dialog_contexts.append(build_context(chunks,d_start,space[0]))
            d_start = prevSpace+1
    
    if len([i for i in range(d_start,length) if i in dialog_indices]) > 0:
        dialog_contexts.append(build_context(chunks,d_start,length))
    
    return dialog_contexts

###############################################################
# Dialog occurrence building
###############################################################

def extract_agents(sentence):
    #We only consider dialogue
    s = sentence.split(str('"'))
    d_from=[]
    nnp_narration=[]
    d_to=[]
    
    for index in range(len(s)):
        ptree = pen.parsetree(s[index],relations=True,  encoding = "utf-8", model = None)
        if index%2 == 1: #Dialogue, extract objects
            d_to.extend([t.relations['SBJ'][key] for t in ptree.sentences for key in list(t.relations['SBJ'].keys())])
            d_to.extend([t.relations['OBJ'][key] for t in ptree.sentences for key in list(t.relations['OBJ'].keys())])
        elif len(ptree.sentences) > 0: #Not dialogue, extract potential speakers
            d_from.extend([t.relations['SBJ'][key] for t in ptree.sentences for key in list(t.relations['SBJ'].keys())])
            nnp_narration.extend([c for t in ptree.sentences for c in t.chunks if c.head.type.find('NNP')==0])
    
    if all([f.head.type.find('NNP')!=0 for f in d_from]):
        d_from.extend(nnp_narration)
        
    filtered_d_from = []
    for chunk in d_from:
        names = extract_name_from_chunk(chunk)
        filtered_d_from.extend(names)
        
        
    filtered_d_to = []
    for chunk in d_to:
        names = extract_name_from_chunk(chunk)
        filtered_d_to.extend(names)
        
    return filtered_d_from, filtered_d_to



def get_weight_from_sentiments(sentiment):
    """
    Extract weights from sentiment scores
    """
    #TODO: Make sure best formula
    polarity, subjectivity = sentiment
    return polarity

def get_occurrences(sentences, sentiments, dialog_spacing, dialog_contexts, speakers):
    dialog_occurrences = []
    dialog_indices = [s[0] for s in dialog_spacing]
    
    for i in range(len(dialog_indices)):
        index = dialog_indices[i]
        if i==0 or index*10//len(sentences) > dialog_indices[i-1]*10//len(sentences):
            print("Dialog metadata generation:", index*10//len(sentences)*10, "% completed...")
        sentence = sentences[index]
        
        #By construction, dialogs belong only to one context
        context = [j for j in range(len(dialog_contexts)) if (dialog_contexts[j][0] <= index and dialog_contexts[j][1] > index)][0] 
        
        #Dialog occurrence building
        d_from, d_to = extract_agents(sentence)
        if speakers[index] != []:
            d_from.extend(speakers[index])
        d_sentiment = get_weight_from_sentiments(sentiments[index])
        dialog_occurrence = {'from': d_from, 'to': d_to, 'sentiment': d_sentiment, 
                             'sentence': sentence, 'index': index, 'context': context}
        
        dialog_occurrences.append(dialog_occurrence)
        #print("sentence ",sentence, "speaker ", speakers[index], d_from, d_to)
        
    
    print("Dialog metadata generation: 100% completed!")
    return dialog_occurrences

###############################################################
# Main dialog extraction method
###############################################################

def dialog_extraction(sentences, breaks, sentiments, chunks, speakers):
    dialog_spacing = spacing_map(sentences,breaks)
    threshold, count = compute_threshold(dialog_spacing)
    
    dialog_contexts = get_contexts(chunks, breaks,dialog_spacing,threshold,len(sentences))
    print("Context generation complete...")
    dialog_occurrences = get_occurrences(sentences, sentiments, dialog_spacing, dialog_contexts, speakers)
    
    return dialog_spacing, dialog_occurrences, dialog_contexts, count, threshold
