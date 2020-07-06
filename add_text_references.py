import json
import os
import re
# TODO: for the next version -> differenciate between the types of refenreces whether a whole absatz is referenced or its parts -> add the lowest order clause only or also the parents!
PATH = 'BGB'
for i, file in enumerate(os.listdir(PATH)):
    with open(os.path.join(PATH,file), "r") as file_:
        data = json.load(file_)

    print(data['Provision_id'], data['Provision_title'])
    references = data['References']
    not_found_files = []
    data['References_text'] = []
    for ref_ in references:
        print(ref_)
        try:
            # exact match -> need only the lowest order clause
            with open(os.path.join(PATH, ref_), "r") as file_:
                appendix = json.load(file_)
            data['References_text']+=appendix['Lowest_order_clause']
        # the file was not found so we need to search for files with similar names and add them all as one single string
        # two possibilities -> a more general clause is referenced -> but it is more precisely stored
        # e.g. P232 is the reference but P232A4 is stored -> in that case find the fist underscore and find
        # all matches
        # the other possibility is if a Satz is referenced that is not found -> in that case we have to search
        # for the absatz
        except FileNotFoundError as e:
            print(e)
            first_underscore = ref_.find('_')
            not_found_files.append(ref_[:first_underscore]) # and the letter before it

    for ref_ in set(not_found_files):
        matched = []
        for j in os.listdir(PATH):
            if re.match(ref_,j) is not None:
                print('match found: {} : {}'.format(ref_, j))
                matched.append(j)
            else: # the only chance for the ref to be longer than the file_name is if it contains a Satz in an Absatz that does not contain Nummer
                S_ = ref_.find('S')
                S_other = j.find('S')
                if S_ != -1 and not (j[S_other+1].isalnum()):
                    ref_ = ref_[:S_]
                    if re.match(ref_, j):
                        print('match found on second try: {} : {}'.format(ref_, j))
                    else:
                        continue

        for match in matched:
            with open(os.path.join(PATH, match), "r") as file_:
                appendix = json.load(file_)

            data['References_text']+=appendix['Lowest_order_clause']
    print(' AT THE END: ',data['Provision_id'])
    print(data['References_text'])
    with open(os.path.join(PATH,file), "w") as file_:
        json.dump(data, file_, ensure_ascii= False)

    print(i)