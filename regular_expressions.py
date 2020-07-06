import re
import requests
import bs4
headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"ccept-Encoding":"gzip, deflate, br",
"Accept-Language":"en-US,en;q=0.5",
"Connection"	:"keep-alive",
"Host":"pytorch.org",
"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"}

# START SESSION
session=requests.Session()

def paragraph_id(paragraph_all_regex, paragraph_order_match, sub_regex = r'und|,|§'):
    groups = []
    for j in re.compile(paragraph_all_regex).finditer(paragraph_order_match):

        print('CURRENT GROUP')
        print(re.sub(sub_regex, '', j.group()).strip().split())
        paragraphs = re.sub(sub_regex, '', j.group()).strip().split()
        if len(paragraphs) > 1:
            groups = paragraphs
        else:
            groups.append(paragraphs)
    return groups



def find_id(match_regex, name, absatz_order_match, sub_regex, message):
    name.append([])
    for k in re.compile(match_regex).finditer(absatz_order_match):
        print('CURRENT {}'. format(message))
        print(k.group())

        print(name)
        # if more than one is found then for sure only the last one can have other IDs referred

        name[-1] = re.sub(r'{}'.format(sub_regex), '', k.group()).strip().split()


def find_paragraphs(tag):
    if tag.name == 'a' and tag.text.startswith('§'):
        return True

def download_paragraph_list(link):
    response = session.get(link, headers=headers).text
    soup = bs4.BeautifulSoup(response, 'html5lib')
    return list(map(lambda x: re.sub('§','',x.text).split()[0], soup.find_all(find_paragraphs)))



def finalize_name_creation(full_names, nomenclature_letters, all_names):
    for n, name_ in enumerate(full_names):
        length = len(re.compile('[A-Z]').findall(name_))
        if length < len(nomenclature_letters):
            full_names[n] += ''.join(list(map(lambda x: x + '_', nomenclature_letters[length:])))
    print('FULL NAMES FINAL: ', full_names)
    all_names += full_names




def generate_names_if_bis(l, letter, p, full_names, nomenclature_letters, k):
    print('we are here: ',l)
    count_begin = letter[p - 1] # the previous id
    print('COUNT BEGIN: ',count_begin)
    print(p)
    print(len(letter))
    c_ = 1
    while count_begin < letter[p + 1]:
        if count_begin[-1].isalpha() and letter[p+1][-1].isalpha():
            end_letter = chr(ord(count_begin[-1]) + 1)
            count_begin = letter[p - 1][:-1] + end_letter
            print('idx: ', -1 - p - (c_-1))
            print('fn ', full_names)
            full_names.append(full_names[-1 - p - (c_-1)])
            full_names[-1] += nomenclature_letters[k] + count_begin
            #full_names.append('P{}A_S_N_'.format(count_begin))
        elif count_begin[-1].isalpha() and not letter[p+1][-1].isalpha():
            count_begin = int(count_begin[:-1])
            count_begin += 1
            count_begin = str(count_begin)
            full_names.append(full_names[-1 - p - (c_ - 1)])
            full_names[-1] += nomenclature_letters[k] + count_begin
        elif not count_begin[-1].isalpha() and letter[p+1][-1].isalpha():
            count_begin = int(count_begin)
            count_begin += 1
            count_begin = str(count_begin)
            if count_begin > letter[p+1][:-1]:
                break
            full_names.append(full_names[-1 - p - (c_ - 1)])
            full_names[-1] += nomenclature_letters[k] + count_begin
        else:
            count_begin = int(count_begin)
            count_begin += 1
            count_begin = str(count_begin)
            print('idx: ', -1 - p - (c_ - 1))
            print('fn ', full_names)
            full_names.append(full_names[-1 - p - (c_ - 1)])
            full_names[-1] += nomenclature_letters[k] + count_begin
        c_+=1

    print('c after bis ', c_)
    return c_





def generate_names_if_not_bis(l, p, c_ , k, full_names, nomenclature_letters, before_bis_count, letter):
    print('generate names NOT bis', l)
    print('full names now: ', full_names)
    print('P: ', p)
    print('C: ', c_)
    print('IDX: ', -1 - p - (c_ - 1))

    full_names.append(full_names[-1 - p])
    full_names[-1] += nomenclature_letters[k] + l
    if 'bis' in letter and p != 0:
        before_bis_count += 1
    return before_bis_count



