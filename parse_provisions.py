import requests
import bs4
import re
import nltk
from crawler_bgb import *
from tree_walker import *
from regex_file import *

def div_with_text_only(tag): # and also leaf
    if (tag.name == "div") and (tag.find(re.compile('dd|dl'))==None):
                return True
    return False #if valid it reaches here
def div_not_title(tag):
    if (tag.text.startswith('(') and tag.text.endswith(')')):
        return False
    else:
        return True
# GOAL OUTPUT:
"""
309 _ 9 a 
(Laufzeit bei Dauerschuldverhältnissen)
bei einem Vertragsverhältnis, das die regelmäßige Lieferung von Waren oder die regelmäßige Erbringung 
von Dienst- oder Werkleistungen durch den Verwender zum Gegenstand hat,
eine den anderen Vertragsteil länger als zwei Jahre bindende Laufzeit des Vertrags
dies gilt nicht für Verträge über die Lieferung als zusammengehörig verkaufter Sachen sowie für 
Versicherungsverträge

"""


# it will be easier to just find all references -> and filter those that are inside than first find the inside and later the outside references
# TODO: FIND REFERENCES IN THE SECOND PARTS OF THE PARENTS -> IF SO -> STORE 2. PARTS ONLY WITH RELEVANT PROVISIONS
# TODO: DONE! find correct way to get the number of the Satz which now gets reinitialized at each sub-norm box (whereever there are Nummer/Buchstaben
# TODO: DONE maybe -need more tests? find solution to the problem in 309 : finding a dls of different hierarhy when recursice = True and nothing when recursive = False
# the problem is that in 309 sometimes the dl is inside a DIV and not directly inside the parent dd. it is even worse
# that sometimes the first div is not the one cotaining the dl but a title... so we have to find that first div which
# does not contain the title
# TODO: DONE? stop satz number from being updated on Nummern (should be updated only on sentences of Absaetze)
# TODO: DONE? decide what to do with the continuations of the Nummern / Buchstaben etc.
"""
Currently the most precise separation is done on absatz level -> the absatz is split into sentences if there
is one single sub-norm box. For the Nummern and other sub-norms there is currently another solution : the whole
text above and the whole text below a sub-norm box are treated as "previous/next sentence" 

"""
# TODO: DONE! gmodularize code!
# TODO: DONE! make sure all sentences stored are stripped! and have the same format in ordet that the keys are equal!!!
# TODO: DONE! find a way to store the id separately
# TODO: change variable names
# TODO: make sure the supplementary continuation check always returns the correct continuation - I have doubts about the case where there is a title inside the parent clause
# TODO: DONE! check the key generation !there is a problem creating copies of misgenerated keys...
# TODO: save the actual text of the lowest order clause separately in a separate datafield so that we can use it in the reference field

