# Prints a list of a grammar's non-terminal's FIRSTS and FOLLOWS
# Can deal with recursive grammars

# usage: $python parser.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/10/30

EPSILON = '\' \''
EOF ='$'
BODY_START_INDEX = 2

def setToString(set, separator):
    """
    Creates a string made of the elements of a set 
    separated by a given string
    Arguments:
        set: a python set
        separator: the string to insert between set elements
    Returns:
        The string created with the list of set elements
    """
    resultString = ""
    for item in set:
        resultString += item + separator
    return resultString[:-len(separator)]

def header(production):
    '''
    Returns the header portion of a grammar's production
    Arguments:
        production: a python list of tokens representing a production
    Returns:
        The production's header as a string
    '''
    return production[0]

def body(production):
    '''
    Returns the body portion of a grammar's production
    Arguments:
        production: a python list of tokens representing a production
    Returns:
        The production's body as a list of tokenss
    '''
    return production[2:]

def firstsOfString(string):
    '''
    Return the set of firsts of a string
    Arguments:
        string: a python list of grammar symbols
    Returns:
        The set of firsts for the sequence of symbols
    '''
    stringFirsts = set()
    for i in range(len(string)):
        if string[i] in nonTerminals:
            nonTermFirsts = firsts[string[i]]
            stringFirsts.update(nonTermFirsts)
            stringFirsts.discard(EPSILON)
            if not EPSILON in nonTermFirsts:
                return stringFirsts
        else:
            stringFirsts.add(string[i])
            return stringFirsts
    stringFirsts.add(EPSILON)
    return stringFirsts

def markEpsilons(nonTerminal):
    '''
    Replaces all ocurrences of a non-terminal with epsilon in the 
    bodies of productions for marking, and repeats recursively 
    when a production that has only epsilon in its body is found
    Arguments:
        nonTerminal: the non-terminal to replace
    '''
    for production in productionsForMarking:
        bodyIsAllEpsilon = True
        for i in range(BODY_START_INDEX, len(production)):
            if production[i] == nonTerminal:
                production[i] = EPSILON

            if production[i] != EPSILON:
                bodyIsAllEpsilon = False
        
        producingNonTerm = header(production)
        if bodyIsAllEpsilon and EPSILON not in firsts[producingNonTerm]:
            firsts[producingNonTerm].add(EPSILON)
            markEpsilons(producingNonTerm)

def propagateFirstsSeeds(nonTerminal, seeds):
    '''
    Uses the firsts dependency graph to propagate firsts
    between non-terminals
    Arguments:
        nonTerminal: a non-terminal to propagate to
        seeds: a set of tokens to propagate
    '''
    firsts[nonTerminal].update(seeds)
    for node in reverseFirstsDependencies[nonTerminal]:
        propagateFirstsSeeds(node, seeds)

def propagateFollowsSeeds(nonTerminal, seeds):
    '''
    Uses the follows dependency graph to propagate follows
    between non-terminals
    Arguments:
        nonTerminal: a non-terminal to propagate to
        seeds: a set of tokens to propagate
    '''
    follows[nonTerminal].update(seeds)
    for node in reverseFollowsDependencies[nonTerminal]:
        propagateFollowsSeeds(node, seeds)

# Parse input into list of tokens and initialize data structures
numberOfProductions = int(input().strip())
productions = []
nonTerminals = set()
startNonTerm = None

productionsForMarking = []
firsts = dict()
firstsSeeds = dict()
reverseFirstsDependencies = dict()

follows = dict()
followsSeeds = dict()
reverseFollowsDependencies = dict()

for i in range(numberOfProductions):
    line = input().strip()

    # Store each production as a list of tokens
    production = line.split()
    if production[2] == '\'' and production[3] == '\'':
        production.pop()
        production.pop()
        production.append(EPSILON)
    productions.append(production)
    productionsForMarking.append(production.copy())

    # Store all non-terminals
    nonTerminal = header(production)
    nonTerminals.add(nonTerminal)

    # Initialize set of empty set of first and follows for each non-terminal
    firsts[nonTerminal] = set()
    firstsSeeds[nonTerminal] = set()
    reverseFirstsDependencies[nonTerminal] = set()

    follows[nonTerminal] = set()
    followsSeeds[nonTerminal] = set()
    reverseFollowsDependencies[nonTerminal] = set()

startNonTerm = header(productions[0])


# Find which non-terminals have epsilon in their firsts
for production in productionsForMarking:
    nonTerminal = header(production)
    if production[BODY_START_INDEX] == EPSILON and EPSILON not in firsts[nonTerminal]:
        firsts[nonTerminal].add(EPSILON)
        markEpsilons(nonTerminal)

# Build firsts dependency graph and find firsts seeds
for production in productions:
    if production[BODY_START_INDEX] == EPSILON:
        continue

    nonTerminal = header(production)
    for i in range(BODY_START_INDEX, len(production)):
        token = production[i]
        if token in nonTerminals:
            reverseFirstsDependencies[token].add(nonTerminal)
            if EPSILON not in firsts[token]:
                break
        else:
            firstsSeeds[nonTerminal].add(token)
            break

# Propagate firsts seeds
for nonTerminal in nonTerminals:
    if len(firstsSeeds[nonTerminal]) > 0:
        propagateFirstsSeeds(nonTerminal, firstsSeeds[nonTerminal])


# Build follows dependency graph and find firsts seeds
followsSeeds[startNonTerm].add(EOF)
for production in productions:
    for i in range(BODY_START_INDEX, len(production)):
        token = production[i]
        if token in nonTerminals:
            if i < len(production) - 1:
                betaFirsts = firstsOfString(production[i + 1:])
                followsSeeds[token].update(betaFirsts)
                followsSeeds[token].discard(EPSILON)
                if EPSILON in betaFirsts:
                    reverseFollowsDependencies[header(production)].add(token)
            else:
                reverseFollowsDependencies[header(production)].add(token)

# Propagate follows seeds
for nonTerminal in nonTerminals:
    if len(followsSeeds[nonTerminal]) > 0:
        propagateFollowsSeeds(nonTerminal, followsSeeds[nonTerminal])


# Show first and follow sets
for nonTerminal in nonTerminals:
    print(nonTerminal + " => FIRST = {" + setToString(firsts[nonTerminal], ",") + "}, ", end="")
    print("FOLLOW = {" + setToString(follows[nonTerminal], ",") + "}")