import random
import sys

def gcd(n: int, m: int):
    """
    gcd returns the greatest common divider of n and m 
    using Euclid's algorithm.
    """
    while m > 0:
        tmp = m
        m = n % tmp
        n = tmp

    return n

def numToBin(num: int):
    """
    Find the binary representation of num. The binary output is a str.
    """
    bin_str = ''
    while num > 0:
        if num % 2 == 1:
            num -= 1
            num = num // 2
            bin_str += '1'
        else:
            num = num // 2
            bin_str += '0'

    return bin_str[::-1]

def modularExponentiation(a: int, b: int, n: int):
    """
    Perform modular exponentiation by repeated squaring.
    The represented input is in the form of a^b mod n.
    """
    if b == 0:
        return a % n
    binaryExp = numToBin(b)[::-1]

    current = a % n
    if binaryExp[0] == '1':
        result = current
    else:
        result = 1

    # a^(2^0) mod n = 1, all other results of current will be 1
    if current == 1:
            return result

    for i in range(1, len(binaryExp)):
        # computing next term in the sequence to reach a^(2^i) mod n
        current = (current * current) % n
        
        # check if current = 1, as all other current values will then be 1
        if current == 1:
            return result

        elif binaryExp[i] == '1':
            result = (result * current) % n
        
    return result

def millerRabinRandomisedPrimality(n: int, k: int):
    """
    This function performs the miller rabin randomised primality test returning a boolean value.
    False represents a composite found and True represents a prime found.

    Assuming input >= (2^3) - 1 and always odd.
    """
    # represent n - 1 as (2^s) * t
    s = 0
    t = n - 1
    while t % 2 == 0:
        s += 1
        t = t//2

    # run for k tests
    for i in range(k):
        a = random.randint(2, n-2)

        # fermat's little theorem
        if modularExponentiation(a, (2**s) * t, n) != 1:
            return False
        
        # perform the sequence test
        prev_x_j = modularExponentiation(a, 0, n)
        for j in range(1, s):
            x_j = modularExponentiation(a, j, n)
            if x_j == 1 and (prev_x_j != 1 and prev_x_j != n-1):
                return False
            prev_x_j = x_j
    
    return True

if __name__ == "__main__":
    _, d = sys.argv

    # find primes p and q, which are the two smallest primes after the initial n
    n = (2**int(d))
    primes = []
    primesFound = 0
    while primesFound < 2:
        if millerRabinRandomisedPrimality(n - 1, 6):
            primes.append(n - 1)
            primesFound += 1
            n *= 2

        else:
            n *= 2

    modulus = primes[0] * primes[1]
    vLambda = ((primes[0] - 1)*(primes[1] - 1))//gcd(primes[0] - 1, primes[1] - 1)

    # check if the randomly chosen exp and vLambda are relatively prime
    while True:
        exp = random.randint(3, vLambda - 1)
        if gcd(exp, vLambda) == 1:
            break

    # write output to the respective files
    file = open("publickeyinfo.txt", "w")
    file.write("# modulus (n) \n{0}\n".format(modulus))
    file.write("# exponent (e) \n{0}\n".format(exp))
    file.close()

    file = open("secretprimes.txt", "w")
    file.write("# p \n{0}\n".format(primes[0]))
    file.write("# q \n{0}\n".format(primes[1]))
    file.close()
