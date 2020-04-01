import networkx as nx
import pattern.text.en as pen
from pattern.en.wordlist import ACADEMIC, BASIC, PROFANITY, TIME
import ast
import nameparser
import nltk


from helpers import is_root


###############################################################
# Alias table functions
###############################################################
def is_valid(word):
    if word[0] != word[0].upper() or word == word.upper():
        return False
    return True
    
def build_alias_table(sentence, oldAliasTable,oldConnectionsTable,oldAliases):
    aliasTable = oldAliasTable
    connectionsTable = oldConnectionsTable #Initialized at new graph if nothing is loaded
    aliases=oldAliases #Initialized at new graph if nothing is loaded
    chunks = []

    for l in sentence:
        for s in l:
            if isinstance(s, pen.Sentence):
                chunks.extend(s.chunks)
            else:
               print("error, wrong type ", type(s), type(l))
    
    #First pass, isolate relevant proper nouns
    proper_nouns = {}
    locations = {}
    honorifics, female_honorifics, male_honorifics = get_honorifics()
    for honorific in honorifics:
        if honorific not in nameparser.config.CONSTANTS.titles:
            nameparser.config.CONSTANTS.titles.add(honorific)
            nameparser.config.CONSTANTS.titles.add(honorific.lower())
           
    honorifics = nameparser.config.titles.TITLES
    verbs = get_verb_dependency()
    stop_words = get_stop_list()
    """
    for l in sentence:
        for s in l:    
            for verb in s.verbs:
                for line in verbs:
                    if verb.string == line[0] :
                        if line[1] == "nsubj":
                            print(verb.string, s.subjects)
                            break
                        else:
                            print(verb, line[1])
                        

    exit()
    """
    for c in chunks:
        if c.head.type.find('NNP')==0 and is_valid(c.head.string):
            name = c.head.string
            if c.head.type == "NNP-LOC":
                if name not in locations:
                    locations[name] = 1
                else:
                    locations[name] += 1
            else:
                if c.head != c.sentence.chunk[0].words[0] and name.lower() not  in ACADEMIC \
                    and name.lower() not in PROFANITY and name.lower() not in TIME\
                    and name.lower() not in stop_words and name not in honorifics:
                    if name not in proper_nouns:
                        proper_nouns[name] = 0
                    else:
                        proper_nouns[name] += 1
    #for all names that are both proper name and locations, choose the dominant use                    
    deleted_locations = []
    print("ambiguous locations:")
    for loc in locations:
        if loc in proper_nouns:
            print(loc)
            if locations[loc] >= proper_nouns[loc]// 4:
                print("confirmed")
                del proper_nouns[loc]
            else:
                print("proper name")
                deleted_locations.append(loc)
    for loc in deleted_locations:
        del locations[loc]
        
    print("locations: ",locations)
            

    
    #create dict containing canonical name linked to each proper noun    
    canonical_names_dict = {}
    proper_names = list(proper_nouns)

    for proper_noun  in proper_names:
        canonical_names_dict[proper_noun] = []
        
    names_corpus = nltk.corpus.names
    male_names = names_corpus.words('male.txt')
    female_names = names_corpus.words('female.txt')
    
    #Second pass,check all canonical names from chunks headed by a proper name
    for c in chunks:
        if c.head.string in proper_names:
            canonical_names_list = canonical_names_from_chunk(c, proper_names)        
            for wordlist in canonical_names_list:
                canonical_name = ' '.join(wordlist)
                if canonical_name not in connectionsTable:        
                    name = nameparser.HumanName(canonical_name)                    
                    gender = 0
                    for i in range(len(name.title_list)):
                        honorific = name.title_list[i]
                        if honorific[-1] == ".":
                            honorific = honorific[:-1]
                        if honorific in female_honorifics:
                            gender -= 1
                        elif honorific in male_honorifics:
                            gender += 1
                    if name.first != "":
                        if name.first in male_names:
                            gender +=1
                        elif name.first in female_names:
                            gender -=1
                    if gender > 0:
                        gender = 1
                    elif gender < 0:
                        gender = -1
                    name_category = 6 #default 6: only title
                    if name.title != "" and name.first != "" and name.last != "":
                        name_category = 1
                    elif name.first != "" and name.last != "":
                        name_category = 2
                    elif name.title != "" and name.first != "":
                        name_category = 3
                    elif name.title != "" and name.last != "":
                        name_category = 4 
                    elif name.first != "" or name.last != "" :
                        name_category = 5
                    
                    if name.first != "" and name.first not in proper_names:
                        if name.first.lower() not in BASIC and name.first.lower() not in ACADEMIC and name.first.lower() not in PROFANITY \
                            and name.first.lower() not in TIME and name.first not in locations and len(name.first.split()) == 1:
                            proper_names.append(name.first)
                            if c != c.sentence.chunk[0] or gender != 0:
                                #if begin of a sentence, firstname could be wrongly added
                                #but gender added mean that the name is well-labelled
                                proper_names.append(name.first)
                        else:
                            name_category = 6
                            
                    if name_category < 6:
                        connectionsTable.add_node(canonical_name)
                        connectionsTable.add_node(canonical_name)
                        connectionsTable.nodes[canonical_name]["gender"] = gender
                        connectionsTable.nodes[canonical_name]["name_category"] = name_category
                        connectionsTable.nodes[canonical_name]["name"] = name
                        connectionsTable.nodes[canonical_name]["value"] = 1                        
                        aliasTable[canonical_name]=[c.string]
                        for word in wordlist:
                            if word in canonical_names_dict:
                                canonical_names_dict[word].append(canonical_name)
                            else:
                                canonical_names_dict[word] = [canonical_name]
                    if name.first in proper_names and name.first not in canonical_names_dict.keys():
                        print("error proper name: ",name, name_category, name.first, wordlist, " chunk: ", c.words)
                    #else: #DEBUG 
                        #print(name_category, name.title,", first =", name.first,",last = ", name.last,"|", name)
                                
                else:
                    aliasTable[canonical_name].append(c.string)
                    connectionsTable.nodes[canonical_name]["value"] += 1 
    #del all name detected as proper but not related not any canonical name
    index = 0
    while index < len(proper_names):
        if len(canonical_names_dict[proper_names[index]]) == 0:
            del canonical_names_dict[proper_names[index]]
            proper_names.pop(index)
            #print("pop: ", proper_names.pop(index))
        index +=1
    #del all non proper name in the cnn dictionnary
    index = 0
    key_list = list(canonical_names_dict.keys())
    while index < len(key_list):
        if key_list[index] not in proper_names:
            del canonical_names_dict[key_list[index]]
        index +=1

    nicknames = get_nicknames()
    for name in proper_names:
        nick = []
        for n in proper_names[proper_names.index(name)+1:]:
            if is_root(name,n):
                nick.append(n)
        if len(nick) > 0:
            nick.append(name)
            nicknames.append(nick)        
                    
    #link between them canonical names sharing firstname
    #name sharing a 1-value edge are considered as the same character while 2-value edge means a potential selection    
    used = {w : False for w in proper_names}

    for canonical_name, data in connectionsTable.nodes(data = True):
        #Use all firstname, category 3 or 4 indicates that firstname/last name have not been separated properly
        if data["name_category"] < 3: 
            firstname = data["name"].first
            if firstname != "" and used[firstname] == False:
                used[firstname] = True
                names_bucket = set()
                firstname_bucket = set()
                firstname_bucket.add(firstname)
                names_bucket.update(canonical_names_dict[firstname])
                for cluster in nicknames:#check nickname associated
                    if firstname in cluster:
                        for nickname in cluster:
                            if nickname in proper_names:
                                names_bucket.update(canonical_names_dict[nickname])
                                firstname_bucket.add(nickname)
                                used[nickname] = True
                if firstname[0] in proper_names:#check initial present
                    names_bucket.update(canonical_names_dict[firstname[0]])
                    firstname_bucket.add(firstname[0])
                    used[firstname] = True                
            names_bucket = list(names_bucket)
            for i in range(len(names_bucket)):
                for j in range(i+1, len(names_bucket)): 
                    node1 = connectionsTable.nodes[names_bucket[i]]
                    node2 = connectionsTable.nodes[names_bucket[j]]
                    if node1["gender"]*node2["gender"] != -1:#avoid to link male and female CN
                        if node1["name"].first in firstname_bucket and node2["name"].first in firstname_bucket:                        
                            if node1["name"].last == node2["name"].last:
                                equalize_gender(node1, node2)
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)  
                            elif node1["name"].last == "" or node2["name"].last == "": 
                                if node1["name"].last == "" and node2["name"].last == "":
                                    equalize_gender(node1, node2)
                                    connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)
                                else:
                                    connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 2)
                        elif node1["name"].first == "" or node2["name"].first == "" :
                            if node1["name"].first == "" and node2["name"].first == "":
                                equalize_gender(node1, node2)
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 1)
                            else:
                                connectionsTable.add_edge(names_bucket[i], names_bucket[j], paired = 2)

    
    #BUG McGiffin    
    #link name sharing only lastname
    for canonical_name, data in connectionsTable.nodes(data = True):
        lastname_list = data["name"].last_list
        if data["name"].first != "" and not used[data["name"].first] :
            lastname_list.append(data["name"].first)
            data["name"].first == None
        for lastname in lastname_list:
            if lastname in proper_names and used[lastname] == False:
                used[lastname] = True
                bucket = []
                bucket.extend(canonical_names_dict[lastname])
                
                if lastname[0] in proper_nouns:#check initial
                    for cn2 in canonical_names_dict[lastname[0]]:
                        if cn2 not in bucket:
                            bucket.append(cn2)
                for cluster in nicknames:#check nickname associated
                    if lastname in cluster:
                        for nickname in cluster:
                            if nickname in proper_names:
                                for cn2 in canonical_names_dict[nickname]:
                                    if cn2 not in bucket:
                                        bucket.append(cn2)                               
                                used[nickname] = True
                                
                for i in range(len(bucket)):
                    for j in range(i+1, len(bucket)):
                        node1 = connectionsTable.nodes[bucket[i]]
                        node2 = connectionsTable.nodes[bucket[j]]
                        if node1["gender"] * node2["gender"] != -1 and (bucket[i], bucket[j]) not in connectionsTable.edges() :
                            connectionsTable.add_edge(bucket[i], bucket[j], paired = 2)
                            
    #link neutral noun with the most used nouns among their potential partner
    used = {w : False for w in connectionsTable.nodes}
    
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False and data["gender"] == 0 and data["name_category"] <= 2:
            used[canonical_name] = True
            
            cluster = [canonical_name]
            ## group paired nodes from the neutral cluster
            cluster_1_pair(connectionsTable, used, cluster)

            ## group their non-neutral nbh using their edges
            candidates_edge = []
            for cn2 in cluster:    
                for edge in connectionsTable.edges(canonical_name, data = True):  
                    if edge[2]["paired"] == 2:
                        candidates_edge.append(edge)
            if len(candidates_edge) > 0:     
                subAT= {s[1]: connectionsTable.nodes[s[1]]["value"] for s in candidates_edge}
                while len(subAT.keys()) != 0:
                    maxMentions = max(subAT, key=subAT.get)
                    gender = connectionsTable.nodes[maxMentions]["gender"]
                    del subAT[maxMentions]
                    if gender != 0:
                        for cn2 in cluster:
                            connectionsTable.nodes[cn2]["gender"] = gender                       
                        break
                    else:
                        connectionsTable.add_edge(canonical_name, maxMentions, paired = 1)
                        cluster.append(maxMentions)
                        cluster_1_pair(connectionsTable, used, cluster, index = len(cluster)-1)
            

        elif used[canonical_name] == False and data["name_category"] > 2:
            
            used[canonical_name] = True  
            
            cluster = [canonical_name]
            cluster_1_pair(connectionsTable, used, cluster) 
                
            ## group their non-neutral nbh using their edges
            candidates_edge = []
            for cn2 in cluster:    
                for edge in connectionsTable.edges(canonical_name, data = True):                
                    if edge[2]["paired"] == 2 and connectionsTable.nodes[edge[1]]["gender"] * \
                        connectionsTable.nodes[canonical_name]["gender"] != -1:
                        candidates_edge.append(edge)
            if len(candidates_edge) > 0: 
                subAT= {s[1]: connectionsTable.nodes[s[1]]["value"] for s in candidates_edge}
                first_mention =  max(subAT, key=subAT.get)
                while True:
                    maxMentions = max(subAT, key=subAT.get)
                    del subAT[maxMentions]
                    if connectionsTable.nodes[maxMentions]["name_category"] < 3:
                        break
                    elif len(subAT.keys()) == 0:
                        maxMentions = first_mention
                        break
                connectionsTable.add_edge(maxMentions, canonical_name, paired = 1)
                if connectionsTable.nodes[canonical_name]["gender"] == 0 and connectionsTable.nodes[maxMentions]["gender"] != 0:
                    for node in cluster:
                        connectionsTable.nodes[node]["gender"] = connectionsTable.nodes[maxMentions]["gender"]
                elif connectionsTable.nodes[canonical_name]["gender"] != 0 and connectionsTable.nodes[maxMentions]["gender"] == 0:
                        cluster = [maxMentions]
                        used2 = {w : False for w in connectionsTable.nodes}
                        cluster_1_pair_without_used(connectionsTable, cluster) 
                        for node in cluster:
                            connectionsTable.nodes[node]["gender"] = connectionsTable.nodes[canonical_name]["gender"]

                        
        elif used[canonical_name] == False:#during the first phase, some inconsistent 2-paired conenction could have been made
            gender = connectionsTable.nodes[canonical_name]["gender"]
            bucket = []
            bucket.extend(connectionsTable.neighbors(canonical_name))
            for nghb in bucket: 
                if connectionsTable.nodes[nghb]["gender"] * gender == -1:
                    connectionsTable.remove_edge(canonical_name,nghb)
     
    #directed graph containg arrow linked to main canonical name of a cluster
    aliases.add_nodes_from(connectionsTable.nodes(data = True))
    print("connection established")
    used = {w : False for w in connectionsTable.nodes}

    #creates cluster of names related to every character
    for canonical_name, data in connectionsTable.nodes(data = True):
        if used[canonical_name] == False:  
            used[canonical_name] = True
            #add all neibhors and their neighbors recursively to our cluster
            cluster = []
            candidates = [canonical_name]
            while len(candidates) > 0:
                cn2 = candidates.pop()
                cluster.append(cn2)
                for edge in connectionsTable.edges(cn2, data = True):
                    
                    if edge[2]["paired"] == 1 and not used[edge[1]]:
                        used[edge[1]] = True
                        candidates.append(edge[1])
                        
            subAT= {s: connectionsTable.nodes[s]["value"] for s in cluster}
            maxMentions = max(subAT, key=subAT.get) 
            cluster.remove(maxMentions)
            for cn2 in cluster:
                aliases.add_edge(cn2, maxMentions)
                aliasTable[maxMentions].extend(aliasTable.pop(cn2,[]))
    print("graph made")            
    return aliasTable, connectionsTable, aliases