"""
FUNCTION: recursion -> create the tree structure of the current provision so that the Absatz type clause is the parent of the 
          all other lower-order clauses 
INPUT: nodes -> list of bs4 objects holding clauses -> initially Absatze
       tree -> python dict -> to be processed inplace and at the end it hold the tree structure 
       MATCHING_ABSATZ -> regex for Absatze not beginning with a number
       fathers -> a list -> initially an empty list
       satz_number -> initially 1 -> the current satz number -> only relevant inside an absatz
OUTPUT: satz_number
NOTE: the important part is the tree structure -> the python dict that holds it is processed in-place
"""
def recursion(nodes, tree, MATCHING_ABSATZ, fathers = None, satz_number = 1):
    print('satz number at the beginning of the loop: ', satz_number)
    for i, node in enumerate(nodes):

        # initialize the number of the Satz inside an Absatz and initialize fathers as [] for every Absatz
        try:
            if node.attrs['class'][0]=='jurAbsatz':
                print('\n\n\n\nABSATZ:{}'.format(i+1))
                satz_number = 1
                print('SATZ NUMBER initialized at: {}\n\n\n\n'.format(satz_number))
                fathers = []
        except KeyError:
            pass

        print('number of nodes: ', len(nodes))
        print('CURRENT NODE: ', node)

        try:
            print('NEXT NODE TO COME',nodes[i+1])
        except:
            pass

        dls = node.find_all('dl',recursive = False) # find all boxes containing numbers/letters/double letters
        node_text = node.text
        # find the id of the current clause
        nr = find_clause_id(node, MATCHING_ABSATZ)

        # BASE CONDITIONS -> there are no further sub clauses (no more 'dl' blocks inside the node)
        if len(dls) == 0:
            print('BEFORE TURNING OFF RECURSION: there were no dls')

            # make sure the node really does not comprise sub clauses
            dls = supplementary_dl_check(node, div_not_title)

            if len(dls) == 0:

                # deal with the leaf nodes
                store_leaf_nodes(node, tree, nr, node_text, MATCHING_ABSATZ)
                continue


        print('NUMBER OF DLS: ',len(dls))
        for j, dl in enumerate(dls):

            print('\n\n\nCONSECUTIVE LOOP: {}\n\n\n\n'.format(j))
            print('CURRENT NODE?: {}...'.format(node.text[:30]))
            try:
                print('DL TO COME: ',dls[j+1])

            except IndexError:
                pass

            dds = dl.find_all('dd', recursive = False)

            # store each sentence separately ONLY for clauses of type Absatz and not for other divisions
            # determine if the parent is a clause of type Absatz
            is_absatz = is_parent_absatz(dl)

            print('CURRENT DL: ', dl)
            print('PREVIOUS SIBLING: ', dl.previousSibling)
            print('DDS: ',dds)

            # the "parent" clause can be retrieved as a previousSibling: split the parent clause into sentences
            previous_sentences = nltk.sent_tokenize(dl.previousSibling, 'german')
            previous_sent = previous_sentences[-1] # the last previous sentence is the sentence which contains the provision
            previous_sent = re.sub(MATCHING_ABSATZ,'',previous_sent)
            next_sentence = dl.nextSibling

            # the continuation to the current sentence might not be reachable as nextSibling
            # if the current dl is inside
            # div inside the node -> thus we have to take this into account
            title_ = ''
            if next_sentence is None:
                # supplementary next sentence check
                next_sentence, title_ = supplementary_continuation_check(dl, div_with_text_only)

            # if parent clause is a clause of Absatz type then its sentences up until the 'dl' of the
            # current clause should be stored separately as keys of the provision tree
            # if the parent clause is not of Absatz type then all its sentences up until the 'dl' of the
            # current clause should be stored together as one text (this is a matter of decision could change)
            insert_previous_sentences_into_tree(is_absatz,
                                                previous_sentences,
                                                MATCHING_ABSATZ,
                                                tree,
                                                nr,
                                                satz_number,
                                                title_)

            fathers.append(nr+previous_sent)

            # update satz number
            satz_number += len(previous_sentences) -1
            print('UPDATING SATZ NUMBER: ',satz_number)

            # define the key of the key value pair for the current clause: the key contains the text from
            # the parent clause
            key = define_key(satz_number, next_sentence, is_absatz, nr, title_, previous_sent)

            if is_absatz:
                satz_number += 1
            print('UPDATING SATZ NUMBER: ', satz_number)
            print('next sentence: ', next_sentence)

            try:
                if next_sentence[0].isupper() and is_absatz: # the text after the box is NOT a continuation of the text vb
                    print('WRITING SEPARATE SENTENCES')
                    # store next sentences
                    insert_next_sentences_into_tree(next_sentence, tree, nr, satz_number, START=0)
                    next_sentence = ''

                elif (not next_sentence[0].isupper()) and is_absatz: # if is absatz then the continuation to the current sentence is the first sentence recognized by nltk and the others should be stored separately
                    next_sentence = nltk.sent_tokenize(next_sentence, 'german')[0]
                    insert_next_sentences_into_tree(next_sentence, tree, nr, satz_number, START=1)

                # if there are more than one sub-clause boxes inside a non-Absatz clause and the continuation text
                # does not contain a part of the paren clause : store the whole next text as a one single key
                elif next_sentence[0].isupper() and not is_absatz and len(dls)>1:
                    insert_next_texts_into_tree_non_absatz(tree, nr, title_, next_sentence)

            except TypeError as e:
                next_sentence = ''
                print(e)
            except IndexError as e:
                next_sentence = ''
                print(e)
            # if none of these is true then we have a continuation of a non-absatz and the exceptions were not thrown
            # then the next sentence remains the whole found next_sentence

            tree[key]={}
            tree[key]['CONTINUATION'] = next_sentence

            satz_number = recursion(dds, tree[key], MATCHING_ABSATZ, fathers, satz_number)
            print('RETURNED satz number: ',satz_number)
            print(fathers)
            del fathers[-1]
            print('fathers after deletion', fathers)

        print('\n\n\n\n')
    return satz_number


# create datastructure ready to be exported to json

# TODO: write the texts to files as wanted -> take into account the logical and and also in a separate field write only the clause of lower order
# TODO: DONE! create the nomenclature for the files from the IDs
# TODO: write comments to this function
# TODO: DONE! modularize code
# TODO: DONE! remove punctuation from ids

