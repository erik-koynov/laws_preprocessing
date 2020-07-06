import re
import nltk
"""
FUNCTIONS LIST: find_clause_id
                supplementary_dl_check
                store_leaf_nodes
                is_parent_absatz
                supplementary_continuation_check
                insert_previous_sentences_into_tree
"""
"""
FUNCTION: find_clause_id -> every clause (be it an Absatz, Nummer, etc.) has an "id" number inside the provision
(e.g. 1. or b) or (1)) and in order to be able to identify it when storing it we have to find this ID. In the
current website the ids are stored either as 'dt' right before the actual clause or as part of the clause if the
clause is an Absatz. This function implements this differences in the way the ids are stored and returns the
ID
INPUT: node (BS4 object)-> the current node (the logical part of the clause which is currently being processed)
       MATCHING_ABSATZ -> compiled regular expression finding the ID inside the text of an Absatz
OUTPUT: nr -> the number found + ' '
"""
def find_clause_id(node, MATCHING_ABSATZ):
    # first check for absaetze and then for anything else
    if len(MATCHING_ABSATZ.findall(node.text)) != 0:
        nr = str(MATCHING_ABSATZ.findall(node.text)[0]) + ' '  # the first match
        print('h: {}'.format(nr))
        return nr
    else:
        try:
            if node.attrs['class'][0]=='jurAbsatz':
                # there is no number in the Absatz:there is only one Absatz in the Paragraph-> store an '_'
                nr = '_ '
                return nr

        except KeyError:
            try: # the number is stored in a dt
                nr = node.findPrevious('dt').text + ' '
                print('NUMBER: at find previous: {}'.format(nr))
                if '*)' in nr: # there is from time to time a strange *) instead of an actual number
                    raise AttributeError
                return nr

            except AttributeError: # the number is not stored in a dt->the clause is an Absatz:the number is inside its text


                # there is no number in the clause :there is only one Absatz in the Paragraph-> store an '_'
                nr = '_ '
                return nr

"""
FUNCTION: supplementary_dl_check -> in could be the case that the non-recursive search for 'dl's (sub clauses)
does not yield any results falsely - that is, no dl box was found but there actually is one. The reason for this
could be that the dl is nested inside a div inside the node and is not direct child of the node. To make sure
a sub clause is not left unseen we should carry out additional checks
INPUT: node (BS4 object) -> the current clause inside which we search for sub clauses
       div_not_title -> function that returns True is the tag div is not a title
OUTPUT: dls -> list of BS4 objects of 'dl' tags
"""
def supplementary_dl_check(node, div_not_title):
    # the 'dl' tag may not be a direct child of the current node but nested inside a div
    try:
        dls = node.find(div_not_title).find_all('dl', recursive=False)

    except AttributeError:
        # there was no div that does not start with ( and end with ) -
        # i.e. the only 'div's there are titles of clauses -> find all 'dl' in the current node
        dls = node.find_all('dl')

    # however it could theoretically be the case that even if there is a div that is not a title
    # it still does not contain any 'dl's : to make sure no clause is overlooked retrieve all 'dl's
    if len(dls) == 0:
        dls = node.find_all('dl')

    return dls

"""
FUNCTION: store_leaf_nodes -> store the node text as a key with value None inside the tree structure also
if the sub clauses are connected with the logical operator AND store inside the parent node of the tree 
INPUT: node (BS4 object) -> the current clause which we check for being a laef
       tree -> a python dictionary passed by reference and modified inplace -> holds the tree of the provision
       nr -> the clause id 
       node_text -> the text contained in the current node (stored in a variable)
OUTPUT: None -> the insertions into the tree are done in-place
"""
def store_leaf_nodes(node, tree, nr, node_text, MATCHING_ABSATZ):
    if node.name == 'dd':

        print('NODE IS LEAF: ', nr, node_text)
        if node.text.endswith('oder'):
            tree[(nr, node_text[:-4].strip())] = None
        else:
            tree[(nr, node_text.strip())] = None
        # fathers[-1].append(node.findPrevious('dt').text+ node.text)
    else:
        print('NODE IS LEAF: ', node.text)  # the text is the leaf node
        node_is_absatz = False
        # check is the current node is an Absatz
        try:
            if node.attrs['class'][0] == 'jurAbsatz':
                node_is_absatz = True
                tree[(MATCHING_ABSATZ.findall(node.text)[0], re.sub(MATCHING_ABSATZ, '', node_text).strip())] = None

        except KeyError as e:
            print(e)
            pass
        # for the case where there is no Absatz number
        except IndexError as e:
            print(e)
            tree['_ ', re.sub(MATCHING_ABSATZ, '', node_text).strip()] = None

        # this code block should never be executed -> but is implemented just in case
        if node.text.endswith('oder'):
            tree[(MATCHING_ABSATZ.findall(node.text[:-4])[0], re.sub(MATCHING_ABSATZ, '', node_text[:-4]).strip())] = None

        elif not node_is_absatz:
            print('generating key')
            tree[(MATCHING_ABSATZ.findall(node.text)[0], re.sub(MATCHING_ABSATZ, '', node_text).strip())] = None

    if node.text.endswith('und'):
        tree['LOGICAL AND'] = True

