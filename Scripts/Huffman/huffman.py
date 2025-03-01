from collections import Counter
# import pickle as pkl
import filecmp
import argparse
import bitarray

parser = argparse.ArgumentParser()
parser.add_argument('file', default=None)
args = parser.parse_args()


class Node():

    def __init__(self, label, value):
        self.label = label
        self.value = value
        self.right = None
        self.left = None

    def __repr__(self):
        return str((self.label, self.value, self.left, self.right))


class HuffmanTree():

    def __init__(self):
        self.nodes = []
        self.head = None
        self.dict = {}
        self.reversed_dict = {}

    def add_text(self, text):
        count = Counter(list(text))
        for key in count:
            self.add_node(Node(key, count[key]))

    def add_node(self, node):
        self.nodes.append(node)

        # sort inversely by node value
        self.nodes.sort(key=lambda x: x.value, reverse=True)

    def mount(self):

        while len(self.nodes) > 1:

            # get left/right nodes from end if list
            node_left = self.nodes[-2]
            node_right = self.nodes[-1]

            # set new node to be father of previus nodes
            node = Node(node_left.label + node_right.label,
                        node_left.value + node_right.value)
            #
            node.left = node_left
            node.right = node_right

            # remove last nodes
            self.nodes = self.nodes[:-2]

            # add new node
            self.add_node(node)

        # save root
        self.head = self.nodes[0]

        # create dict of letters
        self.__mount_dict()

        # create reverse dict
        self.__reverse_dict()

    def __nav_tree(self, node, code):

        # leaf node
        if node.left == node.right:
            self.dict[node.label] = code

        else:

            # left node
            if node.left:
                self.__nav_tree(node.left, code + '0')
            # right node
            if node.right:
                self.__nav_tree(node.right, code + '1')

    def __mount_dict(self):

        self.__nav_tree(self.head, '')

    def __reverse_dict(self):

        self.reversed_dict = {self.dict[key]: key for key in self.dict}

    def encode(self, text):

        result = ''

        for letter in list(text):

            # Letter is in dict?
            if self.dict.get(letter):
                result += self.dict[letter]
            else:
                result += '?'

        return result

    def decode(self, code):

        result = ''
        acc = ''

        code = [c for c in code if c.isdigit()]

        for number in code:
            acc += number

            # Is in dict?
            if self.reversed_dict.get(acc):
                result += self.reversed_dict[acc]
                acc = ''

        return result


if __name__ == '__main__':
    try:

        text = open(args.file, encoding='latin1', newline='\n', mode='r').read()

        tree = HuffmanTree()
        tree.add_text(text)
        tree.mount()

        string_encoded = tree.encode(text)
        bits_encoded = bitarray.bitarray(string_encoded)

        # See Dicts
        # print(tree.dict)
        # print(tree.reversed_dict)

        # Save file encoded
        with open(args.file + '.encode', 'wb') as w:
            bits_encoded.tofile(w)

        # Open file encoded
        bits_to_decode = bitarray.bitarray()
        with open(args.file + '.encode', 'rb') as r:
            bits_to_decode.fromfile(r)

        # Save file decoded
        with open(args.file + '.decode', 'w') as w:
            w.write(tree.decode(str(bits_to_decode)))

        # Tests
        a = Counter(text)
        b = Counter(tree.decode(str(bits_to_decode)))

        print('Dictionary of Counts are equal?', a == b)

        print('Check if files are equal:', filecmp.cmp(args.file, args.file + '.decode', shallow=False))

    except EOFError:
        pass
