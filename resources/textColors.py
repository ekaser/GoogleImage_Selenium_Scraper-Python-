class textColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDCHAR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def greenText(input) :
    return textColors.GREEN + str(input) + textColors.ENDCHAR
def blueText(input):
    return textColors.BLUE + str(input) + textColors.ENDCHAR
def redText(input):
    return textColors.RED + str(input) + textColors.ENDCHAR
def headerText(input) :
    return textColors.HEADER + str(input) + textColors.ENDCHAR