"""
FUNCTION: is_parent_absatz -> determine whether the parent of the current clause an Absatz 
INPUT: dl (BS4 object) -> the current clause
OUTPUT: is_absatz -> a boolean variable -> True if the parent is an Absatz
"""
def is_parent_absatz(dl):
    is_absatz = False

    try:
        if dl.parent.attrs['class'][0] == 'jurAbsatz':
            is_absatz = True
    except KeyError:
        is_absatz = False

    return is_absatz



"""
FUNCTION: supplementary_continuation_check -> since the current clause may not be a direct descendant of the 
parent clause but may be nested inside a div, finding the continuation of the parent clause using .nextSibling
on the current clause will not be possible since the continuation of the parent clause will most surely not be
inside the same div. Thus we have to check anon for 'div' tags containing only text which does not only contain
a title. If a title is found though we would also like to return it.
INPUT: dl -> the current clause (BS4 object)
       div_with_text_only -> a function that returns true if the tag found is a div that contains only text
OUTPUT: next_sentence -> a string holding the continuation to the parent clause -> coming right after the current
                         clause visually (one or many sentences)
        title_ -> a string holding the title of the parent clause if such is available and not already the parent
                  of the current clause

# ADDITIONAL COMMENT -> finding divs that only contain text is ok if there is only one DL inside the clause box
                        In the case of Absatz type clauses this should not be a problem because I currently have
                        NOT found an example that does not work -> that is the 'dl' of the current clause is
                        always a direct child of the 'div' of the Absatz. However there might be the case where
                        inside a Nummer or other subclause there are more than one 'dl' boxes and each sentence
                        is stored in a separate 'div'- try to find such examples and deal with them. 
"""
def supplementary_continuation_check(dl, div_with_text_only):
    print('NEXT SENTENCE was not found as nextSibling. Next part of the paragraph might be stored in a div')
    print('current div parent: ', dl.parent.parent)

    # find all 'div'-s that contain only text
    additional_infos = dl.parent.parent.find_all(div_with_text_only, recursive=False)
    print('ADDITIONAL INFOS: ', additional_infos)

    if len(additional_infos) > 1:
        # the second sentence because the first is the div containing the title of the whole provision
        next_sentence = additional_infos[1]
        title_ = additional_infos[0].text

        print('TITLE: ', title_)

        # check if by any chance the found div is not a clause of type Absatz this would mean we have gone
        # outside the parent Absatz and found the next one -> which should not be the case -> but just to make sure
        try:

            if next_sentence.attrs['class'][0] == 'jurAbsatz':
                next_sentence = ''
            else:
                next_sentence = next_sentence.text

        except KeyError:
            next_sentence = next_sentence.text

    # if the only one text-only-'div' was found and it starts with '(' then it is a title
    elif len(additional_infos) == 1 and additional_infos[0].text[0] == '(':
        title_ = additional_infos[0].text
        print('TITLE: ', title_)
        next_sentence = ''

    # if the only one text-only-'div' was found and it does not start with '(' then it is a continuation
    elif len(additional_infos) == 1:
        next_sentence = additional_infos[0].text
        title_ = ''

    # if no div containing only text was found -> there is no continuation to the clause
    else:
        next_sentence = ''
        title_ = ''

    return next_sentence, title_

"""
FUNCTION: insert_previous_sentences_into_tree -> insert the sentences of the parent clause preceding the current 
clause into the tree of the provision as keys with value None and also write their number. However if the parent
clause is not of the Absatz type -> store the whole preceding information into one node (not in separate).
INPUT: is_absatz -> bool : holds info whether the parent is an Absatz
       previous_sentences -> list of strings (sent tokenized by nltk)
       MATCHING_ABSATZ -> regular expression to remove the Absatz number (e.g. (1) from the beginning of the Absatz)
       tree -> python dictionary -> holding the logical tree of the provision
       nr -> the ID of the parent clause (e.g. (1) or b))
       satz_number -> the number of the current centence inside the Absatz
       title_ -> title of the clause (if available)
OUTPUT: None -> the tree is updated inplace
"""


def insert_previous_sentences_into_tree(is_absatz,
                                        previous_sentences,
                                        MATCHING_ABSATZ,
                                        tree,
                                        nr,
                                        satz_number,
                                        title_):
    if is_absatz:
        for i, sent in enumerate(previous_sentences[:-1]):
            sent = re.sub(MATCHING_ABSATZ, '', sent)
            # insert each sentence into the tree as a key with value None
            print('type of nr: ', type(nr),nr)
            if tree.get((nr + str(satz_number + i), title_ + sent.strip()), 0) == 0:
                tree[(nr + str(satz_number + i), title_ + sent.strip())] = None

    # for now I have decided to store the sentences of the nummern / buchstaben etc.
    # as one unit and not to split them
    else:
        if tree.get((nr, title_ + ' '.join(previous_sentences).strip()), 0) == 0:
            tree[(nr, title_ + ' '.join(previous_sentences).strip())] = None



