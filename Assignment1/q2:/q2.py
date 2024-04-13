import sys

# Global variables
ALPHABET_SIZE = 26
UNICODE_A = 97

def Zalg(string: str):
    n = len(string)
    zVal = [0] * n

    # initialise left and right (z box) and k
    l = 0
    r = 0
    k = 0

    # iterate through the string
    for i in range(1, n):
        if i > r: # nothing has been matched yet
            # making z box the current character at i
            l = i 
            r = i

            # expanding the z box by increasing r for each matched character
            while r < n and string[r] == string[r-l]:
                r += 1
            
            zVal[i] += r-l  # set the z val as the size of the z box
            r -= 1  
        
        else: # inside the z box
            k = i - l   # index inside the z box

            if zVal[k] < r - i + 1: # case 2a, not reached end of z box, copy already computed z values across.
                zVal[i] = zVal[k]

            else: # case 2b, the number of matches of this z box exceeds what is computed at the start
                # start from r and check the next chars
                l = i

                while r < n and string[r] == string[r-l]: # compare chars
                    r += 1  # extend z box
                
                zVal[i] += r-l  # record the length of z box
                r -= 1    

    return zVal

def extBadChar(pat: str, len_pat: int):
    """
    2d array where the rows is the length of the pattern and the columns
    are each letter of the alphabet. A value of -1 represents no pre occuring 
    letter in the pattern corresponding to that index and all other values > -1
    represent where its right most occurance of that letter is in the pattern, starting from 0.
    """

    # create bad character 2d array
    badChars = [[-1]*ALPHABET_SIZE for i in range(len_pat)]

    # iterate through each row
    for i in range(len_pat - 1):

        # update next row with the previous row
        for j in range(ALPHABET_SIZE):
            badChars[i+1][j] = badChars[i][j]

        # update the next char in their row and column
        if badChars[i+1][ord(pat[i]) - UNICODE_A] < i: # update the specific column of the char to i
            badChars[i+1][ord(pat[i]) - UNICODE_A] = i

    return badChars

def goodSuffix(pat: str, len_pat: int):
    """
    A good suffix array of length of the pattern + 1. Each value in the array refers 
    to the index of the right endpoint of the right most substring that matches the suffix in a given range.
    The indexing starts from 1.
    """

    gs = [0] * (len_pat + 1)
    zArr = Zalg(pat[::-1])[::-1]

    # iterating through each zArr index
    for i in range(len_pat - 1):
        j = len_pat - zArr[i]
        
        # identifying if the preceding character are different
        if pat[i - zArr[i]] != pat[len_pat - zArr[i] - 1]:
            gs[j] = i + 1   # updating the good suffix with its right most substring that matches it

    return gs

def matchedPrefix(pat: str, len_pat: int):
    """
    The matched prefix is an array of size length of the pattern + 1, containing 
    values corresponding to the longest suffix of pat[i:] that is also a prefix of pat.
    """

    mp = [0] * (len_pat + 1)
    zArr = Zalg(pat)[::-1]
    longest = 0

    for i in range(len_pat):
        if zArr[i] == i + 1: # insuring the length of the 
            longest = max(zArr[i], longest)
        
        mp[-i - 2] = longest
    
    mp[0] = len_pat

    return mp

def search(string: str, pat: str):
    """
    Implementation of the Boyer-Moore algorithm, which utilises 
    the preprocessing to achieve a fast search. This function also uses 
    Galil's optimisation to reduce the number of comparisons.
    """

    len_string = len(string)
    len_pat = len(pat)

    matches = []

    # base case
    if len_string < len_pat:
        return matches

    # pre-processing
    badChar = extBadChar(pat, len_pat)
    gs = goodSuffix(pat, len_pat)
    mp = matchedPrefix(pat, len_pat)

    k = len_pat - 1 # alignment of end of pat relative to string

    # Galil's optimisation for where the good suffix value is > 0
    galil_k_start = -1
    galil_k_stop = -1
    # Galil's optimisation for where the good suffix value is = 0
    galil_k_mp = -1

    # iterate through the string
    while k < len_string:

        i = len_pat - 1     # character to compare in pat
        j = k               # character to compare in string

        # comparing pattern and string at index i
        while i >= 0 and pat[i] == string[j]:
            # utilising Galil's optimisation where gs[i+1] = 0
            if galil_k_mp == i:
                # skip the repeated substring in pattern and reset the galil variables
                i -= galil_k_mp  
                j -= galil_k_mp       
                galil_k_mp = -1

            # utilising Galil's optimisation where gs[i+1] > 0
            elif galil_k_stop - 1 == i:
                # skip the repeated substring in pattern and reset the galil variables
                i -= (galil_k_stop - galil_k_start)  
                j -= (galil_k_stop - galil_k_start)    
                galil_k_stop = -1
                galil_k_start = -1
            
            # Galil's optimisation is not used
            else:
                i -= 1
                j -= 1

        if i == -1: # iterated through all of pat
            matches.append(k - len_pat + 2)

            # update k
            if len_pat > 1:
                k += len_pat - mp[1] # shift by the 2nd largest matched prefix 
            else:
                k += 1

        else: # no match, move by max of bad character or good suffix rules
            # reset galil counters
            galil_k_mp = -1
            galil_k_stop = -1
            galil_k_start = -1

            # calculate the bad character shift
            badCharVal = badChar[i][ord(string[j]) - UNICODE_A]
            if badCharVal == -1:
                badCharShift = i + 1
            else:
                badCharShift = i - badCharVal

            # calculate the good suffix rule shift
            if gs[i+1] == 0:
                shift = len_pat - mp[i+1]
                galil_k_mp = mp[i+1]

            elif gs[i+1] > 0:
                shift = len_pat - gs[i+1]
                galil_k_start = gs[i+1] - len_pat + i + 1
                galil_k_stop = gs[i+1]
            
            finalShift = max(shift, badCharShift)

            k += finalShift
    return matches

def read_file(file: str):
    """
    reading lines within a file.
    """
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    return lines

if __name__ == "__main__":
    # reading in file names
    _, textFile, patFile = sys.argv

    # obtaining content from the files into a list
    textFileContents = read_file(textFile)
    patFileContents = read_file(patFile)

    matches = []

    # both text and pattern files need to have content
    if textFileContents and patFileContents:
        string = textFileContents[0]
        pat = patFileContents[0]
        
        # pat only contains a dot
        if pat == ".":
            for i in range(len(string)):
                matches.append(i+1)

        # pat contains characters and a dot
        elif "." in pat:

            #  split pat into two parts, seperated by "."
            pat1, pat2 = pat.split(".")

            matches1 = search(string, pat1)
            matches2 = search(string, pat2)

            len_pat1 = len(pat1)

            # iterating through the matches and pairing both patterns
            if pat[0] == ".": # dot is at the start
                for v in matches2:
                    if v != 0:
                        matches.append(v - 1)

            elif pat[-1] == ".": # "." is at the end
                len_string = len(string)
                for v in matches1:
                    if v + len_pat1 != len_string: # ensure that there is space for the "."
                        matches.append(v)
                
            else: # "." is in the middle
                for i in range(len(matches1)):
                    if matches1[i] + len_pat1 + 1 in matches2:
                        matches.append(matches1[i])

        # pat only contains characters
        else:
            matches = search(string, pat)
            for v in matches:
                matches.append(v)

    # writing output to output_q1.txt
    file = open("output_q2.txt", "w")
    for v in matches:
        file.write("{0}\n".format(v))
    file.close()

