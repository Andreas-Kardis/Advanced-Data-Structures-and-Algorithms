"""
Name: Andreas Kardis
ID: 31468438
"""
import sys

globalEnd = -1

class Node:
    """
    This class creates a node and also stores the values of the edge that lead into it.
    """
    def __init__(self, extension: int, start: int, end: int, suffixLink: object = None):
        self.leaf = extension
        self.suffixLink = suffixLink
        self.start = start
        self.end = end
        self.children = {}

    def __getattribute__(self, name: str):
        """
        Is used to keep each leaf node up to date with the global end value.
        """
        if name == 'end' and self.leaf != None:
            return globalEnd
        
        return super(Node, self).__getattribute__(name)
            

class UkkonenSuffixTree:
    def __init__(self, string: str):
        """
        This method creates the suffix tree using Ukkonen's optimisations when the class is called.
        It uses the Node class along with the newNode method to create new edges and nodes.
        """
        global globalEnd
        self.string = string
        self.root = self.newNode(None, None, None)

        # base case, phase = extension = 0
        last_j = 0  # explicit extensions
        self.activeNode = self.root
        self.activeLength = 0
        self.rem = []
        globalEnd = 0
        self.root.children[string[0]] = self.newNode(1, 0, globalEnd)
        self.root.suffixLink = self.root    # root node is suffix linked to itself

        n = len(string)
        # phase
        for i in range(1, n):
            globalEnd += 1
            prevInternalNode = None

            j = last_j + 1  # as globalEnd performes all rule 1s
            # extension
            while j <= i:
                # skip-count down, where skipCountNode acts as the activeNode when it has traversed
                skipCountNode = self.traverse()

                # at the node and don't need to traverse down its edge
                if self.activeLength == 0:
                    # if the node already has a leading edge starting with string[i]
                    if string[i] in skipCountNode.children:
                        self.rem.append(i)

                        if prevInternalNode: # unresolved suffix link
                            prevInternalNode.suffixLink = self.activeNode
                            prevInternalNode = None

                        # If the edge starting with string[i] is only 1 char long, make it the activeNode
                        tmp_edge = skipCountNode.children[string[i]]
                        if tmp_edge.end - tmp_edge.start == 0:  # the edge is only 1 character long
                            self.activeNode = tmp_edge # make this edge the active node
                        else:
                            self.activeLength += 1

                        break

                    else:   # rule 2 (case 1)
                        skipCountNode.children[string[i]] = self.newNode(j+1, i, globalEnd)  # start at the active node and create a new leaf

                        # internal node was not created, so link the internal node previously created to active node
                        if prevInternalNode and prevInternalNode.suffixLink != self.activeNode: # unresolved suffix link
                            prevInternalNode.suffixLink = self.activeNode
                            prevInternalNode = None

                # traverse down edge and see if there is a match
                elif self.string[skipCountNode.start + self.activeLength] == self.string[i]:
                    self.rem.append(i)
                    self.activeLength += 1

                    if prevInternalNode: # unresolved suffix link
                            prevInternalNode.suffixLink = self.activeNode
                            prevInternalNode = None
                    break

                else: # no match, add an internal node
                    # Connect newEdge to the the pre-existing skipCountNode
                    # oldEdge acts as the pre-existing skipCountNode
                    oldEdge = self.newNode(None, None, None)
                    
                    # need to save skipCountNode variables in temporary variables as otherwise these values will be updated with newEdge
                    leaf = skipCountNode.leaf
                    oldEdge.leaf = leaf
                    start = skipCountNode.start
                    oldEdge.start = self.activeLength + start
                    end = skipCountNode.end
                    oldEdge.end = end
                    suffixLink = skipCountNode.suffixLink
                    oldEdge.suffixLink = suffixLink
                    children = skipCountNode.children
                    oldEdge.children = children

                    # newEdge takes skipCountNode's place and populates it correctly
                    newEdge = skipCountNode
                    newEdge.end = skipCountNode.start + self.activeLength - 1
                    newEdge.suffixLink = None
                    newEdge.leaf = None
                    newEdge.children = {}
                    
                    # add child to the new edge
                    newEdge.children[string[i]] = self.newNode(j+1, i, globalEnd)

                    # add the old edge to the new edge
                    newEdge.children[string[oldEdge.start]] = oldEdge

                    # check if the previous extension created an internal node
                    # save this node and link it to the new one if created in the same phase
                    if not prevInternalNode:
                        prevInternalNode = newEdge
                    else:
                        # update the previous internal node's suffix link to the new internal node
                        prevInternalNode.suffixLink = newEdge
                        prevInternalNode = newEdge
                
                if self.activeNode == self.activeNode.suffixLink or not self.activeNode.suffixLink:    # dont follow a suffix link out
                    if self.rem:
                        self.rem = self.rem[1:]
                    if self.activeLength > 0:
                        self.activeLength -= 1

                elif self.activeNode.suffixLink:
                    self.activeNode = self.activeNode.suffixLink  # follow suffix link out of active node
                    self.rem = self.rem[1:]

                    if not self.rem and self.activeLength > 0:
                        self.activeLength -= 1
                    
                last_j += 1

                j += 1

    def newNode(self, extension: int, start: int, end: int, suffixLink: object = None):
        """
        Creates a new node using the Node class.
        """
        node = Node(extension, start, end, suffixLink)

        return node
    
    def traverse(self):
        """
        This method uses the skip count optimisation to traverse down the tree. 
        It updates the remainder, active length and active node.
        The output is the current node to be considered.
        """
        # already at the node to consider
        if self.activeLength == 0 or not self.rem:
            return self.activeNode
        
        else:
            rem_length = len(self.rem)
            skipCountNode = self.activeNode.children[self.string[self.rem[rem_length - self.activeLength]]] # current edge and node being traversed

            curr_edge_length = skipCountNode.end - skipCountNode.start + 1   # accumulation of edge lengths being traversed
            
            while True:    
                # still need to traverse the tree to find edge and node to consider            
                if self.activeLength > curr_edge_length:
                    self.activeNode = skipCountNode  # most recent internal node visited
                    self.activeLength -= curr_edge_length
                    skipCountNode = skipCountNode.children[self.string[self.rem[rem_length - self.activeLength]]]
                    curr_edge_length = skipCountNode.end - skipCountNode.start + 1
                
                # reached edge and node to consider
                elif self.activeLength == curr_edge_length:
                    self.activeNode = skipCountNode
                    self.activeLength = 0
                    break

                else:   # final iteration of skip counting
                    break

            return skipCountNode
        
