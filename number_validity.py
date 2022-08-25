import re

def isValid(s):

    # 1) Begins with 0 or 91
    # 2) Then contains 7 or 8 or 9.
    # 3) Then contains 9 digits
    Pattern = re.compile("[6-9][0-9]{9}")
    return Pattern.match(s)

## Driver Code