# p: paragraph, a: absatz, s: satz, n: nummer, b: buchstabe, d: doppelbuchstabe
"""
FUNCTION: walk_tree -> a function to walk the tree created by the recursion function. This function comprises some very
          important functionalities -> create the content as is envisioned, write the correctly parsed content to files
INPUT: node -> initially it is actually the tree (the python dict) itself
       PATH -> the path where to store the created files -> preferably the name of the law
       hierarchical_place -> dict -> since this function is going to be called inside the structure_extractor.py the hierarchical_place
       is a python dict created there
       provision_title -> string -> the title of the provision
       provision_id -> string -> a number that is the id of the provision i.e. Art. 10 -> 10 is the id
       PUNCTUATION_REGEX -> regex for deleting punctuation where needed
       fathers -> initially an empty list -> that is then inplace processed and holds the parents of the current
       sub-order clause -> i.e. if we have a number the parent will be the Absatz and Satz inside of which the Nummer 
       resides
OUTPUT: None -> everything is done inplace
"""
def walk_tree(node, PATH, hierarchical_place, provision_title, provision_id, PUNCTUATION_REGEX,fathers = None):
    nomenclature_letters = ['P', 'A', 'S', 'N', 'B', 'D']
    print(fathers)
    try:
        provisions =[]
        logical_and = node.get('LOGICAL AND',False)
        for i, (key, value) in enumerate(node.items()):
            if key == 'CONTINUATION' or key == 'LOGICAL AND':
                continue

            print('logical and',logical_and)
            if logical_and:
                provisions.append(key)

                print('LOGICAL AND encountered ')
                continue
            print('CURRENT KEY: ', key)
            if node[key] is not None:
                print(node)
                print('NODE is not an end node: inserting into the fathers')
                fathers.append((key, node[key].get('CONTINUATION', '')))
            walk_tree(node[key], PATH, hierarchical_place, provision_title, provision_id, PUNCTUATION_REGEX,fathers)

            # CREATE FILENAME
            if not logical_and and node[key] is None:
                #file name file content
                file_content, file_name = create_file_name_and_file_content(fathers, key)
                print('FILE CONTENT')
                print(file_content.strip())
                # generate final name
                final_name = name_generator(nomenclature_letters, file_name, PUNCTUATION_REGEX)
                print('FILE NAME: ',final_name)
                print('\n\n\n')
                # find the references
                references = find_references(file_content)
                final_name = 'P' + provision_id + final_name
                #print('REFERENCES: ', references)
                add_prefixes_to_inner_references(references, final_name)
                print('REFERENCES: ', references)
                write_to_json(PATH,
                              file_content,
                              final_name,
                              key,
                              hierarchical_place,
                              provision_title,
                              provision_id,
                              references,
                              fathers)



            if node[key] is not None:
                print('CURRENT KEY: at del ', key)
                del fathers[-1]


        if logical_and:
            file_content, file_name = create_file_name_and_file_content(fathers, None, logical_and, provisions)
            final_name = name_generator(nomenclature_letters, file_name, PUNCTUATION_REGEX)
            print('FINAL NAME: ', final_name)
            print('FILE CONTENT AND: ', file_content)
            references = find_references(file_content)
            final_name = 'P' + provision_id + final_name
            # print('REFERENCES: ', references)

            # add prefixes to the inner references
            add_prefixes_to_inner_references(references, final_name)
            print('REFERENCES: ', references)

            write_to_json(PATH,
                          file_content,
                          final_name,
                          provisions,
                          hierarchical_place,
                          provision_title,
                          provision_id,
                          references,
                          fathers)
    except AttributeError: # base condition will be that the key passed is None
        print('FATHERS at the end node: ', fathers)

        return




if __name__=='__main__':
    # DEFINE HEADERS
    headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "ccept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-US,en;q=0.5",
    "Connection"	:"keep-alive",
    "Host":"pytorch.org",
    "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"}
    # START SESSION
    session=requests.Session()
    # GET A PROVISION
    response = session.get('https://www.gesetze-im-internet.de/bgb/__556g.html', headers=headers).text



    soup = bs4.BeautifulSoup(response,'html5lib')

    box = soup.find('div',{'id':'container'})
    title = box.find('h1').text

    print(title)



    # FIND THE ABSAETZE
    absaetze = box.find('div',class_ = 'jnhtml').find_all('div',class_='jurAbsatz')

    MATCHING_ABSATZ = re.compile('^\([1-9][a-z]?\)')
    tree = {}
    nomenclature_letters = ['P', 'A', 'S', 'N', 'B', 'D']
    PUNCTUATION_REGEX = re.compile(r'\(|\)|{|}|\[|\]|\.|,|:|;| ')

    recursion(absaetze,tree, MATCHING_ABSATZ)
    print('\n\n\n\n\nWalking Tree\n\n\n\n\n\n')

    fathers = []
    print(tree)
    walk_tree(tree,
              PATH = 'TEST',
              hierarchical_place = {'Buch':'Sachenrecht'},
              provision_title = 'some title',
              provision_id = '55a',
              PUNCTUATION_REGEX = PUNCTUATION_REGEX,
              fathers = fathers)
    print(fathers)