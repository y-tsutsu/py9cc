from enum import Enum, auto

from generator import (AssignGenerator, ForGenerator, IdentGenerator,
                       IfElseGenerator, IfGenerator, NumGenerator,
                       OperatorGenerator, ReturnGenerator, WhileGenerator)


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
    IF = auto()
    IF_ELSE = auto()
    WHILE = auto()
    FOR = auto()


class Node:
    def __init__(self, n_type, generator):
        self.__type = n_type
        self.__generator = generator

    def generate(self, output):
        self.__generator.generate(self, output)

    @property
    def type(self):
        return self.__type


class NodeFactory:
    @classmethod
    def create_num_node(self, value):
        node = Node(NodeTypes.NUM, NumGenerator())
        node.value = value
        return node

    @classmethod
    def create_ope_node(self, n_type, left, right):
        node = Node(n_type, OperatorGenerator())
        node.left = left
        node.right = right
        return node

    @classmethod
    def create_assign_node(self, left, right):
        node = Node(NodeTypes.ASSIGN, AssignGenerator())
        node.left = left
        node.right = right
        return node

    @classmethod
    def create_ident_node(self, offset):
        node = Node(NodeTypes.IDENT, IdentGenerator())
        node.offset = offset
        return node

    @classmethod
    def create_return_node(self, child):
        node = Node(NodeTypes.RETURN, ReturnGenerator())
        node.child = child
        return node

    @classmethod
    def create_if_node(self, expr, stmt):
        node = Node(NodeTypes.IF, IfGenerator())
        node.expr = expr
        node.stmt = stmt
        return node

    @classmethod
    def create_if_else_node(self, expr, stmt, else_stmt):
        node = Node(NodeTypes.IF_ELSE, IfElseGenerator())
        node.expr = expr
        node.stmt = stmt
        node.else_stmt = else_stmt
        return node

    @classmethod
    def create_while_node(self, expr, stmt):
        node = Node(NodeTypes.WHILE, WhileGenerator())
        node.expr = expr
        node.stmt = stmt
        return node

    @classmethod
    def create_for_node(self, expr1, expr2, expr3, stmt):
        node = Node(NodeTypes.FOR, ForGenerator())
        node.expr1 = expr1
        node.expr2 = expr2
        node.expr3 = expr3
        node.stmt = stmt
        return node


class Parser:
    '''
    program    = stmt*
    stmt       = expr ";"
               | "if" "(" expr ")" stmt ("else" stmt)?
               | "while" "(" expr ")" stmt
               | "for" "(" expr? ";" expr? ";" expr? ")" stmt
               | "return" expr ";"
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
        stmt = expr ";"
             | "if" "(" expr ")" stmt ("else" stmt)?
             | "while" "(" expr ")" stmt
             | "for" "(" expr? ";" expr? ";" expr? ")" stmt
             | "return" expr ";"
        '''
        if tokens.consume_if():
            tokens.expect_symbol('(')
            expr = self.__expr(tokens)
            tokens.expect_symbol(')')
            stmt = self.__stmt(tokens)
            else_stmt = self.__stmt(tokens) if tokens.consume_else() else None
            if else_stmt:
                node = NodeFactory.create_if_else_node(expr, stmt, else_stmt)
            else:
                node = NodeFactory.create_if_node(expr, stmt)
        elif tokens.consume_while():
            tokens.expect_symbol('(')
            expr = self.__expr(tokens)
            tokens.expect_symbol(')')
            stmt = self.__stmt(tokens)
            node = NodeFactory.create_while_node(expr, stmt)
        elif tokens.consume_for():
            tokens.expect_symbol('(')
            expr1 = None if tokens.consume_symbol(';') else self.__expr(tokens)
            if expr1:
                tokens.expect_symbol(';')
            expr2 = None if tokens.consume_symbol(';') else self.__expr(tokens)
            if expr2:
                tokens.expect_symbol(';')
            expr3 = None if tokens.consume_symbol(')') else self.__expr(tokens)
            if expr3:
                tokens.expect_symbol(')')
            stmt = self.__stmt(tokens)
            node = NodeFactory.create_for_node(expr1, expr2, expr3, stmt)
        elif tokens.consume_return():
            node = NodeFactory.create_return_node(self.__expr(tokens))
            tokens.expect_symbol(';')
        else:
            node = self.__expr(tokens)
            tokens.expect_symbol(';')
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
        if tokens.consume_symbol('='):
            node = NodeFactory.create_assign_node(node, self.__assign(tokens))
        return node

    def __parse_common_func(self, tokens, map_, next_func):
        node = next_func(tokens)
        while True:
            for k, v in map_.items():
                token = tokens.consume_symbol(k)
                if token:
                    node = NodeFactory.create_ope_node(v, node, next_func(tokens))
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
        token = tokens.consume_symbol('+')
        if token:
            return self.__term(tokens)
        token = tokens.consume_symbol('-')
        if token:
            return NodeFactory.create_ope_node(NodeTypes.SUB, NodeFactory.create_num_node(0), self.__term(tokens))
        return self.__term(tokens)

    def __term(self, tokens):
        '''
        term = num | ident | "(" expr ")"
        '''
        token = tokens.consume_symbol('(')
        if token:
            node = self.__expr(tokens)
            tokens.expect_symbol(')')
            return node
        token = tokens.consume_ident()
        if token:
            name = token.code[:token.length]
            if name not in self.__varnames:
                self.__varnames.append(name)
            offset = (self.__varnames.index(name) + 1) * 8
            node = NodeFactory.create_ident_node(offset)
            return node
        token_num = tokens.expect_num()
        return NodeFactory.create_num_node(token_num.value)

    @property
    def varsize(self):
        return (len(self.__varnames) + 1) * 8
