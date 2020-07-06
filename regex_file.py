"""
CRAWL https://dejure.org/gesetze/BGB/ and store the provisions as follows
{"link"
 "gesetz"
 "buch"
 "abschnitt"
 "titel"
 "untertitel"
 "kapitel"
 "unterkapitel"
 "norm"
 "references"
 "other_norms_links"
}
"""
import requests
import bs4
import re
from regular_expressions import *
# DEFINE HEADERS
headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"ccept-Encoding":"gzip, deflate, br",
"Accept-Language":"en-US,en;q=0.5",
"Connection"	:"keep-alive",
"Host":"pytorch.org",
"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0"}

# START SESSION
session=requests.Session()

# request a web-page
#response = session.get('https://dejure.org/gesetze/BGB/305.html', headers=headers).text

#file = open('BGB - Bürgerliches Gesetzbuch.html','r')
#soup = bs4.BeautifulSoup(response,'html5lib')
#print(soup.find('div',{'id':'gesetzestext'}).text.strip())
#soup = bs4.BeautifulSoup(file.read(),'html5lib')
"""
# parse


thing = soup.find_all('div',{'title':re.compile('Einzelnorm|Gliederung')})
for i in range(1,10):
    print(thing[i].text)
    print('\n\n\n')
#print(soup.find('div',{'title':re.compile('\bEinzelnorm\b|\bGliederung\b')}).text)

"""
#a = 'Zu der Beschaffenheit nach § 2321 und Art. 23 Absatz 5, 6 bis 7, 25 Absatz 8 Satz 2, 6 Nr. 2, 3 und 4 des BGB gehören auch Eigenschaften, die der Käufer nach den öffentlichen Äußerungen des Verkäufers'
#matching = re.compile('(I[XV]|V?I*)')
#a = 'nach den §§ 440, 323 und 326 Abs. 5 Nr. 4 und 6 von dem Vertrag zurücktreten oder nach § 441 den Kaufpreis mindern und kostet 5 euro'
#a = ' Für Absatz 3, 4, 6 bis 7 Satz 2, 6 und Absatz 3 Satz 2, 3 und 4 Nummer 2 und 3 und Absatz 4 § 491 Absatz 2 Nummer 1 bis 5, Absatz 3 Satz 2 und Absatz 4 und § 434 Absatz 23 Nummer 12 die §§ 491a bis 495 und 505a bis 505e Abs. 5 und § 240 Abs. 5 Entbehrlichkeit der Bestimmung der Nummer 8 einer § 5 Absatz 5, 6a bis 9 Satz 6 bis 8, Absatz 10a bis 11 Frist zur Abhilfe und für die Entbehrlichkeit einer Abmahnung findet § 323 Abs. 5 und Absatz 6 Satz 2 Nummer 1 und 2 Buchstabe a und b Doppelbuchstabe cc, bb und dd entsprechende Anwendung. Die Bestimmung einer Frist zur Abhilfe und eine Abmah'

