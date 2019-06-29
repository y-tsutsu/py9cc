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


class Node:
    def __init__(self):
        self.type = None
        self.left = None
        self.right = None
        self.value = None


class Parser:
    '''
    expr       = equality
    equality   = relational ("==" relational | "!=" relational)*
    relational = add ("<" add | "<=" add | ">" add | ">=" add)*
    add        = mul ("+" mul | "-" mul)*
    mul        = unary ("*" unary | "/" unary)*
    unary      = ("+" | "-")? term
    term       = num | "(" expr ")"
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
        node.type = NodeTypes.NUM
        node.value = value
        return node

    def parse(self):
        return self.__expr(self.__tokens)

    def __expr(self, tokens):
        '''
        expr = equality
        '''
        return self.__equality(tokens)

    def __parse_common_func(self, tokens, map_, next_func):
        node = next_func(tokens)
        while True:
            for k, v in map_.items():
                token = tokens.consume(k)
                if token:
                    node = self.__create_node(v, node, next_func(tokens))
                    break
            else:
                return node

    def __equality(self, tokens):
        '''
        equality = relational ("==" relational | "!=" relational)*
        '''
        map_ = {'==': NodeTypes.EQ, '!=': NodeTypes.NE}
        return self.__parse_common_func(tokens, map_, self.__relational)

    def __relational(self, tokens):
        '''
        relational = add ("<" add | "<=" add | ">" add | ">=" add)*
        '''
        map_ = {'<': NodeTypes.LT, '<=': NodeTypes.LE, '>': NodeTypes.GT, '>=': NodeTypes.GE}
        return self.__parse_common_func(tokens, map_, self.__add)

    def __add(self, tokens):
        '''
        add = mul ("+" mul | "-" mul)*
        '''
        map_ = {'+': NodeTypes.ADD, '-': NodeTypes.SUB}
        return self.__parse_common_func(tokens, map_, self.__mul)

    def __mul(self, tokens):
        '''
        mul = unary ("*" unary | "/" unary)*
        '''
        map_ = {'*': NodeTypes.MUL, '/': NodeTypes.DIV}
        return self.__parse_common_func(tokens, map_, self.__unary)

    def __unary(self, tokens):
        '''
        unary = ("+" | "-")? term
        '''
        token = tokens.consume('+')
        if token:
            return self.__term(tokens)
        token = tokens.consume('-')
        if token:
            return self.__create_node(NodeTypes.SUB, self.__create_num_node(0), self.__term(tokens))
        return self.__term(tokens)

    def __term(self, tokens):
        '''
        term = num | "(" expr ")"
        '''
        token = tokens.consume('(')
        if token:
            node = self.__expr(tokens)
            tokens.expect(')')
            return node
        token_num = tokens.expect_num()
        return self.__create_num_node(token_num.value)
