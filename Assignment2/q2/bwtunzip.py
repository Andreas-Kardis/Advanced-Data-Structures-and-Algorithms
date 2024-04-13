"""
Name: Andreas Kardis
ID: 31468438
"""
import sys
import math

def decode_huffman(bits: str):
    """
    Decodes the huffman encoding where in binary 
    bits it is first given the ascii value, the code 
    length then the huffman code of a character.
    Returns 3 values: the character, 
    huffman code then the remaining bits to be processed.
    """
    # reading ascii
    ascii_bits = bits[0:7]
    ascii_num = bin_to_num(ascii_bits)
    char = chr(ascii_num)
    bits = bits[7:]

    # code length
    code_length, bits = decode_elias_omega(bits)
    huffman_code = bits[0:code_length]
    bits = bits[code_length:]

    return char, huffman_code, bits
    
def decode_elias_omega(bits: str):
    """
    Decoding of an encoding using Elias Omega encoding.
    This function returns 2 values: the decoded number 
    and rest of the bits to be decoded.
    """
    # if it is a code or length component
    if bits[0] == '0':

        length = 1
        j = 0   # index of the whole elias omega encoding
        while True:
            if bits[j] == '0': # reading a length component

                # reading a length component
                tmp_bits = ''
                for _ in range(length):
                    tmp_bits += bits[j]
                    j += 1
                
                # make leading bit a '1'
                tmp_bits = tmp_bits[1:]
                tmp_bits = '1' + tmp_bits

                # bin to number
                length = bin_to_num(tmp_bits) + 1

            else:   # reading code word of N
                tmp_bits = bits[j : j+length]
                bits = bits[j+length:]
                return bin_to_num(tmp_bits), bits

    else:
        bits = bits[1:]
        return 1, bits
    
def decode_bwt(bwt: list):
    """
    decoding of the bwt given as a list.
    Returns the original string.
    """
    bwt_len = len(bwt)
    tmp_bwt = bwt
    for _ in range(bwt_len - 1):
        tmp_bwt = sorted(tmp_bwt)

        for j in range(bwt_len):
            tmp_bwt[j] = bwt[j] + tmp_bwt[j]
    return sorted(tmp_bwt)


def bin_to_num(bits: str):
    """
    Translates a binary string into base 10
    """
    num = 0
    len_bits = len(bits)
    for i in range(len_bits):
        num += int(bits[i])*2**(len_bits - i - 1)
    return num

def num_to_bin(num: int):
    """
    Translates a base 10 number into base 2 binary string
    """
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

def read_bytes_to_bits(file: str):
    """
    read a bin file containing bytes and 
    transforms them into a binary string.
    """
    num_bytes = 3   # number of bytes to be read
    f = open(file, 'rb')
    cont = f.read(num_bytes)
    f.close()

    # converting output into a number
    n = int.from_bytes(cont, byteorder='big')   

    # converting the number into its binary form
    bin_str = num_to_bin(n) 

    # add leading '0's if they are missing
    bin_str_len = len(bin_str)
    if num_bytes * 8 != bin_str_len:
        leading_0s = (num_bytes * 8) - bin_str_len
        bin_str = ('0' * leading_0s) + bin_str
    
    return bin_str

def replen_bytes(bit_len: int, bits: str):
    """
    Calculates the number of bytes to replenish 
    from the number of bits used.
    """
    n = bit_len - len(bits)     # how many bits used 
    bytes = math.ceil(n / 8)    # number of bytes to replenish rounded up
    return bytes

def add_bits(old_bits: str, new_bits: int, num_bytes: int):
    """
    Adds new read bits to he end of the current string of bits.
    When reading bits from the file, leading 0s are cut off, these are added back.
    """
    n = int.from_bytes(new_bits, byteorder='big')   
    new_bits = num_to_bin(n)
    bit_len = len(new_bits)

    # if the number of bits read is less than expected and is not a multiple of 8
    # the first condition is to add leading 0s
    # the second condition is if at the end of file
    if (num_bytes * 8 > bit_len) and (bit_len % 8 != 0):    
        leading_0s = (num_bytes * 8) - bit_len
        if leading_0s > 7:  # max leading 0s is 7 as there needs to be at least a '1' in the leading byte '00000001'
            leading_0s -= 8
        return old_bits + ('0' * leading_0s) + new_bits
    
    else:
        return old_bits + new_bits

if __name__ == "__main__":
    _, binFile = sys.argv

    f = open(binFile, 'rb')

    # read 3 bytes of information initially
    bytes_to_read = 3
    content = f.read(bytes_to_read)
    n = int.from_bytes(content, byteorder='big')   
    bits = num_to_bin(n)
    bit_len = len(bits)

    if bytes_to_read * 8 > bit_len:
        leading_0s = (bytes_to_read * 8) - bit_len
        bits = ('0' * leading_0s) + bits

    bit_len = len(bits) # number of bits


    # read length of bwt
    bwt_length, bits = decode_elias_omega(bits)

    bytes_to_read = replen_bytes(bit_len, bits)
    if bytes_to_read > 0:
        content = f.read(bytes_to_read)
        bits = add_bits(bits, content, bytes_to_read)
    
    bit_len = len(bits)
  

    # read number of unique characters of bwt
    nUniqueChars, bits = decode_elias_omega(bits)

    bytes_to_read = replen_bytes(bit_len, bits)
    if bytes_to_read > 0:
        content = f.read(bytes_to_read)
        bits = add_bits(bits, content, bytes_to_read)

    bit_len = len(bits)


    # decoding the unique characters
    huffman_code_dict = {}
    for i in range(nUniqueChars):
        char, huffman_code, bits = decode_huffman(bits)

        huffman_code_dict[huffman_code] = char

        bytes_to_read = replen_bytes(bit_len, bits)
        if bytes_to_read > 0:
            content = f.read(bytes_to_read)
            bits = add_bits(bits, content, bytes_to_read)
        
        bit_len = len(bits)

    # decoding the bwt string
    bwt = []
    huffman_bits = ''
    bits_used = 0
    chars_read = 0
    
    while chars_read < bwt_length:
        huffman_bits += bits[0]
        bits = bits[1:]

        if huffman_bits in huffman_code_dict:
            # find the run length
            runLength, bits = decode_elias_omega(bits)
            for i in range(runLength):
                bwt.append(huffman_code_dict[huffman_bits])
            chars_read += runLength
            huffman_bits = ''

        bits_used += 1

        if bits_used == 8:
            bits_used = 0
            content = f.read(1)
            bits = add_bits(bits, content, 1)

    # decode bwt
    output = open('recovered.txt', 'w')
    output.write(decode_bwt(bwt)[0][1:])
    output.close()

    f.close()