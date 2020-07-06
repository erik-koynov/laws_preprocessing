import re
import json
import os
"""
FUNCTION: name_generator -> generate the names for the files to be saved, holding the provisions in the envisioned 
format. The names follow the following nomenclature : each name consists of 6 capital letters for the 6 possible
provision hierarchical divisions (set up in the nomenclature letters) and after each of the letters there is the
respective ID -> e.g. P309A_S_N8BbDff means paragraph 309a Nummer 8 b) ff) -> if there is no specified ID in the
law text there is a '_' after the respective capital letter. Creating this nomenclature will make it easy to 
retrieve the needed files when inserting references from other provisions.
INPUT: nomenclature_letters-> list of str -> holding the capital letters denominating the respective hierarchical
                              part of the provision
       file_name -> list of the IDs of the nodes that we want to store
       PUNCTUATION_REGEX -> compiled regex to remove punctuation from the IDs when generating the file names
OUTPUT: final_name -> str -> the final name generated after the nomenclature
"""


def name_generator(nomenclature_letters, file_name, PUNCTUATION_REGEX):
    final_name = ''
    i = 0
    j = 0
    while i < len(nomenclature_letters):
        if i == 0:
            j += 1
            i += 1
            continue
        try:
            if len(file_name[j - 1].split()) > 1:
                print('There are more than one elements')
                print(nomenclature_letters[i])

                final_name += nomenclature_letters[i] + re.sub(PUNCTUATION_REGEX,
                                                               '',
                                                               file_name[j - 1].split()[0].strip())
                final_name += nomenclature_letters[i + 1] + re.sub(PUNCTUATION_REGEX,
                                                                   '',
                                                                   file_name[j - 1].split()[1].strip())
                i += 2
                j += 1
                continue
            else:
                final_name += nomenclature_letters[i] + re.sub(PUNCTUATION_REGEX, '', file_name[j - 1].strip())
        except IndexError:
            final_name += nomenclature_letters[i] + '_'
        i += 1
        j += 1
    return final_name


"""
FUNCTION: create_file_name_and_file_content -> this function formats the file content and extracts the needed
information in order that the file name can be later generated using the name_generator function. The format
of the file content approximates the way a lawyer would read a clause of a provision.
INPUT: fathers -> a list of tuples holding the clauses that are parents to the current clause
       key -> a tuple -> the actual current clause with its ID
       logical_and -> whether or not the clauses are conjugated by a logical and
       provisions -> only applicable if logical_and is also True -> a list of provisions conjugated by and
OUTPUT: file_content -> a string containing the content that is to be written onto the files
        file_name -> the elements that should be used to generate the file name using name_generator
"""


def create_file_name_and_file_content(fathers, key, logical_and = False, provisions = None):
    if not logical_and:
        file_name = []
        print('\n\n\nPROVISION:')
        file_content = ''
        for i in fathers:
            print(i[0])
            if not i[0][0].endswith('_ '):
                file_content += i[0][0] + ' ' + i[0][1] + '\n'
            else:
                file_content += re.sub(r'_ ','',i[0][0]) + i[0][1] + '\n'
            file_name.append(i[0][0])
        print(key)
        if key[0] == '_ ': # if the provision is an Absatz without an Absatz id
            file_content += key[1] + '\n'
        elif not key[0].endswith(' '):
            file_content += '\b\b' + key[0] + ' ' + key[1] + '\n'
        else:
            file_content += '\b\b' + key[0] + key[1] + '\n'
        file_name.append(key[0])
        for j in reversed(fathers):
            print(j[1])
            file_content += j[1] + '\n'

        print(file_name)
        return file_content, file_name
    else:
        file_name = []
        file_content = ''
        print('\n\n\nFINAL PROVISION OUTPUT AT LOGICAL AND\n\n\n')
        for i in fathers:
            print(i[0])
            file_name.append(i[0][0])
            if not i[0][0].endswith('_ '):
                file_content += i[0][0] + ' ' + i[0][1] + '\n'
            else:
                file_content += re.sub(r'_ ','',i[0][0]) + i[0][1] + '\n'
        print('\t\t', provisions)
        for i in provisions:
            file_content += '\b\b' + i[0] + i[1] + '\n'
        for j in reversed(fathers):
            print(j[1])
            file_content += j[1] + '\n'
        return file_content, file_name



"""
FUNCTION: write_to_json -> create the data structure and store it in json files according to the previously created
file nomenclature. Called in parse_provisions.py
INPUT: PATH -> the folder where the files are to be stored
       contend -> string : that contains the text of a provision "as a lawyer would read it" as returned by the 
                  create_file_name_and_file_content function
       file_name -> string : the name of the file as generated by create_file_name_and_file_content
       lowest_order_clauses -> the clauses of lowest order -> to be used if the provision in referred to by others
       hierarchical_place -> python dict: where inside the law tree structure (i.e. book, chapter etc.)
       provision_title -> string : the title of the provision
       provision_id -> string (a number) : e.g. 1a, 309 etc.
       references -> a list of strings holding the references as retured by
                     the find_references function defined in the regex_file.py ["P664A_S_N_B_D", "P665A_S_N_B_D"]
       fathers -> a list of tuples -> holding all the parent clauses of the lowest_order_clause -> could be used
                  if a provision is references -> in order not to omit info, or to repeat info a lot of times 
                  if only the provision content is used / or if only the lower_order_clause is used 
OUTPUT: None -> the datastructure full_content is written to the jason file      
"""
def write_to_json(PATH, content, file_name, lowest_order_clauses, hierarchical_place, provision_title, provision_id, references, fathers):
    if type(lowest_order_clauses)==tuple:
        lowest_order_clauses = [lowest_order_clauses]
    full_content = {'Provision': content,
                    'Lowest_order_clause': list(map(lambda key : key[0] + ' ' + key[1]\
                        if not key[0].endswith(' ') else key[0] + key[1], lowest_order_clauses)),
                    'Provision_title': provision_title,
                    'Provision_id': provision_id,
                    'References': list(set(references)),
                    'Parent_clauses': fathers}
    full_content.update(hierarchical_place)
    try:
        f = open(os.path.join(PATH, file_name), 'w')
    except:
        os.mkdir(PATH)
        f = open(os.path.join(PATH, file_name), 'w')
    json.dump(full_content, f, ensure_ascii= False)


"""
FUNCTION: add_prefixes_to_inner_references -> before storing the references which are actually names of the 
          respective files holding the respective provisions after the nomenclature we need to make sure that
          the inner references - i.e. that provisions that refer to Absatz/ Nummer type clauses inside the same
          provision, we need to store the names correctly 
INPUT: references -> the names of the references
       final_nale -> the final name of the file currently to be written
OUTPUT: None
"""

def add_prefixes_to_inner_references(references, final_name):

    for i, ref_ in enumerate(references):
        try:
            idx = final_name.index(ref_[0])
            if idx != 0:
                references[i] = final_name[:idx] + ref_
        except ValueError as e:
            print(e)
            print(ref_)






def write_to_json_full(PATH, content, file_name, hierarchical_place, provision_title, provision_id, references):

    full_content = {'Provision': content,
                    'Provision_title': provision_title,
                    'Provision_id': provision_id,
                    'References': list(set(references))}
    full_content.update(hierarchical_place)
    try:
        f = open(os.path.join(PATH, file_name), 'w')
    except:
        os.mkdir(PATH)
        f = open(os.path.join(PATH, file_name), 'w')
    json.dump(full_content, f, ensure_ascii= False)