#from chunk, extract canonical name in a wordlist form
def canonical_names_from_chunk(chunk, proper_names):
    detected = 0
    canonical_names_list = [] #list of canonical names
    wordlist = []# canonical name in a form of wordlist      
    for w in chunk.words:
        if is_valid(w.string):
            detected = 1
            wordlist.append(w.string)
        elif detected == 1:
            canonical_names_list.append(wordlist)
            wordlist = []
            detected = 0
            
    if detected == 1:
        canonical_names_list.append(wordlist)
    
    #if multiple names in chunk, check that all of them contain a proper name
    if len(canonical_names_list) > 1:
        index = 0
        while index < len(canonical_names_list):
            wordlist = canonical_names_list[index]
            correct = 0
            for word in wordlist:
                if word in proper_names:
                    correct = 1
                    break
            if not correct:
                canonical_names_list.pop(index)
            else:
                index +=1
    return canonical_names_list
    
def equalize_gender(node1, node2):
    if node1["gender"] == 0:
        node1["gender"] = node2["gender"]
    elif node2["gender"] == 0:
        node2["gender"] = node1["gender"]

#cluster unused nodes linked by an 1-value edge
def cluster_1_pair(connectionsTable, used, cluster, index = 0):
    while index < len(cluster):
        for edge in connectionsTable.edges(cluster[index], data = True):
            if edge[2]["paired"] == 1 and not used[edge[1]]:
                used[edge[1]] = True
                cluster.append(edge[1])
        index+=1
#cluster nodes linked by an 1-value edge
def cluster_1_pair_without_used(connectionsTable, cluster, index = 0):
    used = []
    while index < len(cluster):
        for edge in connectionsTable.edges(cluster[index], data = True):
            if edge[2]["paired"] == 1 and edge[1] not in used:
                used.append(edge[1])
                cluster.append(edge[1])
        index+=1
        

def get_honorifics():
    f = open("text_file\honorifics.txt", "r")
    string  = f.read()
    honorifics, female_honor, male_honor = ast.literal_eval(string)
    f.close()
    return honorifics, female_honor, male_honor

def get_stop_list():
    f = open("text_file\stop-list.txt", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        strings.append(line)
    f.close()
    return strings
    
def get_nicknames():
    f = open("text_file\hypocorisms.txt", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        strings.append(line.split())
    f.close()
    return strings
    
def get_verb_dependency():
    f = open("text_file\character-verb-predicates.tsv", "r")
    f1 = f.read().split("\n")
    strings = []
    for line in f1:
        string = line.split()
        if len(string) > 0:
            strings.append(string)
    f.close()
    return strings




