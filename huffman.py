#!/usr/bin/env python
# Antti Palosaari <crope+uni@iki.fi>

import sys
import re
import argparse
import time


# 521144A, ADS, University of Oulu, Finland.
# Example implementations of heapsort and
# priority queue (an application of heapsort).
# Defines the required data structures, the
# required routines and the algorithm.
# Heap data structure declaration
# Heap is defined by two attributes:
#       - a base array
#       - size of the actual heap
class Heap:
    def __init__(self, array=None):
        if array == None:
            array = []
        self.data = [Node(None, 0, None, None)] + array[:]  # omit index 0 in heap data
        self.size = len(array)


# Navigation routines for binary trees.
def getParent(i):
    return i / 2  # automatically floored

def getLeftChild(i):
    return 2 * i

def getRightChild(i):
    return (2 * i + 1)


# minHeapify routine.
# Enforce the max-heap property on a sub-heap
# whose root node is the element at index i.
# Utilizes the following properties ('heap property')
# that always hold for heaps:

# Heap property for max-heaps
# aHeap.data[getParent(i)] >= aHeap.data[i]

# Heap property for min-heaps
# aHeap.data[getParent(i)] <= aHeap.data[i]

def minHeapify(aHeap, i):
    left = getLeftChild(i)
    right = getRightChild(i)
    
    if left <= aHeap.size and aHeap.data[left].weight < aHeap.data[i].weight:
        smallest = left
    else:
        smallest = i

    if right <= aHeap.size and aHeap.data[right].weight < aHeap.data[smallest].weight:
        smallest = right

    if smallest != i:
        aHeap.data[i], aHeap.data[smallest] = aHeap.data[smallest], aHeap.data[i]
        minHeapify(aHeap, smallest)


        
# Priority queue implentation based on the heap given above.

# Priority queue is a data structure for managing a set of elements S
# where each node is associated with a certain priority (key).

# The following operations are implemented here:
# insert(S, x)
# getMaximum(S)
# extractMax(S)
# increaseKey(S, x, k)

# For more information, see for example
# http://en.wikipedia.org/wiki/Priority_queue

    
# routine that returns and extracts the node with the highest priority
def heapExtractMin(aHeap):
    if aHeap.size < 1:
        return None
    max_ = aHeap.data[1]
    aHeap.data[1] = aHeap.data[aHeap.size]
    aHeap.size = aHeap.size - 1
    minHeapify(aHeap, 1)
    return max_
    
# operation that changes the priority of a designated node.
def heapIncreaseKey(aHeap, i, key):
    if key.weight < aHeap.data[i].weight:
        return None  # error: trying to decrease the priority

    aHeap.data[i] = key
    while i > 1 and aHeap.data[getParent(i)].weight > aHeap.data[i].weight:
        aHeap.data[i], aHeap.data[getParent(i)] = aHeap.data[getParent(i)], aHeap.data[i]
        i = getParent(i)

# implementation of 'insert' for a heap-based priority queue.
def minHeapInsert(aHeap, key):
#    aHeap.data.append.
    aHeap.size = aHeap.size + 1
    if aHeap.size == len(aHeap.data):
        aHeap.data.append(Node(None, -sys.maxint, None, None))  # sentinel
    else:
        aHeap.data[aHeap.size] = Node(None, -sys.maxint, None, None)  # sentinel

    heapIncreaseKey(aHeap, aHeap.size, key)

class Node:
    def __init__(self, s = None, w = None, l = None, r = None):
        self.symbol = s
        self.weight = w
        self.left = l
        self.right = r

# post-order traverse recursively whole tree
def traverseTree(codeTable, node, code):
    if (node == None):
        return

    if (node.symbol != None):
        codeTable[node.symbol] = code 

    traverseTree(codeTable, node.left, code + '0')
    traverseTree(codeTable, node.right, code + '1')


def encode(f):
    '''
    Collecting the symbol, weight pairs
    Reads letters from file and populates dictionary with count of each letter.
    '''
    dictionary = {}
    data = f.read()

    for c in data:
        dictionary[c] = dictionary.get(c, 0) + 1

    '''
    Min priority queue by Node weight.
    '''
    # create empty queue
    minPriQueue = Heap()
    
    # populate queue 
    for key, value in dictionary.iteritems():
        minHeapInsert(minPriQueue, Node(key, value))
    
    # read queue
    while True:
        left = heapExtractMin(minPriQueue)
        right = heapExtractMin(minPriQueue)
        # Queue is empty, left contains root node
        if (right == None):
            break
        minHeapInsert(minPriQueue, Node(None, left.weight + right.weight, left, right))

    node = left
    
    codeTable = {}
    traverseTree(codeTable, node, '')
    
    # format and write data to file
    with open('encoded.txt', 'w') as f:
        lenOriginal = len(data)
        lenEncoded = 0
        # translation table
        for key, value in codeTable.iteritems():
            f.write('%s %s\n' % (repr(key), value))
        
        # marker
        f.write('----\n')

        # encoded data
        for c in data:
            f.write('%s' % (codeTable[c]))
            lenEncoded += len(codeTable[c])
        f.write('\n')

        # marker
        f.write('----\n')

        # compression ratio
        ratio = 1.0 * lenEncoded / (lenOriginal * 8)
        f.write('Compression ratio: %d / (%d * 8) = %.3f\n' % (lenEncoded, lenOriginal, ratio))

def decode(f):
    marker = 0
    table = {}
    
    for line in f:
        line = line.strip()
        if (line == '----'):
            marker += 1
        elif (marker == 0):
            key = re.findall(r'(\d{1,}$)', line)[0]
            val = re.findall(r'(^.{3,6} )', line)[0]
            '''
            Ugly hack! Backslash is special character that must be escaped in
            order to use. However, given sample input doesn't escape it, what
            it still do for other special characters. Do it here manually for
            that single character in order to proceed. For more information
            about special characters, refer Python documentation:
            http://docs.python.org/2/reference/lexical_analysis.html#string-literals
            '''
            if (val == "'\\' "):
                print('bad escape detected - workaround applied')
                val = "'\\\\' "

            val = eval(val)
            table[key] = val
        elif (marker == 1):
            data = line
            
    text = ""
    start = 0
    stop = 0
    for i in range(0, len(data) + 1):
        stop = i
        key = data[start:stop]
        if (key in table):
            text = text + table[key]
            start = stop

    with open('decoded.txt', 'w') as f:
        f.write('%s' % (text))
    
def main():
    parser = argparse.ArgumentParser(description='Huffman encoder and decoder', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('file', type=argparse.FileType('r'), help='Specify the input file')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-e', '--encode', action='store_true', help='Encode the input file to encoded.txt')
    group.add_argument('-d', '--decode', action='store_true', help='Decode the input file to decoded.txt')
    parser.add_argument('-t', '--time', action='store_true', help='Measure elapsed time')
    args = parser.parse_args()
    
    t0 = time.time()

    if (args.encode == True):
        encode(args.file)
    elif (args.decode == True):
        decode(args.file)

    t1 = time.time()
    
    if (args.time == True):
        print ('Time elapsed {0} seconds'.format(t1 - t0))

if __name__ == "__main__":
    main()
