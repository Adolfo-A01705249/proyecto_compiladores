# Prints a list of a grammar's non-terminal's FIRSTS and FOLLOWS

# usage: $python parser.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/10/05

import sys

EPSILON = "\'e\'"
EPSILON_FOR_PRINT = "\' \'"
EOF = "$"
DOT = "."
SHIFT = "S"
REDUCE = "R"
ACCEPT = "AC"

DEBUG_PRINT = True

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
        resultString += (EPSILON_FOR_PRINT if item == EPSILON else item) + separator
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

def firstsOfNonTerm(nonTerminal):
    '''
    Calculates and stores the set of firsts of a non terminal
    Arguments:
        nonTerminal: a grammar's non terminal symbol as a string
    Returns:
        The set of firsts for the non terminal
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
    Arguments:
        string: a python list of grammar symbols
    Returns:
        The set of firsts for the sequence of symbols
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
    Calculates and stores the sets of follows for a non terminal
    Arguments:
        nonTerminal: a grammar's non terminal symbol as a string
    Returns:
        The set of follows for the non terminal
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

def insertIntoDict(aDict, key, value):
    if not key in aDict.keys():
        aDict[key] = value
    else:
        sys.exit(f"Overlap in table cell")

# Parse input productions into lists of tokens
productions = []
n = int(input().strip())

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


# Get sets of terminals and non-terminals
terminals = set()
nonTerminals = set()

for production in productions:
    nonTerminal = header(production)
    nonTerminals.add(nonTerminal)

for production in productions:
    for token in body(production):
        if token not in nonTerminals:
            terminals.add(token)

symbols = terminals.union(nonTerminals)


# Make dictionary of productions organized by non-terminal 
productionsOf = dict()
for nonTerminal in nonTerminals:
    productionsOf[nonTerminal] = []

for production in productions:
    nonTerminal = header(production)
    productionsOf[nonTerminal].append(production)
    

# Create new production that recognizes the grammar
startNonTerm = header(productions[0])
artificialProduction = ["A01705249", "->", startNonTerm]
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

# Build item tree, breath first traversal just cause
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
            # Create brand new item and store connection to it
            itemKernels.append(derivedKernel)
            newItemIndex = len(itemKernels) - 1
            itemQueue.insert(newItemIndex)
            destinationIndex = newItemIndex
            
        else:
            oldItemIndex = itemKernels.index(derivedKernel)
            destinationIndex = oldItemIndex

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

# Get firsts and follows of each non-terminal
'''firsts = dict()
follows = dict()

for nonTerminal in nonTerminals:
    firsts[nonTerminal] = set()
    follows[nonTerminal] = set()

for nonTerminal in nonTerminals:
    firstsOfNonTerm(nonTerminal)

follows[startNonTerm].add(EOF)
for nonTerminal in nonTerminals:
    followsOfNonTerm(nonTerminal)'''

# Store reduce and accepted actions
for itemIndex in range(len(itemKernels)):
    for productionWithDot in itemKernels[itemIndex]:
        if productionWithDot.completed():
            production = productionWithDot.production()
            productionIndex = productions.index(production)
            
            if productionIndex == 0:
                insertIntoDict(itemActions[itemIndex], EOF, (ACCEPT, None))

            else:
                for follow in follows[header(production)]:
                    insertIntoDict(itemActions[itemIndex], follow, (REDUCE, productionIndex))
                
# Parse string with table
