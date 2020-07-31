#!/usr/bin/python3.6# -*- coding: utf-8 -*-

#Library containing constants and uncategorized functions called from various modules

PATH_BOOKS_OBJECT = "../books_objects/"
PATH_BOOKS = "../books_raw/"
PATH_CSV = "../csv/"
PATH_PNG = "../png/"
PATH_SERIALIZED = "../serialized/"
PATH_GRAPHS = "../graphs/"
PATH_CORRECTED = "../corrected_occurrences/"



def uniques(liste):
    """
    Return a list with removed duplicates
    """
    l = []
    for li in liste:
        if li in l:
            pass
        else:
            l.append(li)
    return l

###############################################################
# Word manipulation functions
###############################################################

def crop_word(word):
    if len(word) <= 4:
        return word
    import re
    DIMINUTIVE_ENDINGS=r'ie|y'
    croppedWord =re.sub(r'(.*)('+DIMINUTIVE_ENDINGS+r')$',r'\1',word,re.U).lower()
    if croppedWord[-1] == croppedWord[-2]:
        croppedWord = croppedWord[:-1]
    return croppedWord

def is_root(word1,word2):
    import pattern.text.en as pen
    
    if len(word1) <= 2 or len(word2) <=2:
        return False
    if pen.singularize(word1) == pen.singularize(word2):##if one word is plural of another
        return True
    if word1.find(word2) == 0 or word2.find(word1) == 0:
        return True
    
    croppedWord1 =crop_word(word1)
    croppedWord2 =crop_word(word2)
    f12 = word1.find(croppedWord2)
    f21 = word2.find(croppedWord1)
    if f12!=-1:
        if f21!=-1:
            return True
        if f12 == 0:
            return True
        if not word1[f12-1].isalnum():
            return True
    if f21!=-1:
        if f12!=-1:
            return True
        if f21 == 0:
            return True
        if not word2[f21-1].isalnum():
            return True
    return False

###############################################################
# Statistic of dialog occurence computation function
###############################################################
    
def compute_statistics(dialog_occurrences):
    """
    Print statistics of identified and unidentified in the dialog_occurrences
    """   
    cUnk = 0
    cOth = 0
    for d in dialog_occurrences:
        if d['from'] == []:
            cUnk += 1
        else:
            cOth += 1
    percentID = (1.0*cOth)/(cOth+cUnk)*100
    print("Statistics : "+str(percentID)+ "% of recognized [UNKNOWN, Identified] = ["+str(cUnk)+","+str(cOth)+"]")
    return percentID

def compute_statistics_CID(dialog_occurrences):
    """
    Print statistics of identified and unidentified in the dialog_occurrences
    """   
    cUnk = 0
    cOth = 0
    for d in dialog_occurrences:
        if len(d['from']) == 0:
            cUnk += 1
        else:
            cOth += 1
    percentID = (1.0*cOth)/(cOth+cUnk)*100
    print("Statistics CID: "+str(percentID)+ "% of recognized [UNKNOWN, Identified] = ["+str(cUnk)+","+str(cOth)+"]")
    return percentID

def extract_name_from_chunk(chunk):
        name_list = []
        wordlist = []
        detected = 0#no from detected, 1 from detected , -1 from already detected: looking for a second one
        for word in chunk.words:
            if word.string[0] == word.string[0].upper() or word == chunk.head:
                if detected == -1:
                    name_list.append(' '.join(wordlist))
                    wordlist = []
                detected = 1
                wordlist.append(word.string)
            elif detected == 1:
                detected = -1
        name_list.append(' '.join(wordlist))
        return name_list
