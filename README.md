# laws_preprocessing
Reformat Laws

# Introduction 

The goal of the current practical is to reformat the provisions of the BGB so that their new representation closely resembles they way in which a practicing lawyer would read them. My conviction is that a lawyer does not read the text of a provision sequentially but rather observes the logically connected parts of that provision as one whole inseparable piece of information. Thus some parts of the provision are reread every time some other part to which they are logically related appears in the provision. This logical relation in my opinion is realized in two ways : 
 1. by referencing that part of the text explicitly 
 2. by the order and hierarchy of the clauses of the provision -> i.e. the text of the "Absatz" is always logically related to the text of the "Nummer" inside that "Absatz"
Thus I have devised this new way of representing legal texts an example of which can be seen in the picture below. The parts of the provision that are in hierarchical relation to one another are stored as one single text. The references are stored in a separate datafield.

The currently described API has been tested to work with BGB on the gesetze-im-internet edition. It should be able to work with minor changes on most of the other laws posted in gesetze-im-internet.

## Motivation
Due to the fact that law is a text-based discipline and that the quantity of legal documentation of all kinds (legislative acts, court decisions, administrative acts, etc.) grows hastily, proportionally to the growth of world population and complexity of economic relations between different actors on both the international and the domestic scene, devising a proper way of storing and retrieving legal information has attracted much academic interest. The author of the current work, himself a law graduate, proposes an innovative way to store the texts of the statutes in manner that mirrors the way a practicing lawyer would read a legal text. The method will enable a more precise statute retrieval system than the currently available - i.e. it will be possible to retrieve correctly the clause of the "lowest order" inside a provision. The state of the art algorithms, known to the author (Predicting associated statutes for legal problems : Liu et al. 2015, Improving Legal information retrieval by distributional composition with term order probabilities Carvalho et al. 2017), produce a provision level result - i.e. if a provision is many paragraphs long and each paragraph has many sub-clauses the user will get a mostly unreadable and useless result - the whole long provision. This is especially detrimental in areas where the parties are not financially equal such as labor law or consumer protection law. To ensure even partial equality we have to create ways for the financially weaker party to get at least enough correct information for free. A precise statute retrieval system is a step in the right direction.  
The paper that is most similar and yet in some respects lags behind is Lexical-Morphological Modelling for Legal text Analysis by Carvalho et al. 2016 section 4.1. - where they describe the way they conduct the preprocessing. Later in this writing we will see how the currently proposed method differs from the one proposed in the cited paper.

## Terminology created by the author for the needs of the current work 
In the current work as in the Bachelor Thesis I am going to write I will use the following terminology: 
 
 'hierarchy' inside a provision -> the logical order in which a lawyer reads a legal text -> in the context of BGB the hierarchy inside a provision is as follows : Absatz, Satz, Nummer, Buchstabe, Doppelbuchstabe.

 'type' of a clause -> the hierarchical absolute position inside a provision that a clause takes -> Absatz, Satz, Nummer, Buchstabe, etc.

 'order' of a clause -> the hierarchical relative position inside a provision that a clause takes to other clauses (higher, highest, lower, lowest).

 'outer' structure of a law -> the sections which the provisions are organized in inside the law

 'inner' structure of a law -> synonymous to the hierarchy of a provision

## Example 
To illustrate why a system that retrieves provisions imprecisely (that is at provision level) is of no use to a layman I will give paragraph 309 BGB as an example. It consists of 15 sub-clauses most of which have their own sub-clauses of which some even have their own sub-clauses! The whole paragraph printed in a book takes up to 2 pages, in a text editor more than 130 lines.
 
The approach proposed by the author lets us combine the normatively connected parts of the provision and provide to the user a "lowest-order-clause" representation of the provision:

'''Paragraph 309 Nr. 8 Buchstabe b Doppelbuchstabe bb'''


 Auch soweit eine Abweichung von den gesetzlichen Vorschriften zulässig ist, ist in Allgemeinen Geschäftsbedingungen unwirksam
  8.  (Sonstige Haftungsausschlüsse bei Pflichtverletzung) 
    b)  (Mängel)eine Bestimmung, durch die bei Verträgen über Lieferungen neu 	  hergestellter Sachen und über Werkleistungen
      bb) (Beschränkung auf Nacherfüllung)die Ansprüche gegen den Verwender insgesamt oder bezüglich einzelner Teile auf ein Recht auf Nacherfüllung beschränkt werden, sofern dem anderen Vertragsteil nicht ausdrücklich das Recht vorbehalten wird, bei Fehlschlagen der Nacherfüllung zu mindern oder, wenn nicht eine Bauleistung Gegenstand der Mängelhaftung ist, nach seiner Wahl vom Vertrag zurückzutreten;

As we see in the example we get a coherent and precise representation of the cited provision up to the lowest order clause in its logical context within the provision. This is the novelty in the approach which lets it shine in comparison to the dim background that the preceding papers present.

# Implementation 

There are two main difficulties when I devised the concept - first, there are two structures that we have to have in mind when preprocessing statute texts and second we have to deal with the references. After the whole algorithm was carried out the total number of files stored is 5197, which is more than 2 times the number of provisions (2385) inside the BGB. This is due to the fact that I store the provisions with precision to their lowest order clause.

## The two structures of a statute text 

### Outer structure of a law 
The statute consists of different hierarchical sections : in the context of BGB : Buch, Abschnitt, Titel etc. They carry a lot of useful systematic information and are the key to conducting systematic interpretation of the law. Without this information we would treat the law only linguistically as a heap of letters neglecting a most crucial principle - lex specialis derogat legi generali. As I will broadly discuss in my Bachelor thesis having the name of those sections and weighting them accordingly provides us the opportunity to conduct systematic interpretation of the law, which again is a novelty that has not been described in the papers known to the author.

