#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Pre-processing library using CLiPS Pattern and unicode


import codecs
import re
import pattern.text.en as pen

from helpers import PATH_BOOKS, PATH_BOOKS_OBJECT

EMPTY_STRING=re.compile('\s+',re.U)

def read_book(path):
    """
    Read a UTF-8 book in text format
    """
    f = codecs.open(path, encoding='utf-8')
    book = [line for line in f]
    replacements = [("‘",str("'")),("’",str("'")),("—",str("-")),('“',str('"')),
                    ('”',str('"')), ('…',(' ... '))]
                    ##,(u"\u2013", unicode("-")), (u"\u2306", unicode("e"))
    for replacement in replacements:
        book = [line.replace(replacement[0],replacement[1]) for line in book]
    return book

def get_sentences(book):
    """
    Uses the CLiPS Pattern parse tree to get individual sentences and chunks
    """
    sentences = []
    chunks = []
    for line in book:
        if EMPTY_STRING.match(line):
            sentences.append(line)
            chunks.append([])
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
    return sentences, chunks

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

def build_book(path):
    book = read_book(path)
    print("Book read!")
    sentences, chunks = get_sentences(book)
    print("Sentences extracted!")
    #indices = range(len(sentences))
    #print "Indices generated!"
    breaks = get_breaks(sentences)
    print("Scene and chapter breaks identified!")
    sentiments = [pen.sentiment(sentence) for sentence in sentences]
    print("Sentiments extracted!")
    #return sentences, indices, breaks, chunks, sentiments
    return sentences, breaks, sentiments, chunks


    
    
