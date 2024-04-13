import sys

def Zalg(string: str):
    """
    Implementation of the z algorithm to compute z values 
    to identify matches in a string with a given pattern.
    The input contains the pattern and string seperated by a "$".

    Time Complexity: O(m + n), where m is the length of the pattern and n the length of the string.
    Space Complexity: O(n), n is the length of the string after the "$".
    """

    n = len(string)
    zVal = [0] * n

    # initialise left and right (z box) and k
    l = 0
    r = 0
    k = 0

    # iterate through the string
    for i in range(1, n):
        if i > r: # case 1, nothing has been matched yet
            # making z box the current character at i
            l = i 
            r = i

            # expanding the z box by increasing r for each matched character
            while r < n and string[r] == string[r-l]:
                r += 1
            
            zVal[i] += r-l  # set the z val as the size of the z box
            r -= 1  
        
        else: # inside the z box
            k = i - l   # index to corresponding z value

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

def concatPatString(pat, string):
    """
    Join the pattern and string, seperated by a "$". 
    The z values are then computed by the z algorithm

    Time Complexity: O(m + n), where m is the length of the pattern and n the length of the string.
    Space Complexity: O(n), n is the length of the string.
    """

    txt = pat + "$" + string

    zVals = Zalg(txt)
    return zVals
    
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

    numMatches = 0
    matches = []

    # both text and pattern files need to have content
    if textFileContents and patFileContents:
        string = textFileContents[0]
        pat = patFileContents[0]

        # z values of the pattern and string as normal and reversed
        zForw = concatPatString(pat, string)
        zBack = concatPatString(pat[::-1], string[::-1])

        len_string = len(string)
        len_pat = len(pat)
        len_z_arr = len(zForw) - 1

        # goes from the start of the string (skipping pat$...) to the possible last occurance of the pattern in the text.
        for i in range(len_pat + 1, len_z_arr - len_pat + 2):
            if zForw[i] == len_pat:
                matches.append("{0}".format(i - len_pat))
                numMatches +=1

            elif zForw[i] >= 1: # at least one character match
                opp_index = len_z_arr - i + 2

                # number of characters after the transposition error that match sum to the length of the pattern.
                if zBack[opp_index] == len_pat - zForw[i] - 2:

                    tranpos_err = i + zForw[i] - len_pat - 1
                    # checking if the transposition error characters match when switched
                    if (string[tranpos_err + 1] == pat[zForw[i]]) and ((string[tranpos_err] == pat[zForw[i] + 1])):
                        matches.append("{0} {1}".format(i - len_pat, i - len_pat + zForw[i]))
                        numMatches +=1

            else: # zForw[i] == 0 
                opp_index = len_z_arr - i + 2 # the start of the pattern didnt match, check if the rear of the pattern matches
                if zBack[opp_index] == len_pat - 2:
                    # check the first two chars switched with the first two chars of pat
                    if string[i - len_pat - 1] == pat[1] and string[i - len_pat] == pat[0]:
                        matches.append("{0} {0}".format(i - len_pat))
                        numMatches +=1

        # writing output to output_q1.txt
    file = open("output_q1.txt", "w")
    file.write("{0}\n".format(numMatches))
    for v in matches:
        file.write(v + "\n")
    file.close()