"""
FUNCTION: define_key -> generate the key that is going to be the parent node of the current clause inside the
provision's logical tree. The differences between the ways to generate the keys are caused by the different
treatment of Absatz sentences and other clause sentences. If the sentence is inside of an Absatz then we want
to store also its sentence number if there are other sentences in that same Absatz.
INPUT: satz_number -> int holding the number of the sentence that happens to be the direct parent clause of the
                      current clause
       next_sentence -> str holding the continuation of the parent clause
       is_absatz -> bool : True is the parent clause is an Absatz
       nr -> str the ID of the parent clause (e.g. (1) or b) etc. )
       title_ -> str : the title of the parent clause (if available)
       previous_sent -> the actual parent sentence
OUTPUT: key -> str -> the generated key
"""


def define_key(satz_number, next_sentence, is_absatz, nr, title_, previous_sent):

    # if the parent sentence is the 1st sentence of the parent clause
    if satz_number-1 == 0:

        # add the sentence number if there are other sentences in that Absatz
        if next_sentence != '' and \
                (next_sentence[0].isupper() or len(nltk.sent_tokenize(next_sentence, 'german')) > 1)\
                and is_absatz:
            key = (nr + str(satz_number), title_ + previous_sent.strip())
            print('KEY: ', key)

        # if it is the first sentence inside the parent clause but either has no continuation or the sentence is not
        # part of an Absatz clause or there is a continuation but it starts with a lower letter and there is no
        # other sentence inside the Absatz
        elif not is_absatz:
            key = (nr, title_ + previous_sent.strip())
            print('KEY: ', key)
        elif is_absatz:
            key = (nr + '_ ', title_ + previous_sent.strip())
            print('KEY: ', key)
    # if the sentence is not the first and is inside an Absatz clause (i.e. there are other sentences in the Absatz)
    elif is_absatz:
        key = (nr + str(satz_number), title_ + previous_sent.strip())
        print('KEY: ', key)

    # if the sentence is not the first and is not inside an Absatz
    else:
        key = (nr, title_ + previous_sent.strip())
        print('KEY: ', key)

    return key

"""
FUNCTION: insert_next_sentences_into_tree -> insert the next sentences (the continuation of the current clause's 
parent tokenized into sentences) as keys with None values into the logical tree of the provision
INPUT: next_sentence -> string -> contains the full text of the continuation of the parent of the current clause
                                  it could contain one or many sentences -> for this reason sent_tokenize and 
                                  save each sentence separately
       tree -> python dictionary -> the logical tree of the current provision
       nr -> str the ID of the parent clause (e.g. (1) or b) etc. )
       satz_number -> int holding the number of the sentence that happens to be the direct parent clause of the
                      current clause
       START -> the position (the sentence) at which to start storing the next sentences in this way -> basically
                start should be either 1 or 0 -> if 0 then there is no continuation to the parent sentence and
                all following text consists of separate sentences -> if 1 then the first found sentence is the 
                continuation and it has to be stored in another way
OUTPUT: None -> the keys are inserted in-place into the logical tree of the provision
"""

def insert_next_sentences_into_tree(next_sentence, tree, nr, satz_number, START):
    for i, sent in enumerate(nltk.sent_tokenize(next_sentence, 'german')[START:]):

        if tree.get((nr + str(satz_number + i), sent.strip()), 0) == 0:
            print('SEPARATE KEY: ', (nr + str(satz_number + i), sent.strip()))
            tree[(nr + str(satz_number + i), sent.strip())] = None


"""
FUNCTION: insert_next_texts_into_tree_non_absatz -> if the next sentence text does not contain a continuation to
the parent clause sentence and at the same time there are more sub-clauses to that parent clause and the parent
clause is not an Absatz (for which we already have insert_next_sentences_into_tree) we need to store the whole
text (not split into separate sentences as would be the case if the parent clause was an Absatz) of the next part
of the parent clause as a key with value None.
INPUT: tree -> python dictionary -> the logical tree of the current provision
       nr -> str the ID of the parent clause (e.g. (1) or b) etc. )
       title_ -> str : the title of the parent clause (if available)
       next_sentence -> the full text of the parent clause which visually follows the current clause
OUTPUT: None : the key is stored with value None into the tree in-place
"""


def insert_next_texts_into_tree_non_absatz(tree, nr, title_, next_sentence):
    if tree.get((nr, title_ + next_sentence.strip()), 0) == 0:
        tree[(nr, title_ + next_sentence.strip())] = None



