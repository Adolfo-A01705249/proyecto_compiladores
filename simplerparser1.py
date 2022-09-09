# Prints a list of a grammar's terminals and non-terminals
# given an ENBF grammar

# usage: $python parser.py < <input file>

# Author: Adolfo Acosta Castro [A01705249]
# Date: 2022/09/09

def printSet(set):
    """
    Creates a string made of the elements of a set separated by commas
    Arguments:
        set: a python set
    Returns:
        The created string with the list of set elements
    """
    resultString = ""
    SEPARATOR = ", "
    for item in set:
        resultString += item + SEPARATOR
    return resultString[:-len(SEPARATOR)]

def parseLine(line, headerTokens, bodyTokens):
    """
    Takes the head and production tokens from one grammar production
    and adds them to their respective sets
    Arguments:
        line: a string representing a grammar production
        headerTokens: a set for the tokens on production headers
        bodyTokens: a set for the tokens on production bodies
    """
    tokens = line.split()
    headerTokens.add(tokens[0])
    for i in range(2, len(tokens)):
        if tokens[i] == '\'':
            continue
        bodyTokens.add(tokens[i])


n = int(input().strip())

headerTokens = set()
bodyTokens = set()

# Process each production one by one
for i in range(n):
    line = input().strip()
    parseLine(line, headerTokens, bodyTokens)

# If a token appears on a production header then it is not terminal
# even if it appears on a production body
for token in headerTokens:
    bodyTokens.discard(token)

print(f"Terminal: {printSet(bodyTokens)}")
print(f"Non terminal: {printSet(headerTokens)}")