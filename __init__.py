# -*- coding: utf-8 -*-
# Official Docs: https://github.com/mz3r0/small-bang/blob/main/Python%20Projects/TXTBuilder/README.md
import re
import random

MAX_LINES = 1000000
TXTB_EMPTY_STRING = ""
CALL_FUNCTIONS_DEFAULT = True
NR_OF_RECURSIONS_DEFAULT = -1
REMOVE_DATA_TRAILING_NEWINES = False
FILE_CONFIG = "builder.config"
FILE_ENCODING = "utf-8-sig"
FLAG_SET_ITEMS_RANDOMIZATION = True

class TXTB:
    def __init__(self, inputName, settingsName=FILE_CONFIG):
        self.data = list()
        self.dataLen = 0
        self.tokens = list()
        self.sets = {} # Dictionary

        self.charSheet = {
            's': ' ',  # Space
            't': '\t',  # Tab
            'n': '\n'  # Newline
        }

        self.methods = {
            'strip': TXTB_strip,
            'rpl_newline': TXTB_rpl_newline,
            'caps': TXTB_to_caps,
            'lower': TXTB_to_lower,
            'linktitle': TXTB_precede_minus,
            'title': TXTB_str_title,
            'gametag': TXTB_audiosurf_gamemode
        }

        with open(settingsName, 'r', encoding=FILE_ENCODING) as fin:
            GS = fin.readline()
            LS = fin.readline()

        with open(inputName, 'r', encoding=FILE_ENCODING) as fin:
            allLines = fin.readlines(MAX_LINES)

        self.filterComments(allLines, LS)
        oneText = ''.join(allLines)  # join before splitting again on separators

        sectionData, sectionSyntax = oneText.split(GS, 1)  # maxsplit feels redudant but I'll leave it
        self.data = list(sectionData.split(LS))
        self.dataLen = len(self.data)

        # Handle trailing newlines in every element
        if REMOVE_DATA_TRAILING_NEWINES:
            for i in range(self.dataLen):
                self.data[i] = self.data[i].strip()

        # Build self.setsByIndex & self.setsByName
        # self.data is NOT modified during this process
        for i in range(self.dataLen):
            element = self.data[i].strip()
            line1, line2 = element.split('\n')

            if line1[0] == "#" and len(line1) > 2 and line1.count("#") == 2:
                _, nameOfSet, _ = line1.split("#")

                # We expect line2 to be in CSV format
                # Create the set
                theSet = { x.strip() for x in line2.split(',') }

                # Add the set
                # Note: Every set has a name and an index
                self.sets[(str(i),nameOfSet)] = theSet

        # Tokenize the syntax (newlines are purged)
        self.tokenize(sectionSyntax)

    def filterComments(self, lines, LS):
        for index, line in enumerate(lines):
            matchComment = re.search("^" + LS + " ", line)
            matchDefault = True if line == LS + '\n' else False
            if matchComment or matchDefault:
                lines[index] = LS

    def tokenize(self, sectionSyntax):
        """Prepares self.tokens"""
        for chunk in sectionSyntax.split('\n'):  # residual empty strings are created: ''
            for token in chunk.split():  # ''.split() == [] is True
                self.tokens.append(token)  # this doesn't run if chunk.split() == []

    def generateTxt(self, outputName):
        userPromptFlag = False
        aiPromptFlag = False
        methodsToken = ""   # Redundant assignment
        userPrompt = "" # Unsure if redundant assignment
        aiPrompt = []   # Unsure if redundant assignment

        with open(outputName, 'w', encoding=FILE_ENCODING) as fout:  # overwrite if exists
            for token in self.tokens:
                
                # Case User Prompt
                if token[0] == "~":
                    userPromptFlag = not userPromptFlag     # Switch flag
                    
                    if userPromptFlag:  # Prompt beginning
                        methodsToken = token
                    else:  # Prompt end - ask user
                        if len(methodsToken.split('.')) > 1:
                            userPrompt = self.functionWrap(userPrompt, methodsToken)
                        userInput = input(userPrompt + ': ')
                        fout.write(self.functionWrap(userInput, token))
                        userPrompt = ""  # Unsure if redundant assignment

                    continue  # to the next element

                # Case Generate AI Prompt
                if token[0] == "@":
                    aiPromptFlag = not aiPromptFlag     # Switch flag

                    if not userPromptFlag:  # Prompt end
                        for line in self.aiPrompt(aiPrompt):
                            if line:
                                fout.write(line+'\n')
                        aiPrompt = []   # Unsure if redundant assignment

                    continue  # to the next element

                if userPromptFlag:
                    userPrompt += ' ' + self.tokenInterpreter(token)
                elif aiPromptFlag:
                    aiPrompt.append(token)
                else:
                    fout.write(self.tokenInterpreter(token))

    def functionWrap(self, targetText, methodsToken):
        # Modify target based on element's function calls
        functionNames = methodsToken.split('.')[1:]     # [] is returned if length is 1
        if not functionNames:                           # not [] is True therefore no function wrap
            return targetText
        result = self.callFunctionsOn(targetText, functionNames)
        return result

    def callFunctionsOn(self, targetText, functionNames):
        """Reusable and minimal"""
        # args = {'data': targetText}   # **dict(args) is also an option
        for f in functionNames:     # Does f exist in the dict keys?
            if f in self.methods:
                targetText = self.methods[f](targetText)
            else:
                print("Call not found: " + f)  # TODO THROW EXCEPTION
        return targetText

    def tokenInterpreter(self, token, callFunctions=CALL_FUNCTIONS_DEFAULT):
        """
        Can also interpret tokens such as: arbitraryText.caps and 3.strip.
        The token ~ never makes it here.
        CALL_FUNCTIONS_DEFAULT is True.
        """
        baseToken = token.split('.')[0]

        if baseToken in self.charSheet:             # Character Sheet token?
            t = self.charSheet[baseToken]

        elif baseToken.isnumeric():                 # Index token?
            if int(baseToken) < self.dataLen:
                t = self.data[int(baseToken)]
            else:
                print("OUT OF BOUNDS IN DATA LIST")
                t = ""  # TODO THROW EXCEPTION

        else:
            t = baseToken                           # None of the above, no parsing so far

        if not callFunctions:
            return t
        return self.functionWrap(t, token)  # t is always assignmed

    def aiPrompt(self, tokens):
        """
        Tokens are all treated as text constants.
        """
        setRefs = [] # list of tuples

        # Create the prompt template with placeholders
        # We join now so we can replace substrings later
        generatedPrompts = [' '.join(tokens)]

        setKeysSorted = list(self.sets.keys())     # Form: (str,str)
        setKeysSorted.sort()
        setKeyNumeric = {x[0]:x for x in setKeysSorted}
        setKeyName = {x[1]:x for x in setKeysSorted}

        for t in tokens:
            if t[0] == "#" and len(t) > 2 and t.count("#") == 2:
                # Splitting will always yield a list of 3 items
                # The first item will be the empty string
                # tokenModifiers could be empty
                _, nameOfSet, tokenModifiers = t.split("#")

                # Ensure that the starting template only contains placeholders
                # "Bla #hashtags#.20 bla" -> "bla #hashtags# bla"
                if tokenModifiers:
                    generatedPrompts[0] = generatedPrompts[0].replace(t,"#"+nameOfSet+"#")

                if nameOfSet in setKeyNumeric:
                    tpl = (nameOfSet, self.sets[setKeyNumeric[nameOfSet]], tokenModifiers)
                    setRefs.append(tpl)
                elif nameOfSet in setKeyName:
                    tpl = (nameOfSet, self.sets[setKeyName[nameOfSet]], tokenModifiers)
                    setRefs.append(tpl)

        for ref in setRefs:
            temporaryPrompts = list(generatedPrompts)
            generatedPrompts.clear()

            nameOfSet, theSet, tokenModifiers = ref  # Unpack Tuple
            setLength = len(theSet)

            # Case 1 Token modifiers exist
            if tokenModifiers:

                # Note: tokenModiers always begins with a dot (.)
                tokenModifiers = tokenModifiers.split('.')
                tokenModifiers.sort()
                tokenModifiers = tokenModifiers[1:]
                modifierOne = tokenModifiers[0]

                # Case 1.1 Retrieve x number of set elements and insert them as one substring
                if modifierOne.isnumeric():
                    elementsToRetrieve = int(modifierOne)

                    # Edge cases
                    if elementsToRetrieve < 1:
                        print("modifierOne can't be < 1")   # TODO Handle exception
                    elif elementsToRetrieve > setLength:
                        print("asked for too many elements! " + modifierOne)
                        elementsToRetrieve = setLength

                    for promptTemplate in temporaryPrompts:
                        replacement = self.replacementFromSet(theSet, elementsToRetrieve, tokenModifiers)
                        # Insert it. For loop works in the case of using this with combinations
                        generatedPrompts.append(promptTemplate.replace("#"+nameOfSet+"#",replacement))
                
                # Case 1.2 Create combinations after applying modifiers
                else:
                    for promptTemplate in temporaryPrompts:
                        for elem in theSet:
                            modifiedElem = self.callFunctionsOn(elem,tokenModifiers)
                            generatedPrompts.append(promptTemplate.replace("#"+nameOfSet+"#",modifiedElem))

            # Step 2 - Create combinations
            else:
                for promptTemplate in temporaryPrompts:
                    for elem in theSet:
                        generatedPrompts.append(promptTemplate.replace("#"+nameOfSet+"#",elem))

        return generatedPrompts

    def replacementFromSet(self, theSet, nrOfElems, tokenModifiers):
        # We will randomly get items from the set, so a copy is needed
        setCopy = theSet.copy()

        # Sets are unordered, so pop() will remove & return an arbitrary element
        # However, the randomness applies per different runs of the script!
        if FLAG_SET_ITEMS_RANDOMIZATION:
            theSetInListForm = list(theSet)
            randomIndices = set()

            while len(randomIndices) != nrOfElems:
                randomIndices.add(random.randint(0, len(theSet)-1))

            setElements = [theSetInListForm[i] for i in randomIndices]
        else:
            setElements = [setCopy.pop() for i in range(nrOfElems)]

        # Call additional functions based on modifiers
        for i in range(nrOfElems):
            setElements[i] = self.callFunctionsOn(setElements[i],tokenModifiers[1:])

        # Create one big substring
        return ' '.join(setElements)


    def generateRR(self, outputName, recursions=NR_OF_RECURSIONS_DEFAULT):
        """
        Generates the output which is reused as input.
        Keeps track of statistics.
        """
        for i, dataElement in enumerate(self.data):
            self.data[i] = dataElement.strip()   # TODO Turn this into a lambda

        while recursions == -1:
            self.generateTxtMinimal(outputName)     # TODO Save the output in a statistics file
            userContinue = input("+1 Recursion? (y/n): ")
            if userContinue.lower() == 'y':
                continue
            else:
                return

        while recursions > 0:
            self.generateTxtMinimal(outputName)     # TODO Save the output in a statistics file
            recursions = recursions - 1

        return

    def generateTxtMinimal(self, outputName):
        with open(outputName, 'w', encoding=FILE_ENCODING) as fout:
            fout.write(' ')
            for token in self.tokens:
                interpretedToken = self.tokenInterpreter(token, False)
                # print('\nInt:' + interpretedToken, end="")
                fout.write(interpretedToken + ' ')

        self.tokens = list()    # Empty the tokens

        # Read the output back in
        with open(outputName, 'r', encoding=FILE_ENCODING) as fin:
            allLines = fin.readlines(MAX_LINES)

        # Tokenize anew
        self.tokenize(''.join(allLines))


# TXTB FUNCTIONS USED IN THE METHODS DICTIONARY


def TXTB_strip(data=TXTB_EMPTY_STRING):
    return data.strip()


def TXTB_to_caps(data=TXTB_EMPTY_STRING):
    return data.upper()


def TXTB_to_lower(data=TXTB_EMPTY_STRING):
    return data.lower()


def TXTB_precede_minus(data=TXTB_EMPTY_STRING):
    return "- " + data.title()


def TXTB_audiosurf_gamemode(data=TXTB_EMPTY_STRING):
    if data == "none" or data == TXTB_EMPTY_STRING:
        return "None"
    result = ""
    tmp = data.split()
    if len(tmp) > 1:
        for part in tmp:
            result += "[as-" + part + "] "
        result = result.strip()
    else:
        result = "[as-" + data + "]"
    return result


def TXTB_rpl_newline(data=""):
    return data.replace("\n ", "\n")


def TXTB_str_title(data=""):
    return data.title()