def generate_names_full_referenced_paragraphs(groups, paragraph_list, all_names, nomenclature_letters, paragraph = True, delete_last = False):
    full_names = []
    string_for_name = nomenclature_letters[0]+'{}'+'_'.join(nomenclature_letters[1:]) + '_'
    print(groups)
    for count, g in enumerate(groups):
        print(g)
        if g == 'bis' and paragraph:
            print('we are here')
            count_begin = groups[count - 1]
            print('count begin ', count_begin)

            begin_idx = paragraph_list.index(count_begin)
            try:
                end_idx = paragraph_list.index(groups[count + 1])
            except ValueError as e:
                print(e)
                continue

            for paragraph in paragraph_list[begin_idx + 1:end_idx + 1]:
                full_names.append(string_for_name.format(paragraph))

        elif g == 'bis' and not paragraph:
            count_begin = groups[count - 1]
            while count_begin < groups[count + 1]:
                if count_begin[-1].isalpha() and groups[count + 1][-1].isalpha():
                    end_letter = chr(ord(count_begin[-1]) + 1)
                    count_begin = groups[count - 1][:-1] + end_letter
                    full_names.append(string_for_name.format(count_begin))
                    # full_names.append('P{}A_S_N_'.format(count_begin))
                elif count_begin[-1].isalpha() and not groups[count + 1][-1].isalpha():
                    count_begin = int(count_begin[:-1])
                    count_begin += 1
                    count_begin = str(count_begin)
                    full_names.append(string_for_name.format(count_begin))
                elif not count_begin[-1].isalpha() and groups[count + 1][-1].isalpha():
                    count_begin = int(count_begin)
                    count_begin += 1
                    count_begin = str(count_begin)
                    if count_begin > groups[count + 1][-1]:
                        break
                    full_names.append(string_for_name.format(count_begin))
                else:
                    count_begin = int(count_begin)
                    count_begin += 1
                    count_begin = str(count_begin)
                    full_names.append(string_for_name.format(count_begin))

        elif groups[count - 1] == 'bis' and count != 0:  # no repetitions
            print('BIS IS PREVIOUS')
            continue

        else:
            print('we are here', g)
            if type(g)==list:
                g = g[0]
            full_names.append(string_for_name.format(g))
    if delete_last:
        print('DELETE LAST')
        print('last = ', full_names[-1])
        del full_names[-1]
    print(full_names)
    all_names += full_names


def name_creation(name, nomenclature_letters):
    nomenclature_name = ''
    full_names = [nomenclature_name]
    # CREATE NAMES
    for k,letter in enumerate(name):
        print('FULLNAMES: ', full_names)

        print('fist element: ', full_names[0])
        print(len(letter))
        if len(letter)==1:

            full_names[-1] += nomenclature_letters[k]+letter[0]
            print('full names last at single', full_names[-1])
        elif len(letter)==0:
            full_names[-1] += nomenclature_letters[k] + '_'
        else: # more than one id following
            current_last_element = full_names[-1]
            c_ = 1
            before_bis_count = 0
            for p, l in enumerate(letter):
                print('to be added: ',current_last_element)
                # if bis is there

                if l == 'bis':
                    c_ = generate_names_if_bis(l, letter, p, full_names, nomenclature_letters, k)

                elif letter[p - 1] == 'bis' and p != 0:  # no repetitions
                    continue

                else:
                # generate name if not bis
                    before_bis_count = generate_names_if_not_bis(l, p, c_ , k, full_names, nomenclature_letters, before_bis_count, letter)

                print('full_names[-p-1]',full_names[-1])

                print('first full names: ', full_names)

            print(letter)
            print('LEN letter: ',len(letter))
            print('FULL NAMES: ', full_names)
            print('LEN FULL NAMES', len(full_names))
            print(-len(letter)-(c_-2))
            if (c_!= 1):
                print('c is not 1: ', c_)
                print('before_bis : ', before_bis_count)
                print('alleged fist element: ', full_names[-c_-before_bis_count-1])
                del full_names[-c_-before_bis_count-1]
            else:
                print('c is 1: ', c_)
                print('alleged fist element: ', full_names[-len(letter) - 1])
                del full_names[-len(letter)-1]

    return full_names