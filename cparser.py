from enum import Enum, auto

from node import NodeContext, NodeFactory, NodeTypes
from utility import error


class TypeInfo:
    class Types(Enum):
        INT = auto()

    def __init__(self, vtype, ptr_level):
        self.type = vtype
        self.ptr_level = ptr_level


class Parser:
    '''
    program    = func*
    func       = "int" ident "(" ("int" ident)* ")" "{" stm* "}"
    stmt       = "{" stmt* "}"
               | "if" "(" expr ")" stmt ("else" stmt)?
               | "while" "(" expr ")" stmt
               | "for" "(" expr? ";" expr? ";" expr? ")" stmt
               | "return" expr? ";"
               | expr ";"
    expr       = assign
    assign     = equality ("=" assign)?
    equality   = relational ("==" relational | "!=" relational)*
    relational = add ("<" add | "<=" add | ">" add | ">=" add)*
    add        = mul ("+" mul | "-" mul)*
    mul        = unary ("*" unary | "/" unary)*
    unary      = ("*" | "&") unary | ("+" | "-")? term
    term       = "(" expr ")" | "int" "*"* ident | ident ("(" expr* ")")? | num
    '''

    def __init__(self, token_context):
        self.__token_context = token_context
        self.__varinfos = []

    def parse(self):
        nodes = self.__program(self.__token_context)
        return NodeContext(nodes, [name for name, _ in self.__varinfos])

    def __program(self, tcontext):
        '''
        program = func*
        '''
        nodes = []
        while not tcontext.is_empty():
            nodes.append(self.__func(tcontext))
        return nodes

    def __func(self, tcontext):
        '''
        func = "int" ident "(" ("int" ident)* ")" "{" stmt* "}"
        '''
        tcontext.expect_type()
        funcname = tcontext.expect_ident().text
        tcontext.expect_symbol('(')
        args_order_type = []
        while not tcontext.consume_symbol(')'):
            type_token = tcontext.expect_type()
            ptr_level = 0
            while tcontext.consume_symbol('*'):
                ptr_level += 1
            vtype = self.__get_type_from_typename(type_token.text)
            typeinfo = TypeInfo(vtype, ptr_level)

            arg_token = tcontext.expect_ident()
            order = self.__regist_varname(arg_token.text, funcname, typeinfo)
            args_order_type.append((order, typeinfo))
            if not tcontext.consume_symbol(','):
                tcontext.expect_symbol(')')
                break
        if tcontext.current.text != '{':
            error('関数の"{"がありません')
        return NodeFactory.create_func_node(funcname, args_order_type, self.__stmt(tcontext, funcname))

    def __stmt(self, tcontext, funcname):
        '''
        stmt = "{" stmt* "}"
             | "if" "(" expr ")" stmt ("else" stmt)?
             | "while" "(" expr ")" stmt
             | "for" "(" expr? ";" expr? ";" expr? ")" stmt
             | "return" expr? ";"
             | expr ";"
        '''
        if tcontext.consume_symbol('{'):
            stmts = []
            while not tcontext.consume_symbol('}'):
                if tcontext.is_empty():
                    error('ブロックの"}"がありません')
                stmts.append(self.__stmt(tcontext, funcname))
            node = NodeFactory.create_block_node(stmts)
        elif tcontext.consume_if():
            tcontext.expect_symbol('(')
            expr = self.__expr(tcontext, funcname)
            tcontext.expect_symbol(')')
            stmt = self.__stmt(tcontext, funcname)
            else_stmt = self.__stmt(tcontext, funcname) if tcontext.consume_else() else None
            if else_stmt:
                node = NodeFactory.create_if_else_node(expr, stmt, else_stmt)
            else:
                node = NodeFactory.create_if_node(expr, stmt)
        elif tcontext.consume_while():
            tcontext.expect_symbol('(')
            expr = self.__expr(tcontext, funcname)
            tcontext.expect_symbol(')')
            stmt = self.__stmt(tcontext, funcname)
            node = NodeFactory.create_while_node(expr, stmt)
        elif tcontext.consume_for():
            tcontext.expect_symbol('(')
            expr1 = None if tcontext.consume_symbol(';') else self.__expr(tcontext, funcname)
            if expr1:
                tcontext.expect_symbol(';')
            expr2 = None if tcontext.consume_symbol(';') else self.__expr(tcontext, funcname)
            if expr2:
                tcontext.expect_symbol(';')
            else:
                expr2 = NodeFactory.create_for_infinite_dummy_node()
            expr3 = None if tcontext.consume_symbol(')') else self.__expr(tcontext, funcname)
            if expr3:
                tcontext.expect_symbol(')')
            stmt = self.__stmt(tcontext, funcname)
            node = NodeFactory.create_for_node(expr1, expr2, expr3, stmt)
        elif tcontext.consume_return():
            if tcontext.consume_symbol(';'):
                expr = None
            else:
                expr = self.__expr(tcontext, funcname)
                tcontext.expect_symbol(';')
            node = NodeFactory.create_return_node(expr)
        else:
            node = self.__expr(tcontext, funcname)
            tcontext.expect_symbol(';')
        return node

    def __expr(self, tcontext, funcname):
        '''
        expr = assign
        '''
        return self.__assign(tcontext, funcname)

    def __assign(self, tcontext, funcname):
        '''
        assign = equality ("=" assign)?
        '''
        node = self.__equality(tcontext, funcname)
        if tcontext.consume_symbol('='):
            node = NodeFactory.create_assign_node(node, self.__assign(tcontext, funcname))
        return node

    def __parse_common_func(self, tcontext, funcname, map_, next_func):
        node = next_func(tcontext, funcname)
        while True:
            for k, v in map_.items():
                token = tcontext.consume_symbol(k)
                if token:
                    node = NodeFactory.create_ope_node(v, node, next_func(tcontext, funcname))
                    break
            else:
                return node

    def __equality(self, tcontext, funcname):
        '''
        equality = relational ("==" relational | "!=" relational)*
        '''
        map_ = {'==': NodeTypes.EQ, '!=': NodeTypes.NE}
        return self.__parse_common_func(tcontext, funcname, map_, self.__relational)

    def __relational(self, tcontext, funcname):
        '''
        relational = add ("<" add | "<=" add | ">" add | ">=" add)*
        '''
        map_ = {'<': NodeTypes.LT, '<=': NodeTypes.LE, '>': NodeTypes.GT, '>=': NodeTypes.GE}
        return self.__parse_common_func(tcontext, funcname, map_, self.__add)

    def __add(self, tcontext, funcname):
        '''
        add = mul ("+" mul | "-" mul)*
        '''
        map_ = {'+': NodeTypes.ADD, '-': NodeTypes.SUB}
        return self.__parse_common_func(tcontext, funcname, map_, self.__mul)

    def __mul(self, tcontext, funcname):
        '''
        mul = unary ("*" unary | "/" unary)*
        '''
        map_ = {'*': NodeTypes.MUL, '/': NodeTypes.DIV}
        return self.__parse_common_func(tcontext, funcname, map_, self.__unary)

    def __unary(self, tcontext, funcname):
        '''
        unary = ("&" | "*") unary | ("+" | "-")? term
        '''
        token = tcontext.consume_symbol('&')
        if token:
            return NodeFactory.create_address_node(self.__unary(tcontext, funcname))

        token = tcontext.consume_symbol('*')
        if token:
            return NodeFactory.create_dereference_node(self.__unary(tcontext, funcname))

        token = tcontext.consume_symbol('+')
        if token:
            return self.__term(tcontext, funcname)

        token = tcontext.consume_symbol('-')
        if token:
            return NodeFactory.create_ope_node(NodeTypes.SUB, NodeFactory.create_num_node(0), self.__term(tcontext, funcname))

        return self.__term(tcontext, funcname)

    def __term(self, tcontext, funcname):
        '''
        term = "(" expr ")" | "int" "*"* ident | ident ("(" expr* ")")? | num
        '''
        token = tcontext.consume_symbol('(')
        if token:
            node = self.__expr(tcontext, funcname)
            tcontext.expect_symbol(')')
            return node

        token = tcontext.consume_type()
        if token:
            ptr_level = 0
            while tcontext.consume_symbol('*'):
                ptr_level += 1
            vtype = self.__get_type_from_typename(token.text)
            typeinfo = TypeInfo(vtype, ptr_level)
            name = tcontext.expect_ident().text
            order = self.__regist_varname(name, funcname, typeinfo)
            node = NodeFactory.create_ident_node(order, typeinfo)
            return node

        token = tcontext.consume_ident()
        if token:
            name = token.text
            if tcontext.consume_symbol('('):
                args = []
                while not tcontext.consume_symbol(')'):
                    args.append(self.__expr(tcontext, funcname))
                    if not tcontext.consume_symbol(','):
                        tcontext.expect_symbol(')')
                        break
                node = NodeFactory.create_call_node(name, args)
            else:
                order, typeinfo = self.__get_order_and_type_from_varname(name, funcname)
                node = NodeFactory.create_ident_node(order, typeinfo)
            return node

        token_num = tcontext.expect_num()
        return NodeFactory.create_num_node(token_num.value)

    def __regist_varname(self, varname, funcname, typeinfo):
        name = f'{funcname}::{varname}'
        if name in [n for n, t in self.__varinfos]:
            error(f'既に変数が宣言されています {name}')
        self.__varinfos.append((name, typeinfo))
        order, _ = self.__get_order_and_type_from_varname(varname, funcname)
        return order

    def __get_order_and_type_from_varname(self, varname, funcname):
        name = f'{funcname}::{varname}'
        if name not in [n for n, t in self.__varinfos]:
            error(f'未宣言の変数が使われています {name}')
        name_type = [(n, t) for n, t in self.__varinfos if n.startswith(f'{funcname}:')]
        index = [n for n, t in name_type].index(name)
        return index + 1, name_type[index][1]

    def __get_type_from_typename(self, typename):
        type_map = {'int': TypeInfo.Types.INT}
        if typename not in type_map:
            error(f'不明な型名です {typename}')
        return type_map[typename]
