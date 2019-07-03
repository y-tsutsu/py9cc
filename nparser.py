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


class Parser:
    '''
    program    = stmt*
    stmt       = expr ";" | "return" expr ";"
    expr       = assign
    assign     = equality ("=" assign)?
    equality   = relational ("==" relational | "!=" relational)*
    relational = add ("<" add | "<=" add | ">" add | ">=" add)*
    add        = mul ("+" mul | "-" mul)*
    mul        = unary ("*" unary | "/" unary)*
    unary      = ("+" | "-")? term
    term       = num | ident | "(" expr ")"
    '''

    def __init__(self, tokens):
        self.__tokens = tokens
        self.__varnames = []

    def __create_ope_node(self, n_type, left, right):
        node = Node(n_type)
        node.left = left
        node.right = right
        return node

    def __create_num_node(self, value):
        node = Node(NodeTypes.NUM)
        node.value = value
        return node

    def __create_ident_node(self, name):
        node = Node(NodeTypes.IDENT)
        if name not in self.__varnames:
            self.__varnames.append(name)
        node.offset = (self.__varnames.index(name) + 1) * 8
        return node

    def __create_return_node(self, child):
        node = Node(NodeTypes.RETURN)
        node.child = child
        return node

    def parse(self):
        return self.__program(self.__tokens)

    def __program(self, tokens):
        '''
        program = stmt*
        '''
        nodes = []
        while not tokens.is_empty():
            nodes.append(self.__stmt(tokens))
        return nodes

    def __stmt(self, tokens):
        '''
        stmt = expr ";" | "return" expr ";"
        '''
        if tokens.consume_return():
            node = self.__create_return_node(self.__expr(tokens))
        else:
            node = self.__expr(tokens)
        tokens.expect(';')
        return node

    def __expr(self, tokens):
        '''
        expr = assign
        '''
        return self.__assign(tokens)

    def __assign(self, tokens):
        '''
        assign = equality ("=" assign)?
        '''
        node = self.__equality(tokens)
        if tokens.consume('='):
            node = self.__create_ope_node(NodeTypes.ASSIGN, node, self.__assign(tokens))
        return node

    def __parse_common_func(self, tokens, map_, next_func):
        node = next_func(tokens)
        while True:
            for k, v in map_.items():
                token = tokens.consume(k)
                if token:
                    node = self.__create_ope_node(v, node, next_func(tokens))
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
            return self.__create_ope_node(NodeTypes.SUB, self.__create_num_node(0), self.__term(tokens))
        return self.__term(tokens)

    def __term(self, tokens):
        '''
        term = num | ident | "(" expr ")"
        '''
        token = tokens.consume('(')
        if token:
            node = self.__expr(tokens)
            tokens.expect(')')
            return node
        token = tokens.consume_ident()
        if token:
            node = self.__create_ident_node(token.code[:token.length])
            return node
        token_num = tokens.expect_num()
        return self.__create_num_node(token_num.value)

    @property
    def varsize(self):
        return len(self.__varnames) * 8
