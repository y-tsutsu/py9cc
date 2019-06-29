from enum import Enum, auto


class NodeTypes(Enum):
    ND_ADD = auto()
    ND_SUB = auto()
    ND_MUL = auto()
    ND_DIV = auto()
    ND_NUM = auto()


class Node:
    def __init__(self):
        self.type = None
        self.left = None
        self.right = None
        self.value = None


class Parser:
    '''
    expr = mul ("+" mul | "-" mul)*
    mul  = term ("*" term | "/" term)*
    term = num | "(" expr ")"
    '''

    def __init__(self, tokens):
        self.__tokens = tokens

    def __create_node(self, n_type, left, right):
        node = Node()
        node.type = n_type
        node.left = left
        node.right = right
        return node

    def __create_num_node(self, value):
        node = Node()
        node.type = NodeTypes.ND_NUM
        node.value = value
        return node

    def parse(self):
        return self.__expr(self.__tokens)

    def __expr(self, tokens):
        '''
        expr = mul ("+" mul | "-" mul)*
        '''
        node = self.__mul(tokens)
        while True:
            token_add = tokens.consume('+')
            token_sub = tokens.consume('-')
            if token_add:
                node = self.__create_node(NodeTypes.ND_ADD, node, self.__mul(tokens))
            elif token_sub:
                node = self.__create_node(NodeTypes.ND_SUB, node, self.__mul(tokens))
            else:
                return node

    def __mul(self, tokens):
        '''
        mul = term ("*" term | "/" term)*
        '''
        node = self.__term(tokens)
        while True:
            token_mul = tokens.consume('*')
            token_div = tokens.consume('/')
            if token_mul:
                node = self.__create_node(NodeTypes.ND_MUL, node, self.__term(tokens))
            elif token_div:
                node = self.__create_node(NodeTypes.ND_DIV, node, self.__term(tokens))
            else:
                return node

    def __term(self, tokens):
        '''
        term = num | "(" expr ")"
        '''
        token = self.__tokens.consume('(')
        if token:
            node = self.__expr(tokens)
            self.__tokens.expect(')')
            return node
        token_num = self.__tokens.expect_num()
        return self.__create_num_node(token_num.value)
