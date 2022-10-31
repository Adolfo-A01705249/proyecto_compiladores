# Generates a SLR analysis table and uses it to try and parse strings

# usage: $python SLR.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/10/30

import sys

EPSILON = '\' \''
EOF ='$'
DOT = "."
SHIFT = "S"
REDUCE = "R"
ACCEPT = "AC"
UNIQUE_TOKEN = "A01705249"
BODY_START_INDEX = 2
STYLESHEET = "styles.css"
ERROR = 0
MESSAGE = 1

class Queue:
    """
    A simple FIFO queue data structure built
    space-inefficiently on top of a list
    """
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
    '''
    A grammar production with a marker (dot) that
    can be moved between the body's symbols
    '''
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
        '''
        Returns true if the dot has advanced to 
        the end of the production's body
        '''
        if self.production[BODY_START_INDEX] == EPSILON:
            return True
        return (not self.dotIndex < len(self.production))

    def getProduction(self):
        '''
        Returns the objects production
        '''
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

def bodyLength(production):
    '''
    Returns the number of tokens in the body of a production 
    or 0 if the production only derives in epsilon.
    Arguments:
        production: a well-formed list of tokens
    Returns:
        The length as specified above
    '''
    if production[BODY_START_INDEX] == EPSILON:
        return 0
    return (len(production) - 2)

def top(stack, name):
    '''
    Returns the top-most value of a stack. If the stack is empty,
    it sets the parsing error data values.
    Arguments:
        stack: a python list
        name: a string representing a descriptive name for the stack
    Returns:
        The element on the last position of the list
    '''
    if not len(stack) > 0:
        parsingErrorData[ERROR] = True
        parsingErrorData[MESSAGE] = "Error: tried to remove a token from the {name} but it was empty."

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

def retrieveFromDict(dictArray, index, key):
    if key in dictArray[index].keys():
        return dictArray[index][key]
    else:
        parsingErrorData[ERROR] = True
        parsingErrorData[MESSAGE] = f"Error: a required table value ({index}, \"{key}\"), doesn't exist."

def checkTokenInGrammar(token):
    '''
    Validates that a token from an input string
    is a terminal or the end of file token.
    In case of an error, uses global variables to indicate an
    error and a descriptive message.
    Arguments:
        token: the token to validate
    '''
    if token not in actionSymbols:
        parsingErrorData[ERROR] = True
        parsingErrorData[MESSAGE] = f"Error: input string has a symbol ({token}) that is not recognized by the grammar."

def getSlrTableHeader(terminalsArray, nonTerminalsArray):
    '''
    Returns a string representing the header of the SLR table
    with HTML format
    Arguments:
        terminalsArray: a list of terminals for the actions section
        nonTerminals: a list of non-terminals for the goto section
    Returns:
        a string with HTML format
    '''
    headerTitles = f"\t<th> </th>\n"
    headerTitles += f"\t<th colspan = {len(terminalsArray)}> ACTIONS </th>\n"
    headerTitles += f"\t<th colspan = {len(nonTerminalsArray)}> GOTO </th>\n"
    headerTitles = "<tr>\n" + headerTitles + "</tr>\n"

    headerSymbols = f"\t<th> </th>\n"
    for symbol in terminalsArray + nonTerminalsArray:
        headerSymbols += f"\t<th> {symbol} </th>\n"
    headerSymbols = "<tr>\n" + headerSymbols + "</tr>"

    return (headerTitles + headerSymbols)

def getTableHeader(headers):
    '''
    Returns a string representing the header of a simple table
    with HTML format
    Arguments:
        headers: a list of strings for the header of each column
    Returns:
        a string with HTML format
    '''
    headerCells = ""
    for title in headers:
        headerCells += f"\t<th> {title} </th>\n"
    tableHeader = "<tr>\n" + headerCells + "</tr>\n"
    return tableHeader

def getTableRow(cellValues):
    '''
    Returns a string representing a row of the SLR table
    with HTML format
    Arguments:
        cellValues: a list of values for each cell
    Returns:
        a string with HTML format
    '''
    rowCells = ""
    for value in cellValues:
        rowCells += f"\t<td> {value} </td>\n"
    tableRow = "<tr>\n" + rowCells + "</tr>\n"
    return tableRow

def getTable(header, rows):
    '''
    Returns a string representing a full SLR table
    with HTML format
    Arguments:
        header: an HTML string representing a table header
        rows: a list of HTML string representing table rows
    Returns:
        a string with HTML format
    '''
    table = "<table>\n"
    table += header
    for row in rows:
        table += row
    table += "</table>\n"
    return table

def getHtmlDoc(bodyElements):
    '''
    Returns a string representing a full HTML document with content
    and link to a stylesheet
    Arguments:
        bodyElements: a list of HTML strings representing HTML elements
    Returns:
        a string with HTML format
    '''
    doc = "<!DOCTYPE html>\n"
    doc += "<html>\n"
    doc += "<head>\n"
    doc += f"\t<link rel=\'stylesheet\' href=\'{STYLESHEET}\'>\n"
    doc += "\t<title> SLR table </title>\n"
    doc += "</head>\n"
    doc += "<body>\n"
    for element in bodyElements:
        doc += f"{element}\n"
    doc += "</body>\n"
    doc += "</html>\n"
    return doc


#---------------------------------------------------------------
# Parse input into lists of tokens and lists of symbols
#---------------------------------------------------------------
productions = []
nonTerminals = set()
terminals = set()
startNonTerm = None

