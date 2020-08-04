#!/usr/bin/python3.6# -*- coding: utf-8 -*-

#Pre-processing library using CLiPS Pattern and unicode


import codecs
import re
import pattern.text.en as pen

from helpers import PATH_BOOKS, PATH_BOOKS_OBJECT

EMPTY_STRING=re.compile('\s+',re.U)
SCRIPT_SPEAKER =re.compile('_',re.U)
DIALOG = re.compile('^"',re.U)

def read_book(path):
    """
    Read a UTF-8 book in text format
    """
    f = codecs.open(path, encoding='utf-8')
    #book = f.read()
    book = [line for line in f]
    replacements = [("‘",str("'")),("’",str("'")),("—",str(" - ")),('“',str('"')),
                    ('”',str('"')), ('…',(' ... ')), ('...',(' ... ')), (",", " , ")]
    
    for replacement in replacements:
        book = [line.replace(replacement[0],replacement[1]) for line in book] 
    return book

def get_sentences(book):
    """
    Uses the CLiPS Pattern parse tree to get individual sentences and chunks
    """
    sentences = []
    chunks = []
    speakers = []
    speaker = []
    script = False
    for line in book:
        if EMPTY_STRING.match(line):
            sentences.append(line)
            chunks.append([])
            speakers.append("")            
        elif SCRIPT_SPEAKER.match(line):
            wordlist = line[1:-1].split("(")[0].replace('.', '').replace(';', '').replace('V/0', '').replace('-', ' - ').split()
            for i in range(len(wordlist)):
                wordlist[i] = wordlist[i].capitalize()
            speaker = []
            for elem in re.split(' And |, |/', ' '.join(wordlist)):  
                if len(elem) > 1:
                    speaker.append(elem)
            script = True
        else:
            parsedLine = pen.parsetree(line, relations=True, encoding = "utf-8", model = None)
            #Regroup a whole dialogue into a single sentence
            to_ignore = []
            for i in range(len(parsedLine.sentences)):
                if i not in to_ignore:
                    sentence = parsedLine.sentences[i].string
                    chunk = [parsedLine.sentences[i]]
                    if sentence.count('"')%2 == 1:
                        for j in range(i+1, len(parsedLine.sentences)):
                            sentence += " "+parsedLine.sentences[j].string
                            chunk.append(parsedLine.sentences[j])
                            to_ignore.append(j)
                            if sentence.count('"')%2 == 0:
                                break
                    sentences.append(sentence)
                    chunks.append(chunk)
                    if DIALOG.match(line):
                        speakers.append(speaker)
                    else:
                        speakers.append([])
    return sentences, chunks, speakers, script

def get_breaks(sentences):
    """
    Return whether or not each sentence in a list is a chapter break (empty lines)
    """
    breaks = []
    for sentence in sentences:
        if EMPTY_STRING.match(sentence):
            breaks.append(True)
        else:
            breaks.append(False)
    return breaks

def get_speaker(sentences):
    """
    Return whether or not each sentence in a list is a speaker description (for scripts)
    """
    speaker = []
    for sentence in sentences:
        if SCRIPT_SPEAKER.match(sentence):
            speaker.append(True)
        else:
            speaker.append(False)
    return speaker
    
def build_book(path):
    book = read_book(path)
    print("Book read!")
    #book = solve_coreference(book)
    #print("coreference extracted")
    sentences, chunks, speakers, script = get_sentences(book)
    print("Sentences extracted!")
    breaks = get_breaks(sentences)
    print("Scene and chapter breaks identified!")
    sentiments = [pen.sentiment(sentence) for sentence in sentences]
    print("Sentiments extracted!")
    return sentences, breaks, sentiments, chunks, speakers, script



## Solve coreference and replace them in the text
## Actually takes a lot of time and lead to worst result
def solve_coreference(book):
    import time 
    tmps1=time.time()
    
    import spacy
    import neuralcoref
    
    nlp = spacy.load("en_core_web_sm")
    text = "*".join( book )
    print("Coreference resolution ...")
    neuralcoref.add_to_pipe(nlp, greedyness=0.5, max_dist = 1, max_dist_match = 100, blacklist = False, store_scores = False)
    doc = nlp(text)
    text = doc._.coref_resolved
    book = text.split("*")
    """
    #Line per line analysis
    for line in book:
        doc = nlp(line)
        line = doc._.coref_resolved
    """
    
    tmps2=time.time()-tmps1
    print("Temps d'execution = %f" %tmps2)
    return book
    
