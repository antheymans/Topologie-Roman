#!/usr/bin/python3.6# -*- coding: utf-8 -*-

import nltk.sem.drt as drt
import pattern.text.en as pen

import networkx as nx

from helpers import is_root
from bookCharacterIdentification import build_alias_table

context = ["Mr. and Mrs. Dursley , of number four , Privet Drive , were proud to say that they were perfectly normal , thank you very much .",
"They were the last people you 'd expect to be involved in anything strange or mysterious , because they just did n't hold with such nonsense .",
"Vernon Dursley was the director of a firm called Grunnings , which made drills .",
"He was a big , beefy man with hardly any neck , although he did have a very large mustache .",
"Petunia Dursley was thin and blonde and had nearly twice the usual amount of neck , which came in very useful as she spent so much of her time craning over garden fences , spying on the neighbors .",
"The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere .",
"The Dursleys had everything they wanted , but they also had a secret , and their greatest fear was that somebody would discover it .",
"They did n't think they could bear it if anyone found out about the Potters .",
"Mrs. Potter was Mrs. Dursley 's sister , but they had n't met for several years ; in fact , Mrs. Dursley pretended she did n't have a sister , because her sister and her good-for-nothing husband were as unDursleyish as it was possible to be .",
"The Dursleys shuddered to think what the neighbors would say if the Potters arrived in the street .",
"The Dursleys knew that the Potters had a small son , too , but they had never even seen him .",
"This boy was another good reason for keeping the Potters away ; they did n't want Dudley mixing with a child like that .",
"When Mr. and Mrs. Dursley woke up on the dull , gray Tuesday our story starts , there was nothing about the cloudy sky outside to suggest that strange and mysterious things would soon be happening all over the country .",
"Harry hummed as he picked out his most boring tie for work , and Mrs. Dursley gossiped away happily as she wrestled a screaming Dudley into his high chair .",
"None of them noticed a large , tawny owl flutter past the window .",
"At half past eight , Mr. Dursley picked up his briefcase , pecked Mrs. Dursley on the cheek , and tried to kiss Dudley good-bye but missed , because Dudley was now having a tantrum and throwing his cereal at the walls .",
'" Little tyke , " chortled Mr. Dursley as he left the house .',
"He got into his car and backed out of number four 's drive .",
"It was on the corner of the street that he noticed the first sign of something peculiar - a cat reading a map .",
"For a second , Mr. Dursley did n't realize what he had seen - then he jerked his head around to look again .",
"There was a tabby cat standing on the corner of Privet Drive , but there was n't a map in sight .",
"What could he have been thinking of ?",
"It must have been a trick of the light .",
"Mr. Dursley blinked and stared at the cat .",
"It stared back .",
"As Mr. Dursley drove around the corner and up the road , he watched the cat in his mirror .",
"It was now reading the sign that said Privet Drive - no , looking at the sign ; cats could n't read maps or signs .",
"Mr. Dursley gave himself a little shake and put the cat out of his mind .",
"As he drove toward town he thought of nothing except a large order of drills he was hoping to get that day .",
"But on the edge of town , drills were driven out of his mind by something else .",
"As he sat in the usual morning traffic jam , he could n't help noticing that there seemed to be a lot of strangely dressed people about .",
"People in cloaks .",
"Mr. Dursley could n't bear people who dressed in funny clothes - the getups you saw on young people !",
"He supposed this was some stupid new fashion .",
"He drummed his fingers on the steering wheel and his eyes fell on a huddle of these weirdos standing quite close by .",
"They were whispering excitedly together .",
"Mr. Dursley was enraged to see that a couple of them were n't young at all ; why , that man had to be older than he was , and wearing an emerald-green cloak !",
"The nerve of him !",
"But then it struck Mr. Dursley that this was probably some silly stunt - these people were obviously collecting for something…yes , that would be it .",
"The traffic moved on and a few minutes later , Mr. Dursley arrived in the Grunnings parking lot , his mind back on drills .",
"Mr. Dursley always sat with his back to the window in his office on the ninth floor .",
"If he had n't , he might have found it harder to concentrate on drills that morning .",
"He did n't see the owls swooping past in broad daylight , though people down in the street did ; they pointed and gazed open-mouthed as owl after owl sped overhead .",
"Most of them had never seen an owl even at nighttime .",
"Harry Potter , however , had a perfectly normal , owl-free morning .",
"He yelled at five different people .",
"He made several important telephone calls and shouted a bit more .",
"He was in a very good mood until lunchtime , when he thought he 'd stretch his legs and walk across the road to buy himself a bun from the bakery .",
"He 'd for gotten all about the people in cloaks until he passed a group of them next to the baker ' s. He eyed them angrily as he passed .",
"He did n't know why , but they made him uneasy .",
"This bunch were whispering excitedly , too , and he could n't see a single collecting tin .",
"It was on his way back past them , clutching a large doughnut in a bag , that he caught a few words of what they were saying ."]

if __name__ == '__main__':
    from networkx.algorithms.cluster import average_clustering
    G = nx.Graph()
    print(average_clustering(G))
    '''
    G.add_nodes_from(["A","B","C"])
    G.add_edge("A", "B", weight=0.5, mentions=1)
    G["A"]["B"]["weight"] += 0.25
    G["A"]["B"]["mentions"] += 1
    G["A"]["B"]["weight"] /=G["A"]["B"]["mentions"]
    G["A"]["B"].pop("mentions")
    H = nx.Graph()
    H.add_edge("A","B")
    for e in G.edges(data="True"):
        print H.has_edge(*e[0:2]) 
        '''
    '''ptree=[0,0]
    ptree.append([pen.parsetree(str) for str in context])
    aliasTable, aliases = build_alias_table([ptree])
    for key in aliasTable.keys():
        print key,":", aliasTable[key]
    print aliases
    for s in ptree[2][0].sentences[0].chunks:
        print s, s in aliasTable['Dursley']
    '''
    '''
    nnp = []
    for l in ptree[2]:
        for s in l.sentences:
            for c in s.chunks:
                if c.head.type.find('NNP')==0:
                    print c.head.string," -> ",c.string, [w.type for w in c]
                    if pen.singularize(c.head.string) not in nnp:
                        nnp.append(pen.singularize(c.head.string))
    print nnp
    '''