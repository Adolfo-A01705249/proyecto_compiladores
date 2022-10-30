# Prints a list of a grammar's non-terminal's FIRSTS and FOLLOWS

# usage: $python parser.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/10/30

import sys

EPSILON = '\' \''
EOF ='$'
BODY_START_INDEX = 2
DOT = "."
SHIFT = "S"
REDUCE = "R"
ACCEPT = "AC"
UNIQUE_TOKEN = "A01705249"


class Queue:
    values = []
    frontIndex = 0

    def insert(self, value):
        self.values.append(value)   

    def remove(self):
        value = self.values[self.frontIndex]
        self.frontIndex += 1
        return value

    def empty(self):
        return (self.frontIndex == len(self.values))

class ProductionWithDot:
    production = None
    dotIndex = None # Index of symbol that is right after the dot

    def __init__(self, production, dotIntex = 2):
        self.production = production
        self.dotIndex = dotIntex

    def underlined(self):
        '''
        Returns the symbol after the dot or None 
        if dot is at the end of the production
        '''
        if not self.completed():
            return self.production[self.dotIndex]
        else:
            return None

    def advanceDot(self):
        '''
        Returns a copy of the object with the 
        dot one positiono ahead
        '''
        advancedProduction = ProductionWithDot(self.production, self.dotIndex + 1)
        return advancedProduction

    def completed(self):
        return (not self.dotIndex < len(self.production))

    def production(self):
        return self.production

    def __eq__(self, other):
        if isinstance(other, ProductionWithDot):
            return (self.production == other.production and
                    self.dotIndex == other.dotIndex)
        else:
            return False

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __hash__(self):
        productionWithDotTuple = (tuple(self.production), self.dotIndex)
        return hash(productionWithDotTuple)

    def __str__(self):
        separator = " "
        stringRep = separator.join(self.production[:self.dotIndex])
        stringRep += separator + DOT + separator
        if not self.completed():
            stringRep += separator.join(self.production[self.dotIndex:])

        return stringRep


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

def top(stack):
    '''
    Returns the top-most value of a stack
    Arguments:
        stack: a python list
    Returns:
        The element on the last position of the list
    '''
    if not len(stack) > 0:
        sys.exit("Error: no more tokens inside of stack.")

    return stack[-1]

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
    if visited[nonTerminal]:
        return
    visited[nonTerminal] = True
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
    if visited[nonTerminal]:
        return
    visited[nonTerminal] = True
    follows[nonTerminal].update(seeds)
    for node in reverseFollowsDependencies[nonTerminal]:
        propagateFollowsSeeds(node, seeds)

def insertIntoDict(aDict, key, value):
    if not key in aDict.keys():
        aDict[key] = value
    else:
        sys.exit(f"Error: overlap in SLR table cell.")

def retrieveFromDict(aDict, key):
    if key in aDict.keys():
        return aDict[key]
    else:
        sys.exit(f"Error: required action doesn't exist.")


#---------------------------------------------------------------
# Parse input into lists of tokens and lists of symbols
#---------------------------------------------------------------
productions = []
nonTerminals = set()
terminals = set()
startNonTerm = None

numberOfProductions = int(input().strip())
numberOfStrings = int(input().strip())

for i in range(numberOfProductions):
    line = input().strip()

    # Store each production as a list of tokens
    production = line.split()
    if production[2] == '\'' and production[3] == '\'':
        production.pop()
        production.pop()
        production.append(EPSILON)
    productions.append(production)

    # Store all non-terminals
    nonTerminal = header(production)
    nonTerminals.add(nonTerminal)

startNonTerm = header(productions[0])

# Get set of terminals and symbols
for production in productions:
    for token in body(production):
        if token not in nonTerminals and token != EPSILON:
            terminals.add(token)
symbols = terminals.union(nonTerminals)



#---------------------------------------------------------------
# Calculate first and follows sets
#---------------------------------------------------------------
productionsForMarking = []
firsts = dict()
firstsSeeds = dict()
reverseFirstsDependencies = dict()

follows = dict()
followsSeeds = dict()
reverseFollowsDependencies = dict()

visited = dict()

# Initialize sets used for firsts and follows for each non-terminal
for nonTerminal in nonTerminals:
    firsts[nonTerminal] = set()
    firstsSeeds[nonTerminal] = set()
    reverseFirstsDependencies[nonTerminal] = set()

    follows[nonTerminal] = set()
    followsSeeds[nonTerminal] = set()
    reverseFollowsDependencies[nonTerminal] = set()

    visited[nonTerminal] = set()

# Find which non-terminals have epsilon in their firsts
for production in productions:
    productionsForMarking.append(production.copy())

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
        for node in visited:
            visited[node] = False
        propagateFirstsSeeds(nonTerminal, firstsSeeds[nonTerminal])

