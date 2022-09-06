# Generates a text file with a list of grammar terminals and non-terminals 
# given an ENBF grammar

# usage: $python coolerparser1.py <input file route>

# Author: Adolfo Acosta Castro
# Date 2022/09/06

import sys

def printSet(set):
    resultString = ""
    SEPARATOR = ", "
    for item in set:
        resultString += item + SEPARATOR
    return resultString[:-len(SEPARATOR)]

def parseLine(line, headerTokens, productionTokens):
    tokens = line.split()
    headerTokens.add(tokens[0])
    for i in range(2, len(tokens)):
        if tokens[i] == '\'':
            continue
        productionTokens.add(tokens[i])

inputFileName = sys.argv[1]
inputFile = open(inputFileName, 'r')
n = int(inputFile.readline().strip())

headerTokens = set()
productionTokens = set()

for i in range(n):
    line = inputFile.readline().strip()
    parseLine(line, headerTokens, productionTokens)
inputFile.close()

for token in headerTokens:
    productionTokens.discard(token)

# Print results to console
print(f"Terminal: {printSet(productionTokens)}")
print(f"Non terminal: {printSet(headerTokens)}")
