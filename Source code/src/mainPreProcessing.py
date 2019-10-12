import bookInputOutput as bIO
import bookPreProcessing as bPP
import os.path

def preprocess(override):
    #Build a book collection
    #Main function for preprocess
    files = bIO.get_files_in_folder(PATH_BOOKS)

    for f in files:
        if (os.path.isfile(PATH_BOOKS_OBJECT+f[:-4]+".book") and not override):
            print "File",f[:-4]+".book","already exists"
        else:
            print "Creating object for",f[:-4]
            book = bPP.build_book(PATH_BOOKS+f)
            bIO.set_object(book,PATH_BOOKS_OBJECT+f[:-4]+".book")
            print "Book object created for",f[:-4]
    print "Done!"

if __name__ == '__main__':
    preprocess(override = False)



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