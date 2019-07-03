from enum import Enum, auto


class NodeTypes(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    NUM = auto()
    EQ = auto()
    NE = auto()
    GT = auto()
    GE = auto()
    LT = auto()
    LE = auto()
    ASSIGN = auto()
    IDENT = auto()
    RETURN = auto()


class Node:
    def __init__(self, n_type):
        self.type = n_type


class NodeFactory:
    @classmethod
    def create_ope_node(self, n_type, left, right):
        node = Node(n_type)
        node.left = left
        node.right = right
        return node

    @classmethod
    def create_num_node(self, value):
        node = Node(NodeTypes.NUM)
        node.value = value
        return node

    @classmethod
    def create_ident_node(self, offset):
        node = Node(NodeTypes.IDENT)
        node.offset = offset
        return node

    @classmethod
    def create_return_node(self, child):
        node = Node(NodeTypes.RETURN)
        node.child = child
        return node
