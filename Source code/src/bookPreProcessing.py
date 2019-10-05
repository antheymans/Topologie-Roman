#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#Pre-processing library using CLiPS Pattern and unicode

import bookInputOutput as bIO
import pattern.text.en as pen
import codecs
import re
import os
from helpers import PATH_BOOKS, PATH_BOOKS_OBJECT

EMPTY_STRING=re.compile('\s+',re.U)

def readBook(path):
    """
    Read a UTF-8 book in text format
    """
    f = codecs.open(path, encoding='utf-8')
    book = [line for line in f]
    replacements = [(u"‘",unicode("'")),(u"’",unicode("'")),(u"—",unicode("-")),(u'“',unicode('"')),
                    (u'”',unicode('"')),(u'…',unicode('... '))]
    for replacement in replacements:
        book = [line.replace(replacement[0],replacement[1]) for line in book]
    return book

def getSentences(book):
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
            parsedLine = pen.parsetree(line,relations=True)
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

def getBreaks(sentences):
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

def buildBook(path):
    book = readBook(path)
    print "Book read!"
    sentences, chunks = getSentences(book)
    print "Sentences extracted!"
    #indices = range(len(sentences))
    #print "Indices generated!"
    breaks = getBreaks(sentences)
    print "Scene and chapter breaks identified!"
    sentiments = [pen.sentiment(sentence) for sentence in sentences]
    print "Sentiments extracted!"
    #return sentences, indices, breaks, chunks, sentiments
    return sentences, breaks, sentiments, chunks



def preProcess(override):
    #Build a book collection
    files = bIO.get_files_in_folder(PATH_BOOKS)

    for f in files:
        if (os.path.isfile(PATH_BOOKS_OBJECT+f[:-4]+".book") and not override):
            print "File",f[:-4]+".book","already exists"
        else:
            print "Creating object for",f[:-4]
            book = buildBook(PATH_BOOKS+f)
            bIO.setObject(book,PATH_BOOKS_OBJECT+f[:-4]+".book")
            print "Book object created for",f[:-4]
    print "Done!"

if __name__ == '__main__':
    preProcess(override = False)
    """
    sentences, breaks, sentiments, chunks = bIO.getObject("../books_objects/Harry_Potter_1.book")
    print chunks[20]
    """
    #path = '../books_raw/Harry_Potter_1.txt'
    #sentences, breaks, sentiments, chunks = buildBook(path)
    #print len(sentences), len(breaks), len(sentiments), len(chunks)
    #for i in range(3,60):
        #print sentences[i]
        #print breaks[i]
        #print sentiments[i]
        #chunk = chunks[i]
        #print [s.relations for s in chunk]
    #bIO.setObject([sentences, breaks, sentiments, chunks],"../books_objects/Harry_Potter_1.book")
    """
    sentences, indices, breaks, chunks, sentiments = bIO.getObject("../books_objects/Harry_Potter_1.book")
    for i in range(0,100):
        s = sentences[i].split('"')
        print s
        if s[0] == unicode(''): 
            print "yay", [s[i] for i in range(len(s)) if i%2 == 1]
        else:
            print "boo", [s[i] for i in range(len(s)) if i%2 == 0]
        #print indices[i]
        #print breaks[i]
        #print chunks[i]
        #print sentiments[i]
    """
    """
    book = getSentences(readBook('../books_raw/Harry_Potter_1.txt'))[70:76]
    #book = [unicode("He couldn't be more happy. He'd never been this pleased. He'd rather not do that.")]
    for sentence in book:
        #Would-be PRPNNP extraction function
        ##Return all the chunks and let the characterID do the actual identification
        tag = pen.tag(sentence)
        chunk = pen.parsetree(sentence, relations=True)
        print sentence
        print [s.string for s in chunk.sentences]
        sbjobj = [s.relations['SBJ'][key] for s in chunk.sentences for key in s.relations['SBJ'].keys()]
        sbjobj.extend([s.relations['OBJ'][key] for s in chunk.sentences for key in s.relations['OBJ'].keys()])
        print [(s,s.head.type) for s in sbjobj]
        print [c for s in chunk.sentences for c in s.chunks]# if c.head.type == 'NNP']
    """