# Build follows dependency graph and find follows seeds
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
        for node in visited:
            visited[node] = False
        propagateFollowsSeeds(nonTerminal, followsSeeds[nonTerminal])



#---------------------------------------------------------------
# Generate item tree and SLR table
#---------------------------------------------------------------

# Make dictionary of productions organized by non-terminal 
productionsOf = dict()
for nonTerminal in nonTerminals:
    productionsOf[nonTerminal] = []

for production in productions:
    nonTerminal = header(production)
    productionsOf[nonTerminal].append(production)

# Create new production that recognizes the grammar
artificialProduction = [UNIQUE_TOKEN, "->", startNonTerm]
productions.insert(0, artificialProduction)

# Insert new production into kernel of item 0
itemKernels = []
itemProductions = []
itemTransitions = []
itemQueue = Queue()

initialKernel = {ProductionWithDot(artificialProduction)}

itemKernels.append(initialKernel)
newItemIndex = len(itemKernels) - 1
itemQueue.insert(newItemIndex)

# Build item tree, breath first traversal
while not itemQueue.empty():
    itemIndex = itemQueue.remove()

    print(f"\n\nItem #{itemIndex}")
    # Duplicate productions from kernel into list for convenience
    itemProductions.append([])
    print("-------------------------------")
    print("Kernel: ")
    for productionWithDot in itemKernels[itemIndex]:
        print(productionWithDot)
        itemProductions[itemIndex].append(productionWithDot)

    # Add productions of non-terminals with dot before them to item
    print("-------------------------------")
    print("Whole list: ")
    i = 0
    while i < len(itemProductions[itemIndex]):
        productionWithDot = itemProductions[itemIndex][i]
        print(productionWithDot)
        underlinedSymbol = productionWithDot.underlined()
        if underlinedSymbol in nonTerminals:
            for production in productionsOf[underlinedSymbol]:
                newProductionWithDot = ProductionWithDot(production)
                if newProductionWithDot not in itemProductions[itemIndex]:
                    itemProductions[itemIndex].append(newProductionWithDot)
        i += 1  

    # Derive for each terminal and non-terminal
    print("-------------------------------")
    print("Transitions: ")
    itemTransitions.append(dict())

    for symbol in symbols:
        derivedKernel = set()
        for productionWithDot in itemProductions[itemIndex]:
            if productionWithDot.underlined() == symbol:
                advancedProduction = productionWithDot.advanceDot()
                derivedKernel.add(advancedProduction)

        if len(derivedKernel) == 0:
            continue

        destinationIndex = -1
        if not derivedKernel in itemKernels:
            # Create brand new item
            itemKernels.append(derivedKernel)
            newItemIndex = len(itemKernels) - 1
            itemQueue.insert(newItemIndex)
            destinationIndex = newItemIndex
        else:
            oldItemIndex = itemKernels.index(derivedKernel)
            destinationIndex = oldItemIndex

        # Store transitions between items
        itemTransitions[itemIndex][symbol] = destinationIndex
        print(f"Under {symbol} moves to {destinationIndex}")
      
# Store shift actions
itemActions = []
for itemIndex in range(len(itemKernels)):
    itemActions.append(dict())
    for symbol in itemTransitions[itemIndex].keys():
        if symbol in terminals:
            terminal = symbol
            destinationIndex = itemTransitions[itemIndex][terminal]
            itemActions[itemIndex][terminal] = (SHIFT, destinationIndex)

# Store reduce and accepted actions
for itemIndex in range(len(itemKernels)):
    for productionWithDot in itemProductions[itemIndex]:
        if productionWithDot.completed():
            production = productionWithDot.production()
            productionIndex = productions.index(production)
            
            if productionIndex == 0:
                insertIntoDict(itemActions[itemIndex], EOF, (ACCEPT, None))
            else:
                for follow in follows[header(production)]:
                    insertIntoDict(itemActions[itemIndex], follow, (REDUCE, productionIndex))
               


#---------------------------------------------------------------
# Parse strings with SLR table
#---------------------------------------------------------------

# Parse input strings into lists of tokens
strings = []
for i in range(numberOfStrings):
    string = input().strip()
    tokenList = string.split()
    tokenList.append(EOF)
    strings.append(tokenList)

# Parse each string with SLR table  
'''stack = [0]
for i in range(numberOfStrings):
    string = strings[i].reverse()
    j = 0
    while True:
        itemIndex = top(stack)
        stringToken = top(string)
        action = retrieveFromDict(itemActions[itemIndex], stringToken)

        actionType = itemActions[itemIndex][stringToken][0]
        actionParameter = itemActions[itemIndex][stringToken][1]

        if action == SHIFT:
            
        elif action == REDUCE:
            
        elif action == ACCEPT:
            print(f"{strings[i]} accepted")
            break
            '''
            

# Qs
# Do we need to validate overlap in table cell