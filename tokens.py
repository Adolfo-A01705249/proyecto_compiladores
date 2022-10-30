# Generates a text file with a list of grammar terminals and non-terminals 
# given an ENBF grammar

# usage: $python <input file route> <output file route>

# Author: Adolfo Acosta Castro
# Date 2022/09/02

import sys

def reachedEnd(line, i):
    return (i >= len(line))

def isBlank(char):
    return (char in {" ", "\t"})

def skipBlanks(line, i):
    while not reachedEnd(line, i) and isBlank(line[i]):
        i += 1
    return i

def nextCharIs(line, i, char):
    return (not reachedEnd(line, i+1) and line[i+1] == char)

def addToken(tokenList, token):
    if not token in tokenList:
        tokenList.append(token)

def parseLine(line, headerTokens, productionTokens):
    i = 0
    inHeader = True
    while not reachedEnd(line, i):
        i = skipBlanks(line, i)
        if reachedEnd(line, i): break

        # ->
        if line[i] == '-':
            if(nextCharIs(line, i, '>')):
                inHeader = False
                i += 2
                continue

        # ' '
        elif line[i] == '\'':
            while not reachedEnd(line, i) and line[i] != '\'':
                i += 1
            i += 1

        # Every other token
        else:
            token = ""
            while not reachedEnd(line, i) and not isBlank(line[i]):
                token += line[i]
                i += 1

            if inHeader:
                addToken(headerTokens, token)
            else:
                addToken(productionTokens, token)
            
def printSet(set):
    resultString = ""
    SEPARATOR = ", "
    for item in set:
        resultString += item + SEPARATOR
    return resultString[:-len(SEPARATOR)]

inputFileName = sys.argv[1]
inputFile = open(inputFileName, 'r')
n = int(inputFile.readline().strip())

headerTokens = []
productionTokens = []

for i in range(n):
    line = inputFile.readline().strip()
    parseLine(line, headerTokens, productionTokens)
    
inputFile.close()

for token in headerTokens:
    if token in productionTokens:
        productionTokens.remove(token)

# Print results to console
print(f"Terminal: {printSet(productionTokens)}")
print(f"Non terminal: {printSet(headerTokens)}")

# Print results to file
outputFileName = sys.argv[2]
outputFile = open(outputFileName, 'w')
print(f"Terminal: {printSet(productionTokens)}", file = outputFile)
print(f"Non terminal: {printSet(headerTokens)}", file = outputFile)
outputFile.close()