My implementation deduced the outer structure automatically without the need for user interaction : i.e. the only input that the user has to give is the link to the full html text of the law taken from gesetze-im-internet.

The final output in this step would be for example:
§ 2351
"Buch": "Erbrecht", 
"Abschnitt": "Erbverzicht", 
"Titel": "", 
"Untertitel": "", 
"Kapitel": "", 
"Unterkapitel": ""

### Inner structure of a law (hierarchy inside a provision) 
The hierarchy inside a provision is again automatically deduced via building the logical tree of the provision with the clauses of lowest order being the leafs and the clauses of highest order being the root. Building this data structure allows us to then present the lowest order clauses in their logical context inside the provision without losing information but retaining a high level of precision. The presented way of storing the provision and building the inner structure of a law mirrors the way a lawyer would read the law: 

Using the example of '''Paragraph  309 Nr. 9 Buchstabe c''' the representation of the higher order clauses would be: 

[["_ _ ", "Auch soweit eine Abweichung von den gesetzlichen Vorschriften zulässig ist, ist in Allgemeinen Geschäftsbedingungen unwirksam"],      ""], 

[["9. ", "(Laufzeit bei Dauerschuldverhältnissen)bei einem Vertragsverhältnis, das die regelmäßige Lieferung von Waren oder die regelmäßige Erbringung von Dienst- oder Werkleistungen durch den Verwender zum Gegenstand hat,"],          "dies gilt nicht für Verträge über die Lieferung als zusammengehörig verkaufter Sachen sowie für Versicherungsverträge;"]]

Each higher order clause is represented as a list containing 2 elements -> a list which holds the id of the clause (e.g. 9. or b) or _ _ if there are no other clauses of that order) and the text of the clause before any sub-clauses, the second element is the continuation of the clause after all sub-clauses. After reaching the lowest order clause the logical tree structure is concatenated in a way that the first part of a higher order clause precedes all first parts of lower order clauses and the continuation of each lower order clause precedes the continuation of each higher order clause: as in the following example:

'''Paragraph  309 Nr. 9 Buchstabe c''' as represented by my algorithm
 Auch soweit eine Abweichung von den gesetzlichen Vorschriften zulässig ist, ist in Allgemeinen Geschäftsbedingungen unwirksam
    9.  (Laufzeit bei Dauerschuldverhältnissen)bei einem Vertragsverhältnis, das die regelmäßige Lieferung von Waren oder die regelmäßige Erbringung von Dienst- oder Werkleistungen durch den Verwender zum Gegenstand hat,
         c) zu Lasten des anderen Vertragsteils eine längere Kündigungsfrist als drei Monate vor Ablauf der zunächst vorgesehenen oder   stillschweigend verlängerten Vertragsdauer;
    dies gilt nicht für Verträge über die Lieferung als zusammengehörig verkaufter Sachen sowie für Versicherungsverträge;

### Logical operators between same-order-clauses 
The author having in mind that if the same order clauses have been logically joined by the logical operator 'and' than they will only have legal effect cumulatively, has provided for differentiated approach towards the different operators. If two same-order-clauses have been connected by 'and' then they are stored together as if they were one clause. This is because as mentioned above they only have legal effect together - if their hypotheses are cumulatively met. In all other cases - the clauses are stored separately as they describe different hypotheses and should be treated as separate provisions.
This is another novelty which has not been described in any of the papers, known to the author.

## Storing the thus preprocessed provisions 
In order to store the provisions in a way that will make it easy to later use the files properly I have introduced the following nomenclature which is hard coded and may have to be changed according to the inner structure of the other law texts we want to preprocess. 
P - paragraph
A - Absatz
S - Satz
B - Buchstabe 
D - Doppelbuchstabe

A provision name would look like this : Paragraph  309 Nr. 9 Buchstabe c -> P309A_S_N9BcD_ : i.e. if a higher order clause is not named (has no number as in this case) there is an underscore, the same happens if a lower order clause is missing. Thus all provisions are named in the same fashion.


## Dealing with references 
The current work concentrates on the inner-law references - that is - references to provisions inside the law - all other references are explicitly deleted. The module for finding references was also programmed for the current practical and is based on writing a number of regexes. The numerous tests carried out show that it can find all referenced inside the BGB.
The references are then formatted the same way the files are named (after the same nomenclature) and after retrieving the file the lowest order clause stored in that file is added as a text reference to the referencing provision. Having a separate datafield for references would allow us to later weight a match on the reference accordingly. 

## Final data structure 
The provisions are stored in json format which allows us to easily post them to a solr server and test the functionality which that search engine provides. The data fields are the following.


 "Provision" : the preprocessed provision text

 "Lowest_order_clause" : the clause of the lowest order -> if the provision is referenced that field is copied to the other (referencing) provision's references_text datafield

 "Provision_title" : the title of the provision 

 "Provision_id" : provision number (e.g. 440)

 "References" : the referenced provisions in the nomenclature described above

 "Parent_clauses" : clauses that are concatenated with the lowest order clause

 "References_text" : lowest_order_clauses of the provisions that are referenced 
hierarchical position of the provision inside the law's structure:

 "Buch"

 "Abschnitt" 
 
 "Titel" 
 
 "Untertitel" 

 "Kapitel" 

 "Unterkapitel"


# Future work 
The continuation of the current work will be in my Bachelor thesis where I will test my assumptions that storing the hierarchical information would allow us to conduct systematic interpretation of the laws and that formatting the provisions in the way presented in the current work will lead to a much more precise legal IR.
The proposed approach if proven correct can be easily extended to all normative acts and be the foundation for creating a reliable en mass used statute retrieval engine that will improve the position of the financially weak parties against the large capital.
