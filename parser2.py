# Prints a list of a grammar's non-terminal's FIRSTS and FOLLOWS

# usage: $python parser.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/10/05

EPSILON = '\'e\''
EPSILON_FOR_PRINT = '\' \''
EOF ='$'

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
        resultString += (EPSILON_FOR_PRINT if item == EPSILON else item) + separator
    return resultString[:-len(separator)]

def header(production):
    return production[0]

def body(production):
    return production[2:]

def firstsOfNonTerm(nonTerminal):
    '''
    Return the set of firsts of a non terminal
    '''
    # Return stored set of firsts if its been calculated already
    if len(firsts[nonTerminal]) != 0:
        return firsts[nonTerminal]

    for production in productions:
        if header(production) == nonTerminal:
            firsts[nonTerminal].update(firstsOfString(body(production)))

    return firsts[nonTerminal]

def firstsOfString(string):
    '''
    Return the set of firsts of a string
    '''
    stringFirsts = set()
    for i in range(len(string)):
        if string[i] in nonTerminals:
            nonTermFirsts = firstsOfNonTerm(string[i])
            stringFirsts.update(nonTermFirsts)
            stringFirsts.discard(EPSILON)
            if not EPSILON in nonTermFirsts:
                return stringFirsts
        else:
            stringFirsts.add(string[i])
            return stringFirsts
    stringFirsts.add(EPSILON)
    return stringFirsts

def followsOfNonTerm(nonTerminal):
    '''
    Return the sets of follows for a non terminal
    '''
    # Return stored set of follows if its been calculated already
    if len(follows[nonTerminal]) != 0 and follows[nonTerminal] != {EOF}:
        return follows[nonTerminal]

    for production in productions:
        prodBody = body(production)
        addHeaderFollowsFlag = False
        for i in range(len(prodBody)):
            if prodBody[i] == nonTerminal:
                if i < len(prodBody) - 1:
                    betaFirsts = firstsOfString(prodBody[i + 1:])
                    follows[nonTerminal].update(betaFirsts)
                    follows[nonTerminal].discard(EPSILON)
                    if EPSILON in betaFirsts:
                        addHeaderFollowsFlag = True
                else:
                    addHeaderFollowsFlag = True
        
        if addHeaderFollowsFlag and header(production) != nonTerminal:
            headerFollows = followsOfNonTerm(header(production))
            follows[nonTerminal].update(headerFollows)

    return follows[nonTerminal]


n = int(input().strip())

productions = []
firsts = dict()
follows = dict()
nonTerminals = set()
startNonTerm = None

for i in range(n):
    line = input().strip()

    # Change epsilon representation
    lineButCooler = ""
    j = 0
    while j < len(line):
        if line[j] == '\'':
            lineButCooler += EPSILON
            j = j + 3
        else:
            lineButCooler += line[j]
            j = j + 1

    # Store each production as a list of tokens
    production = lineButCooler.split()
    productions.append(production)

    # Store all non-terminals
    nonTerminal = header(production)
    nonTerminals.add(nonTerminal)

    if i == 0:
        startNonTerm = nonTerminal

    # Initialize set of empty set of first and follows for each non-terminal
    firsts[nonTerminal] = set()
    follows[nonTerminal] = set()


# Get firsts of each non-terminal
for nonTerminal in nonTerminals:
    firstsOfNonTerm(nonTerminal)

# Get follows of each non-terminal
follows[startNonTerm].add(EOF)
for nonTerminal in nonTerminals:
    followsOfNonTerm(nonTerminal)

# Validate LL analizable

# Show sets
for nonTerminal in nonTerminals:
    print(nonTerminal + " => FIRST = {" + setToString(firsts[nonTerminal], ",") + "}, ", end="")
    print("FOLLOW = {" + setToString(follows[nonTerminal], ",") + "}")