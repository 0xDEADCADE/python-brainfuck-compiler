#!/bin/env python3
# Brainfuck compiler to python3 written by 0xDEADCADE
# Cell Size: 32 bits, no wrap
# Array Size: 30000 cells, Undefined OOB Behavior
import sys

Memdump = False

# If no file, or too many arguments are supplied.
if len(sys.argv) != 2:
    print("Incorrect usage!")
    print(f"Usage: {sys.argv[0]} [brainfuck file]")
    sys.exit(1)

# Open the file and read it's contents
with open(sys.argv[1], "r") as f:
    BFCode = f.read()

# Minimize the brainfuck code, as to not create errors later.
BFCodeMin = ""
for char in BFCode:
    if char in ".,+-<>[]":
        BFCodeMin += char

# Define snippets of code
# Either single or multi character.
# Can be adjusted for individual programs for better optimization.
BFCodeSnippets = {
    "[]": "pass",
    "[-]": "Cells[Pointer] = 0",
    "+": "Cells[Pointer] += 1",
    "-": "Cells[Pointer] -= 1",
    "[": "while Cells[Pointer] > 0:",
    ">": "Pointer += 1",
    "<": "Pointer -= 1",
    ".": "print(chr(Cells[Pointer]), end='')",
    ",": "Cells[Pointer] = ord(input()[0])"
}

# These can not be adjusted, they are for multiple repeating characters.
# Example: "++++" becomes "Cells[Pointer] += 4"
SameCharSnippets = {
    "+": "Cells[Pointer] += ",
    "-": "Cells[Pointer] -= ",
    ">": "Pointer += ",
    "<": "Pointer -= "
}

# Calculate the longest snippet length
# This is used for multi character bf code optimization
LongestSnippetLength = 0
for CodeSnippet in BFCodeSnippets:
    if len(CodeSnippet) > LongestSnippetLength:
        LongestSnippetLength = len(CodeSnippet)

# Initialize starting variables
PyCode = """Cells = [0 for x in range(30000)]
Pointer = 0
"""
IndentCount = 0
tickpos = 0
# Range from 0-LongestSnippetLength, but reversed
LongestSnippetLengthRange = list(range(LongestSnippetLength))
LongestSnippetLengthRange.reverse()

# While it's not at the end of the code
while tickpos < len(BFCodeMin):
    # The character in this position is equal to itself,
    # So we start with SameCharCount being 1
    SameCharCount = 1
    try:
        # While the characters after the current tickpos character are the same
        while BFCodeMin[tickpos] == BFCodeMin[tickpos + SameCharCount]:
            SameCharCount += 1
        
        # If the current character is repeated and is +, -, <, or >
        if SameCharCount > 1 and BFCodeMin[tickpos] in "+-<>":
            # Add the SameCharSnippets[character],
            # plus the amount of times the character repeats
            Indent = "    " * IndentCount
            PyCode += Indent
            PyCode += SameCharSnippets[BFCodeMin[tickpos]] + str(SameCharCount)
            tickpos += SameCharCount
            PyCode += "\n"
            # Continue to not cause logic errors after this.
            continue
    except IndexError:
        # Pass this, as at the end of the file we get one for some reason.
        pass
    # For every possibility check if it's in the code snippets
    for i in LongestSnippetLengthRange:
        char = BFCodeMin[tickpos:tickpos+i+1]
        if char in BFCodeSnippets.keys():
            Indent = "    " * IndentCount
            PyCode += Indent
            PyCode += BFCodeSnippets[char].replace("INDENT", Indent)
            tickpos += i + 1
            PyCode += "\n"
        # If indenting is required, add some
        if char == "[":
            IndentCount += 1
        elif char == "]":
            IndentCount -= 1
            tickpos += 1

if Memdump:
    PyCode += f"""
MDumpArr = []
TmpArray = []
for item in Cells:
    if len(TmpArray) == 8:
        MDumpArr.append(TmpArray)
        TmpArray = []
    TmpArray.append(item)

while all(n == 0 for n in MDumpArr[-1]):
    del MDumpArr[-1]

for item in MDumpArr:
    for val in item:
        print(str(val) + " ", end="")
    print("")
"""

# Open another file and write the compiled code to it
with open("CompiledBrainfuck.py", "w+") as f:
    f.write(PyCode)

# Execute the compiled code
exec(PyCode)
