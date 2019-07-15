from enum import Enum, auto

from generator import (AddressGenerator, AssignGenerator, BlockGenerator,
                       CallGenerator, DereferenceGenerator, ForGenerator,
                       FuncGenerator, IdentGenerator, IfElseGenerator,
                       IfGenerator, NumGenerator, OperatorGenerator,
                       ReturnGenerator, WhileGenerator)


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
    BLOCK = auto()
    CALL = auto()
    FUNC = auto()
    ADDR = auto()
    DEREF = auto()


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
    @staticmethod
    def create_num_node(value):
        node = Node(NodeTypes.NUM, NumGenerator())
        node.value = value
        return node

    @staticmethod
    def create_ope_node(n_type, left, right):
        node = Node(n_type, OperatorGenerator())
        node.left = left
        node.right = right
        return node

    @staticmethod
    def create_assign_node(left, right):
        node = Node(NodeTypes.ASSIGN, AssignGenerator())
        node.left = left
        node.right = right
        return node

    @staticmethod
    def create_ident_node(order, typeinfo):
        node = Node(NodeTypes.IDENT, IdentGenerator())
        node.order = order
        node.typeinfo = typeinfo
        return node

    @staticmethod
    def create_return_node(expr):
        node = Node(NodeTypes.RETURN, ReturnGenerator())
        node.expr = expr
        return node

    @staticmethod
    def create_if_node(expr, stmt):
        node = Node(NodeTypes.IF, IfGenerator())
        node.expr = expr
        node.stmt = stmt
        return node

    @staticmethod
    def create_if_else_node(expr, stmt, else_stmt):
        node = Node(NodeTypes.IF_ELSE, IfElseGenerator())
        node.expr = expr
        node.stmt = stmt
        node.else_stmt = else_stmt
        return node

    @staticmethod
    def create_while_node(expr, stmt):
        node = Node(NodeTypes.WHILE, WhileGenerator())
        node.expr = expr
        node.stmt = stmt
        return node

    @staticmethod
    def create_for_node(expr1, expr2, expr3, stmt):
        node = Node(NodeTypes.FOR, ForGenerator())
        node.expr1 = expr1
        node.expr2 = expr2
        node.expr3 = expr3
        node.stmt = stmt
        return node

    @staticmethod
    def create_block_node(stmts):
        node = Node(NodeTypes.BLOCK, BlockGenerator())
        node.stmts = stmts
        return node

    @staticmethod
    def create_call_node(name, args):
        node = Node(NodeTypes.CALL, CallGenerator())
        node.name = name
        node.args = args
        return node

    @staticmethod
    def create_for_infinite_dummy_node():
        return NodeFactory.create_num_node(1)

    @staticmethod
    def create_func_node(name, args_order_type, block):
        node = Node(NodeTypes.FUNC, FuncGenerator())
        node.name = name
        node.args_order_type = args_order_type
        node.block = block
        return node

    @staticmethod
    def create_address_node(unary):
        node = Node(NodeTypes.ADDR, AddressGenerator())
        node.unary = unary
        return node

    @staticmethod
    def create_dereference_node(unary):
        node = Node(NodeTypes.DEREF, DereferenceGenerator())
        node.unary = unary
        return node


class NodeContext:
    def __init__(self, nodes, varnames):
        self.__nodes = nodes
        self.__varnames = varnames
        for node in self.__nodes:
            node.varsize = self.__get_varsize(node.name)

    def __get_varsize(self, funcname):
        func_varnames = [x for x in self.__varnames if x.startswith(f'{funcname}:')]
        return len(func_varnames) * 8

    @property
    def nodes(self):
        return self.__nodes