def extract_raw_suffixes(node: object):
    """
    This method traverses the suffix tree and recursively and returns the 
    leading character of the edges and the leaf value. The '' values 
    represent moving up a node and the None values represent going 
    up a node and reading its leaf value.
    The output is a list of these values.
    """
    # if key in node: return node[key].start
    l = []
    if node:
        for k, v in node.items():
            l += [k] + extract_raw_suffixes(v.children) + [v.leaf]
            l += ['']
            
        return l
    else:
        return []    # reached a leaf node
    
def suffixes(node: object, len_str):
    """
    Suffixes interpretes the list from extract_raw_suffixes to generate a suffix array.
    Output is a suffix array.
    """
    raw_suffix_list = extract_raw_suffixes(node)
    len_raw_suffix = len(raw_suffix_list)
    suffix_strings = []
    curr_suffix = ''
    i = 0   # suffix_strings index
    j = 0   # raw_suffix_list index

    while i < len_str + 1 and j < len_raw_suffix:
        if isinstance(raw_suffix_list[j], int):  # see a number
            suffix_strings.append((curr_suffix, raw_suffix_list[j]))
            curr_suffix = curr_suffix[:-1]  # remove last character
            i += 1
            j += 1

        elif raw_suffix_list[j] == None:    # see a None go to next suffix string
            curr_suffix = curr_suffix[:-1]  # remove last character
            j += 2  # skip the current none and next empty str

        elif raw_suffix_list[j] == '': # onto next suffix
            j += 1

        else:
            curr_suffix += raw_suffix_list[j]
            j += 1
            
    suffix_strings = sorted(suffix_strings)
    suffixArray = []
    for i in range(len(suffix_strings)):
        suffixArray.append(suffix_strings[i][1])

    return suffixArray
    

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

    suffixArray = suffixes(UkkonenSuffixTree(string).root.children, len(string))

    output_file = open('output_sa.txt', 'w')
    for i in range(len(suffixArray)):
        output_file.write('{0}\n'.format(suffixArray[i]))
        print(suffixArray[i])
    output_file.close()


