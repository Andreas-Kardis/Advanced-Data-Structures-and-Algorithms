"""
Name: Andreas Kardis
ID: 31468438
"""

import sys
import st2sa

def BurrowsWheelerT(string: str):
    suffixArray = st2sa.suffixes(st2sa.UkkonenSuffixTree(string).root.children, len(string))

    for i in range(len(suffixArray)):
        suffixArray[i] -= 2

    return suffixArray

def runlength_encoding(string: str, suffixArray: list):
    runLength = []
    prev_char = string[suffixArray[0]]
    succ_chars = 1   # successive chars seen

    for i in range(1, len(string)): # iterating through string
        if string[suffixArray[i]] == prev_char:
            succ_chars += 1
        else:
            runLength.append((prev_char, succ_chars))
            prev_char = string[suffixArray[i]]
            succ_chars = 1
    
    runLength.append((prev_char, succ_chars))
    
    return runLength

def num_to_bin(num: int):
    bin_str = ''
    while num > 0:
        if num % 2 == 1:
            num -= 1
            num /= 2
            bin_str += '1'
        else:
            num /= 2
            bin_str += '0'

    return bin_str[::-1]

def Elias_encoding(num: int):
    N = num_to_bin(num)
    l_component = N
    L_num = len(N)

    while L_num > 1:
        l_bin = num_to_bin(L_num - 1)
        l_component = l_bin + l_component
        l_component = l_component[1:]
        l_component = '0' + l_component
        L_num = len(l_bin)

    return l_component

def Huffman_Encoding(string: str):
    freq_count = {}

    for c in string:
        if c not in freq_count:
            freq_count[c] = 1
        else:
            freq_count[c] += 1
    
    bin_tree = {}

    while len(freq_count) > 1:

        min1 = min(freq_count, key=freq_count.get)
        min1_val = freq_count[min1]
        del freq_count[min1]

        min2 = min(freq_count, key=freq_count.get)
        min2_val = freq_count[min2]
        del freq_count[min2]

        freq_count[min1 + min2] = min1_val + min2_val

        if min1 in bin_tree and min2 in bin_tree:
            bin_tree[min2].code = '1'
            bin_tree[min1].code = '0'
            bin_tree[min1 + min2] = Node(min1 + min2, bin_tree[min1], bin_tree[min2])
            del bin_tree[min1]
            del bin_tree[min2]

        elif min1 in bin_tree:
            bin_tree[min1].code = '0'
            bin_tree[min1 + min2] = Node(min1 + min2, bin_tree[min1], Node(min2, '', '', '1', True))
            
            del bin_tree[min1]

        elif min2 in bin_tree:
            bin_tree[min2].code = '1'
            bin_tree[min1 + min2] = Node(min1 + min2, Node(min1, '', '', '0', True), bin_tree[min2])
            del bin_tree[min2]

        else:
            bin_tree[min1 + min2] = Node(min1 + min2, Node(min1, '', '', '0', True), Node(min2, '', '', '1', True))

    root_lab = next(iter(bin_tree))
    huffman_codes_list = extract_huffman_codes(bin_tree[root_lab])

    huffman_codes = {}
    for i in range(len(huffman_codes_list)):
        huffman_codes[huffman_codes_list[i][0]] = huffman_codes_list[i][1]

    return huffman_codes

class Node:
    def __init__(self, lab:str, leftN: str, rightN: str, code: str = '', leaf: bool = False):
        self.lab = lab
        self.right = rightN
        self.left = leftN
        self.leaf = leaf
        self.code = code

def extract_huffman_codes(node: object, code: str = ''):
    res = []

    if node:
        code += node.code
        res = extract_huffman_codes(node.left, code)
        if node.leaf:
            res.append((node.lab, code))
        res = res + extract_huffman_codes(node.right, code)

    code = code[:-1]
    return res

def write_byte(string: str):
    if len(string) >= 8:
        str_to_write = string[:8]
        rem_str = string[8:]

        return str_to_write, rem_str
    
    else:
        return None, string
    
def write_file(file:str, data: str):
    """
    write binary str into a .bin file 1 byte at a time
    """
    f = open(file, 'ab')
    f.write(int(data, 2).to_bytes(length=1, byteorder='big'))
    f.close

def read_file(file: str):
    """
    reading lines within a file.
    """
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    return lines

if __name__ == "__main__":
    _, textFile = sys.argv

    textFileContents = read_file(textFile)
    string = textFileContents[0] + '$'
    
    bwt = BurrowsWheelerT(string)

    huffman_code = Huffman_Encoding(string)

    runlength_code = runlength_encoding(string, bwt)

    f = open('bwtencoded.bin', 'wb')

    bits = ''

    ### Header Part
    # length of bwt in elias code
    bits += Elias_encoding(len(bwt))
    bits_w, bits = write_byte(bits)
    if bits_w:
        f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

    # number of unique characters in the string in elias code
    bits += Elias_encoding(len(huffman_code))
    bits_w, bits = write_byte(bits)
    if bits_w:
        f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

    # encoding unique characters in the bwt 
    for k, v in huffman_code.items():
        # ascii of key 7 chars long
        ascii_bin = num_to_bin(ord(k))
        ascii_bin_len = len(ascii_bin)
        if ascii_bin_len < 7:
            n = 7 - ascii_bin_len
            ascii_bin = ('0' * n) + ascii_bin
        bits += ascii_bin
        bits_w, bits = write_byte(bits)
        if bits_w:
            f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

        # elias code of the code length (v)
        bits += Elias_encoding(len(v))
        bits_w, bits = write_byte(bits)
        if bits_w:
            f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

        # huffman code of the key
        bits += v
        bits_w, bits = write_byte(bits)
        if bits_w:
            f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

    ### Data Part
    # runlength encoding of the bwt
    for i in range(len(runlength_code)):
        bits += huffman_code[runlength_code[i][0]]
        bits_w, bits = write_byte(bits)
        if bits_w:
            f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

        bits += Elias_encoding(runlength_code[i][1])
        bits_w, bits = write_byte(bits)
        if bits_w:
            f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

    bits_len = len(bits)
    if len(bits) < 8:
        n = 8 - bits_len
        bits += '0' * n

    bits_w, bits = write_byte(bits)
    if bits_w:
        f.write(int(bits_w, 2).to_bytes(length=1, byteorder='big'))

    f.close()


