import requests
import bs4
from parse_provisions import *
import re

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
response = session.get('https://www.gesetze-im-internet.de/bgb/BJNR001950896.html', headers=headers).text

soup = bs4.BeautifulSoup(response,'html5lib')

def run_algorithm(PATH, full = True):
    import os
    if not os.path.exists(PATH):
        os.mkdir(PATH)
    current_structure_dict = {}
    # a lower hierarchy division can only come after a higher hierarchy division has already come beforehand
    division_hierarchy = []
    # TODO: DONE! find all jnnorm -> if it contains h2 -> it is a division -> if not -> it is a provision should be prcessed like a norm
    full_law_text = soup.find_all('div', class_ = 'jnnorm')
    # TODO: parse provisions, write the texts to jsons, in other words -> expand the tree warker
    import os

    #os.mkdir(PATH)
    MATCHING_ABSATZ = re.compile('^\([1-9][a-z]?\)')
    nomenclature_letters = ['P', 'A', 'S', 'N', 'B', 'D']
    PUNCTUATION_REGEX = re.compile(r'\(|\)|{|}|\[|\]|\.|,|:|;| ')
    # TODO: comment! all functions
    for text in full_law_text:
        if (text.h2 is None) :
            try:
                # we need only absaetze
                if not text.h3.text.startswith('§'):
                    continue
            except:
                continue

            for footnote in text.find_all('div',class_ = 'jnfussnote'):
                try:
                    footnote.detatch()
                except TypeError:
                    pass
            print('text is a provision: to be parsed')
            full_title = text.find('h3').text
            print('provision title: ', full_title)
            provision_id = full_title.split()[1]
            provision_title = ' '.join(full_title.split()[2:])
            print(provision_id)
            print(provision_title)
            if not full:
                try:
                    absaetze = text.find('div', class_='jnhtml').find_all('div', class_='jurAbsatz')
                    print(len(absaetze))
                    tree = {}
                    fathers = []
                    recursion(absaetze, tree, MATCHING_ABSATZ)
                    walk_tree(tree,
                              PATH=PATH,
                              hierarchical_place=current_structure_dict,
                              provision_title=provision_title,
                              provision_id=provision_id,
                              PUNCTUATION_REGEX = PUNCTUATION_REGEX,
                              fathers=fathers)
                    # pass absaetze as argument to the parsing function

                except AttributeError as e:
                    print(e)
            else:
                try:
                    full_provision = text.find('div', class_='jnhtml').text
                    references = find_references(full_provision)
                    final_name = 'P'+provision_id
                    add_prefixes_to_inner_references(references, final_name)
                    write_to_json_full(PATH,
                                  full_provision,
                                  final_name,
                                  current_structure_dict,
                                  provision_title,
                                  provision_id,
                                  references)
                except AttributeError as e:
                    print(e)


            # parse stuff -> call the functions created in parse provisions, tree_walker, crawler_bgb
            #print(text.text)
        else:
            print('text is a division')
            for br in text.h2.find_all('br'):
                br.replace_with(' ')
            text_to_process = text.h2.text.split()
            division_ID = text_to_process[0]
            division_text = ' '.join(text_to_process[2:])
            # fill in the division hierarchy
            if division_ID not in division_hierarchy:
                division_hierarchy.append(division_ID)
            division_idx = division_hierarchy.index(division_ID)
            current_structure_dict[division_ID] = division_text
            # set all text of ids of lower hierarchy to '' if an ID of higher hierarchy has changed
            try:
                for div in division_hierarchy[division_idx+1:]:
                    current_structure_dict[div] = ''
            except IndexError:
                pass
            print(current_structure_dict)

#print(division_hierarchy)



if __name__=='__main__':

    run_algorithm('BGB',False)

# TODO: download more and see if everything is alright -> then create a function to loop through the files and store all references as additional text fields