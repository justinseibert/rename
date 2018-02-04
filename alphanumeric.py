import string
import sys

def condense(n):
    alphanumeric = string.digits + string.ascii_letters
    base = len(alphanumeric)
    result = ''
    n = n+base
    while n > -1:
        i = n%base
        result = alphanumeric[i] + result

        n = n/base-1

    return result