inputNumbers = input().strip().split()
numberOfProductions = int(inputNumbers[0])
numberOfStrings = int(inputNumbers[1])

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
            production = productionWithDot.getProduction()
            productionIndex = productions.index(production)
            
            if productionIndex == 0:
                insertIntoDict(itemActions[itemIndex], EOF, (ACCEPT, None))
            else:
                for follow in follows[header(production)]:
                    insertIntoDict(itemActions[itemIndex], follow, (REDUCE, productionIndex))
               

#---------------------------------------------------------------
# Build HTML SLR table
#---------------------------------------------------------------
nonTerminalsArray = []
for nonTerminal in nonTerminals:
    nonTerminalsArray.append(nonTerminal)
nonTerminalsArray.sort()

terminalsArray = []
for terminal in terminals:
    terminalsArray.append(terminal)
terminalsArray.sort()
terminalsArray.append(EOF)

slrTableRows = []

for itemIndex in range(len(itemKernels)):
    cellValues = [itemIndex]
    for terminal in terminalsArray:
        if terminal in itemActions[itemIndex].keys():
            actionType = itemActions[itemIndex][terminal][0]
            actionParameter = itemActions[itemIndex][terminal][1]
            if actionType == ACCEPT:
                actionParameter = ""
            cellValues.append(f"{actionType}{actionParameter}")
        else:
            cellValues.append("")

    for nonTerminal in nonTerminalsArray:
        if nonTerminal in itemTransitions[itemIndex].keys():
            destinationIndex = itemTransitions[itemIndex][nonTerminal]
            cellValues.append(destinationIndex)
        else:
            cellValues.append("")

    slrTableRows.append(getTableRow(cellValues))
        
slrTableHeader = getSlrTableHeader(terminalsArray, nonTerminalsArray)
slrTable = getTable(slrTableHeader, slrTableRows)



#---------------------------------------------------------------
# Parse strings with SLR table
#---------------------------------------------------------------

# Parse input strings into lists of tokens
rawStrings = []
strings = []
for i in range(numberOfStrings):
    line = input().strip()
    rawStrings.append(line)
    tokenList = line.split()
    tokenList.append(EOF)
    strings.append(tokenList)

# Parse each string with SLR table  
actionSymbols = terminals.union(EOF)
parsingErrorData = [None, None]

acceptTableRows = []
parseTables = []

for i in range(numberOfStrings):
    stack = [0]
    string = strings[i].copy()
    string.reverse()

    parsingErrorData = [False, ""]
    parsingResultMessage = None

    parseTableRows = []
    
    print(f"\nchecking string {rawStrings[i]}:")
    while True:
        parseCellValues = [" ".join(map(str, stack)), " ".join(map(str, reversed(string)))]

        itemIndex = top(stack, "stack")
        if parsingErrorData[ERROR]: break
        stringToken = top(string, "input string")
        if parsingErrorData[ERROR]: break
        checkTokenInGrammar(stringToken)
        if parsingErrorData[ERROR]: break

        action = retrieveFromDict(itemActions, itemIndex, stringToken)
        if parsingErrorData[ERROR]: break
        actionType = action[0]
        actionParameter = action[1]

        if actionType == SHIFT:
            parseCellValues.append(f"Shift {actionParameter}")

            stack.append(string.pop())
            stack.append(actionParameter)

        elif actionType == REDUCE:
            parseCellValues.append(f"Reduce {actionParameter}")
            parseTableRows.append(getTableRow(parseCellValues))

            tokensToRemove = 2 * bodyLength(productions[actionParameter])
            for j in range(tokensToRemove):
                top(stack, "stack")
                if parsingErrorData[ERROR]: break
                stack.pop()
            topIndex = top(stack, "stack")
            if parsingErrorData[ERROR]: break    
            productionHeader = header(productions[actionParameter])
            stack.append(productionHeader)
            
            # Goto continuation
            parseCellValues = [" ".join(map(str, stack)), " ".join(map(str, reversed(string)))]
            parseCellValues.append(f"Goto {destinationIndex}")

            destinationIndex = retrieveFromDict(itemTransitions, topIndex, productionHeader)
            if parsingErrorData[ERROR]: break
            stack.append(destinationIndex)

        elif actionType == ACCEPT:
            parsingResultMessage = "Accepted."

            parseCellValues.append("Accept")
            parseTableRows.append(getTableRow(parseCellValues))

            break
        
        parseTableRows.append(getTableRow(parseCellValues))

    if parsingErrorData[ERROR]:
        parsingResultMessage = f"Unaccepted. {parsingErrorData[MESSAGE]}"

        parseCellValues = [" ".join(map(str, stack)), " ".join(map(str, reversed(string)))]
        parseCellValues.append(parsingErrorData[MESSAGE])
        parseTableRows.append(getTableRow(parseCellValues))

    acceptTableRow = getTableRow([rawStrings[i], parsingResultMessage])
    acceptTableRows.append(acceptTableRow)

    parseTableHeader = getTableHeader(["Stack", "String", "Action to perform"])
    parseTable = getTable(parseTableHeader, parseTableRows)
    parseTables.append(parseTable)

acceptTableHeader = getTableHeader(["Input string", "Parse result"])
acceptTable = getTable(acceptTableHeader, acceptTableRows)

htmlDoc = getHtmlDoc([slrTable, acceptTable] + parseTables)
print(htmlDoc)

# Qs
# Do we need to validate overlap in table cell, how to handle when this happens
# How to process epsilon prods in SLR tree generation
# make retrieve from dict error more descriptive