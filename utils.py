## Info: https://github.com/Myvh/Discord-long-text-splitter/blob/main/Discord_long_text_splitter.py

# Made by Myvh on 2023 June.

# This little program splits the given text into chunks at most `maxLength` long, with the added condition that the splitting points have to be single newlines (newlines that are not next to another newline).
# This is because Discord trims leading and trailing newlines from messages, so splitting at a multiple newline makes it a single newline when sent.

## Text splitting

def rightTrim(text, toBeTrimmed):
    while text.endswith(toBeTrimmed):
        text = text[:-len(toBeTrimmed)]
    return text

def splittingIndex(text, maxLength, newline):
    if len(text) <= maxLength:
        return(len(text))
    remainingText = text[:maxLength+2*len(newline)]
    while True:
        possibleIndex = remainingText.rindex(newline)
        remainingText = remainingText[:possibleIndex]
        if remainingText.endswith(newline):
            remainingText = rightTrim(remainingText, newline)
        elif possibleIndex <= maxLength:
            return possibleIndex

def split(text, maxLength, newline):
    splittedText = []
    while text != "":
        currentSplittingIndex = splittingIndex(text, maxLength, newline)
        splittedText.append(text[:currentSplittingIndex])
        text = text[currentSplittingIndex+len(newline):]
    return splittedText