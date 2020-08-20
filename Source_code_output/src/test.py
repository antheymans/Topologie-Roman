import spacy 
f=open("harry_potter_1.txt", "r")
text = f.read()
proper_nouns = {}
nlp = spacy.load('en_core_web_sm',disable=['parser', 'tagger', 'textcat'])   
for ent in nlp(text).ents:
    if ent.label_ == "PERSON":
        print(ent.text)
        if ent.text not in proper_nouns:
            proper_nouns[ent.text] = 0
        else:
            proper_nouns[ent.text] += 1

print(proper_nouns)
exit()