def find_references(a):
    paragraph_list = download_paragraph_list('https://www.gesetze-im-internet.de/bgb/index.html')


    regex = '(§+ )?(\d+[a-z]? )?(((Abs\.|Absatz)? \d+?)|(I[XV]|V?I*) )?((Satz|S\.) \d+ )?(Nr\. \d+ )?(des )?(\w*[A-Z]\w*[A-Z]\w*)?( und )?( bis )?,?'

    number_regex = '\d+[a-z]?'
    article_regex = '(Art. |Artikel )'
    paragraph_regex = '(§{1,2} )'
    article_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(article_regex,
                                                                               number_regex,
                                                               article_regex,
                                                                               number_regex)
    paragraph_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(paragraph_regex,
                                                                               number_regex,
                                                               paragraph_regex,
                                                                               number_regex)
    roman_numbers_regex = '(IX|IV|VI{0,3}|I{1,3})'
    absatz_abreviation_regex= '(Abs\.\s|Absatz\s)'
    absatz_german_regex  = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(absatz_abreviation_regex,
                                                                               number_regex,
                                                               absatz_abreviation_regex,
                                                                               number_regex)

    absatz_german_regex_standalone  = '(({}{})((( und |, | bis ){})+)?\s?)'.format(absatz_abreviation_regex,
                                                                               number_regex,
                                                                               number_regex)

    absatz_roman_regex = '((\w{}\w)(( und {}|, {}| bis {})+)?\s?)'.format(roman_numbers_regex,
                                                                roman_numbers_regex,
                                                                    roman_numbers_regex,
                                                                    roman_numbers_regex)

    absatz_regex = '({}|{})'.format(absatz_german_regex,absatz_roman_regex)

    satz_regex = '(Satz\s|S\.\s)'.format(number_regex)
    satz_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(satz_regex,
                                                                               number_regex,
                                                               satz_regex,
                                                                               number_regex)
    nummer_regex = '(Nr\. |Nummer\s)'
    nummer_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(nummer_regex,
                                                                               number_regex,
                                                               nummer_regex,
                                                                               number_regex)
    buchstabe_regex1 = '(Buchstaben? )'
    buchstabe_regex2 = '[a-z]\)'
    letter_regex = '\\b[a-z]\\b'
    buchstabe_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(buchstabe_regex1,
                                                                          letter_regex,
                                                                          buchstabe_regex1,
                                                                          letter_regex)

    double_letter_regex = '\\b[a-z]{2}\\b'
    doppelbuchstabe_regex = '(Doppelbuchstaben? )'
    doppelbuchstabe_all_regex = '(({}{})((( und |, | bis ){}?{})+)?\s?)'.format(doppelbuchstabe_regex,
                                                                                double_letter_regex,
                                                                                doppelbuchstabe_regex,
                                                                                double_letter_regex)
    gesetz_regex = '((des )?((\w*[A-Z]\w*[A-Z]\w*)|([A-Z]\w*gesetzes)))'
    conjugations_regex = '(\s?und |\s?bis|, )'

    full_regex = paragraph_regex + '?' +\
                            absatz_regex + '?'+ \
                            satz_regex + '?'+ \
                          nummer_all_regex + '?'+\
                          gesetz_regex +'?' +\
                          conjugations_regex + '?'
    #print(full_regex)

    """'('+ paragraph_regex+absatz_regex+satz_all_regex+nummer_all_regex+gesetz_regex +')'+\
                          '|'+ '('+ absatz_regex+satz_all_regex+nummer_all_regex+gesetz_regex + ')'+'|'+ '('+\
                          
                           ''"""
    """                    '('+ paragraph_regex+absatz_regex+satz_all_regex+ '?'+nummer_all_regex+'?'+gesetz_regex +'?'+')'+'|'+\
                          '('+ absatz_regex+satz_all_regex+ '?'+nummer_all_regex+'?'+gesetz_regex +'?'+')'+'|'+\
                         '('+ satz_all_regex+nummer_all_regex +')' +'|'+\
                        '('+ paragraph_regex+ ')'"""

    PARAGRAPH_ORDER_MATCHING = re.compile(
        paragraph_all_regex + \
        '(' +'(' + absatz_german_regex + '?' + satz_all_regex + '?'+')'+'?' + '('+ nummer_all_regex \
        + '?' + buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?'+')' + ')'+'?'
                          )
    long_paragraph = paragraph_all_regex + \
        '(' +'(' + absatz_german_regex + '?' + satz_all_regex + '?'+')'+'?' + '('+ nummer_all_regex \
        + '?' + buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?'+')' + ')'+'?'
    long_absatz = '('+absatz_german_regex + satz_all_regex + '?' +'|'+absatz_german_regex + '?' +\
    satz_all_regex +')'+ '('+ nummer_all_regex + '?' +\
    buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?' + ')' +'?'

    ABSATZ_ORDER_MATCHING = re.compile(
    '('+absatz_german_regex + satz_all_regex + '?' +'|'+absatz_german_regex + '?' +\
    satz_all_regex +')'+ '('+ nummer_all_regex + '?' +\
    buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?' + ')' +'?'
                          )
    paragraph_order = long_paragraph + '((((und |, |bis ){})+)?\s?)?'.format(long_absatz)
    other_law_paragraph = long_paragraph + '((((und |, |bis ){})+)?\s?)?'.format(long_absatz) + gesetz_regex
    other_law_paragraph2 = paragraph_order + '((((und |, |bis ){})+)?\s?)?'.format(paragraph_order)\
                           + gesetz_regex
    a = re.sub(other_law_paragraph2, ' ', a)
    a = re.sub(other_law_paragraph, ' ', a)

    print(a)
    PARAGRAPH_ORDER_MATCHING_FINAL = re.compile(
        long_paragraph + '((((und |, |bis ){})+)?\s?)?'.format(long_absatz)
    )
    long_article  = article_all_regex + paragraph_all_regex + '?' \
         +'(' + absatz_german_regex + '?' + satz_all_regex + '?'+')'+'?' + '('+ nummer_all_regex + '?' +\
    buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?' + ')' +'?'

    NUMMER_ORDER_MATCHING = re.compile(
    nummer_all_regex + buchstabe_all_regex + '?' + doppelbuchstabe_all_regex +'?'
                      )

    ARTICLE_ORDER_MATCHING = long_article + '((((und |, |bis |in Verbindung mit ){})+)?\s?)?'.format(paragraph_order)
    a = re.sub(ARTICLE_ORDER_MATCHING,' ', a)
    #matching = re.compile(buchstabe_all_regex)

    # TODO: find a way to parse the matches in the following format P...A...S... etc just as is the nomenclature
    # TODO: DONE! instead of checking if d in None -> create a copy of the text and substitute the matches by ' ' and then carry oout the same search with the lower hierarchy regexes
    # use the fact that if more than one ids of higher order (i.e. Art. or Absatz. are conjugated like this Art. 2, 3 und 5
    # then only the last one can have also an id of lower order -> Art. 2, 3 and 5 Abs. 7 und 8 Nr. 8 because otherwise
    # there won't be clarity as to which id is actually referred -> e.g. Art. 2, 3 Abs 7 und 5 Abs. 8 -> in such a case
    # it won't be clear if Abs. 7 and 5 of the 3rd Art. are refered and Abs. 8 of the current provision -> at least at
    # no point in the law text did I find such a reference. For now I have only found references of this typpe : §§ 495, 499 Abs. 2 und § 500 Abs. 1 Satz 2
    # where only the last referred Id contains the id of a clause of lower order.
    # TODO: when parsing the matches take into account that there may be more than one child nodes !
    # TODO: more than one paragraph simultaneously
    # TODO: deal with 'BIS'
    # TODO: think what to do when bis is between numbers only one of which ends in a letter e.g. 345a bis 347 or 256 bis 258e
    # TODO: after all functionality is fixed -> modularize code!
    print('PARAGRAPH')
    nomenclature_letters = ['P', 'A', 'S', 'N', 'B', 'D']
    # paragraph order matching
    all_names = []
    for c,i in  enumerate(PARAGRAPH_ORDER_MATCHING_FINAL.finditer(a)):
        print('PP: ')
        print(i.group())

        contains_absatz = False
        # paragraph order
        groups = paragraph_id(paragraph_all_regex, i.group())
        # the absaetze found are only relevant to the last paragraph of the grouping
        for j in re.compile(ABSATZ_ORDER_MATCHING).finditer(i.group()):
            contains_absatz= True
            print('type groups: ', type(groups[-1]))
            if type(groups[-1]) == list:
                name = [groups[-1]]
            else:
                name = [[groups[-1]]]
            print('original name', name[-1])
            print('CURRENT GROUP')
            print(j.group())
            print(j.span())

            # absatz ID
            find_id(absatz_german_regex, name, j.group(), r'und|,|Abs\.|Absatz', 'ABSATZ')
            print('NAME: ',name)

            # satz id
            find_id(satz_all_regex, name, j.group(), r'und|,|Satz', 'SATZ')

            #number id
            find_id(nummer_all_regex, name, j.group(), r'und|,|Nummern?|Nr\.', 'NUMMER')

            # buchstabe id
            find_id(buchstabe_all_regex, name, j.group(), r'und|,|Buchstaben?', 'BUCHSTABE')

            # doppelbuchstabe id
            find_id(doppelbuchstabe_all_regex, name, j.group(), r'und|,|Doppelbuchstaben?', 'DOPPELBUCHSTABE')
            print('NAME at THE END: ', name)


            # ALL FINE UNTIL HERE
            full_names = name_creation(name, nomenclature_letters)
            print('FULL NAMES: ', full_names)
            # fill the missing letters
            finalize_name_creation(full_names, nomenclature_letters, all_names)
        # DEAL WITH THE FOUND ABSAETZE that do not come with Absatz id etc.
        if contains_absatz:
            try:

                if groups[-2] == 'bis':
                    print(groups)
                    print('BISSWSWSS')
                    generate_names_full_referenced_paragraphs(groups, paragraph_list, all_names, nomenclature_letters,
                                                              True, True)
                else:
                    print('GENERATING REST NAMES')
                    generate_names_full_referenced_paragraphs(groups[:-1], paragraph_list, all_names,
                                                              nomenclature_letters)
            except IndexError:
                generate_names_full_referenced_paragraphs(groups[:-1], paragraph_list, all_names, nomenclature_letters)
        else:
            generate_names_full_referenced_paragraphs(groups, paragraph_list, all_names, nomenclature_letters)

        a = re.sub(i.group(),' ', a)
    # TODO: create the functionality to find lone absaetze
    # instead of checking -> simply do the procedure for the last -> if it is empty : it is going to be empty
    # and do the absolutely normal procedure for the others
    print('\n\n\n\n\nABSATZ')

    for c, i in enumerate(ABSATZ_ORDER_MATCHING.finditer(a)):
        print('AA')
        print(i.group())
        # absatz ID
        groups = paragraph_id(absatz_german_regex, i.group(),r'und|,|Absatz|Abs.')
        print('NAME: ', groups)
        try: # only satz was found but no Absatz which is not a level we regard in this version
            name = [groups[-1]]
        except IndexError as e:
            print(e)
            continue

        find_id(satz_all_regex, name, i.group(), r'und|,|Satz', 'SATZ')
        print('name: ', name)
        # number id
        find_id(nummer_all_regex, name, i.group(), r'und|,|Nummern?|Nr\.', 'NUMMER')
        print('name: ', name)
        #find_id()
        # buchstabe id
        find_id(buchstabe_all_regex, name, i.group(), r'und|,|Buchstaben?', 'BUCHSTABE')
        print('name: ', name)
        # doppelbuchstabe id
        find_id(doppelbuchstabe_all_regex, name, i.group(), r'und|,|Doppelbuchstaben?', 'DOPPELBUCHSTABE')
        print('NAME at THE END: ', name)

        # ALL FINE UNTIL HERE
        full_names = name_creation(name, nomenclature_letters[1:])
        print('FULL NAMES: ', full_names)
        # fill the missing letters
        finalize_name_creation(full_names, nomenclature_letters[1:], all_names)
        print(len(groups))
        # analogous check to the is_absatz
        try:

            if groups[-2] == 'bis':
                print(groups)
                print('BISSWSWSS')
                generate_names_full_referenced_paragraphs(groups, paragraph_list, all_names, nomenclature_letters[1:], False, True)
        except IndexError:
            generate_names_full_referenced_paragraphs(groups[:-1], paragraph_list, all_names, nomenclature_letters[1:], False)

        a = re.sub(i.group(),' ', a)
        a = re.sub(ABSATZ_ORDER_MATCHING,' ', a)




    print('NUMMER')
    for c, i in enumerate(NUMMER_ORDER_MATCHING.finditer(a)):
        print('NN')
        print(i.group())
        groups = paragraph_id(nummer_all_regex, i.group(), r'und|,|Nr\.|Nummern?')
        print('NAME: ', groups)
        name = [groups[-1]]
        find_id(buchstabe_all_regex, name, i.group(), r'und|,|Buchstaben?', 'BUCHSTABE')
        print('name: ', name)
        # doppelbuchstabe id
        find_id(doppelbuchstabe_all_regex, name, i.group(), r'und|,|Doppelbuchstaben?', 'DOPPELBUCHSTABE')
        print('NAME at THE END: ', name)

        # ALL FINE UNTIL HERE
        full_names = name_creation(name, nomenclature_letters[3:])
        print('FULL NAMES: ', full_names)
        # fill the missing letters
        finalize_name_creation(full_names, nomenclature_letters[3:], all_names)
        print(len(groups))
        # analogous check to the is_absatz
        try:

            if groups[-2] == 'bis':
                print(groups)
                print('BISSWSWSS')
                generate_names_full_referenced_paragraphs(groups, paragraph_list, all_names, nomenclature_letters[3:], False, True)
        except IndexError:
            generate_names_full_referenced_paragraphs(groups[:-1], paragraph_list, all_names, nomenclature_letters[3:], False)

        a = re.sub(i.group(),' ', a)
        a = re.sub(ABSATZ_ORDER_MATCHING,' ', a)
    return all_names


if __name__ == '__main__':
    print('absolute last all names', find_references('Herstellers (§ 4 Abs. 1 und 2 ) '))






































































































"""
# find structural data
structure = soup.find('div',{'id':'headgesetz'})
# convert <br> to \n
for i in soup.find_all('br'):
    i.replace_with('\n')
law_name = structure.find('h2',{'id':'gesetzesname'}).text

# HIERARCHICAL PLACE OF THE NORM
structural_units = structure.find_all('table',{'class':'gesetzesgliederung'})
hierarchy_list = list(map(lambda x: x.text.split('(')[0].strip().split('-')[1].strip(),structural_units))
print(hierarchy_list)

# PROVISION NUMBER
provision_id = soup.find('h1',{'id':'normueberschrift'}).text
print(provision_id.split('\n'))

# PROVISION TEXT
provision_text = soup.find('div',{'id':'gesetzestext'})
print(provision_text.text)

"""