from node import NodeContext, NodeFactory, NodeTypes
from utility import error


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
    term       = "(" expr ")" | "int" ident | ident ("(" expr* ")")? | num
    '''

    def __init__(self, token_context):
        self.__token_context = token_context
        self.__varnames = []

    def parse(self):
        nodes = self.__program(self.__token_context)
        return NodeContext(nodes, self.__varnames)

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
        arg_offsets = []
        while not tcontext.consume_symbol(')'):
            tcontext.expect_type()
            arg_token = tcontext.expect_ident()
            offset = self.__regist_varname(arg_token.text, funcname)
            arg_offsets.append(offset)
            if not tcontext.consume_symbol(','):
                tcontext.expect_symbol(')')
                break
        if tcontext.current.text != '{':
            error('関数の"{"がありません')
        return NodeFactory.create_func_node(funcname, arg_offsets, self.__stmt(tcontext, funcname))

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
        term = "(" expr ")" | "int" ident | ident ("(" expr* ")")? | num
        '''
        token = tcontext.consume_symbol('(')
        if token:
            node = self.__expr(tcontext, funcname)
            tcontext.expect_symbol(')')
            return node

        token = tcontext.consume_type()
        if token:
            name = tcontext.expect_ident().text
            offset = self.__regist_varname(name, funcname)
            node = NodeFactory.create_ident_node(offset)
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
                offset = self.__get_offset_from_varname(name, funcname)
                node = NodeFactory.create_ident_node(offset)
            return node

        token_num = tcontext.expect_num()
        return NodeFactory.create_num_node(token_num.value)

    def __regist_varname(self, varname, funcname):
        name = f'{funcname}::{varname}'
        if name in self.__varnames:
            error(f'既に変数が宣言されています {name}')
        self.__varnames.append(name)
        return self.__get_offset_from_varname(varname, funcname)

    def __get_offset_from_varname(self, varname, funcname):
        name = f'{funcname}::{varname}'
        if name not in self.__varnames:
            error(f'未宣言の変数が使われています {name}')
        func_varnames = [x for x in self.__varnames if x.startswith(f'{funcname}:')]
        offset = (func_varnames.index(name) + 1) * 8
        return offset
