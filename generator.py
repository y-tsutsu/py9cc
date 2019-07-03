from nparser import NodeTypes
from utility import error


class Generator:
    def __init__(self, nodes, c_code, varsize):
        self.__nodes = nodes
        self.__c_code = c_code
        self.__varsize = varsize

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_prologue(self.__varsize)
        gen3 = self.__gen_from_nodes(self.__nodes)
        gen4 = self.__gen_epilogue()
        return gen1 + gen2 + gen3 + gen4

    def __gen_pre(self):
        result = []
        result.append('.intel_syntax noprefix')
        result.append('.global main')
        result.append('main:')
        return result

    def __gen_prologue(self, varsize):
        result = []
        result.append(f'  push rbp')
        result.append(f'  mov rbp, rsp')
        result.append(f'  sub rsp, {varsize}')
        return result

    def __gen_epilogue(self):
        result = []
        result.append('  mov rsp, rbp')
        result.append('  pop rbp')
        result.append('  ret')
        return result

    def __gen_from_nodes(self, nodes):
        result = []
        for x in nodes:
            self.__gen_from_node_inner(x, result)
            result.append('  pop rax')
        return result

    def __gen_from_node_inner(self, node, output):
        funcs = [self.__gen_return, self.__gen_num, self.__gen_ident,
                 self.__gen_assign, self.__gen_operator]
        for func in funcs:
            if func(node, output):
                return

        error(f'ジェネレートできませんでした {node.type}')

    def __gen_return(self, node, output):
        if node.type == NodeTypes.RETURN:
            self.__gen_from_node_inner(node.child, output)
            output.append('  pop rax')
            output.append('  mov rsp, rbp')
            output.append('  pop rbp')
            output.append('  ret')
        else:
            return False
        return True

    def __gen_num(self, node, output):
        if node.type == NodeTypes.NUM:
            output.append(f'  push {node.value}')
        else:
            return False
        return True

    def __gen_ident(self, node, output):
        if node.type == NodeTypes.IDENT:
            self.__gen_lval(node, output)
            output.append('  pop rax')
            output.append('  mov rax, [rax]')
            output.append('  push rax')
        else:
            return False
        return True

    def __gen_assign(self, node, output):
        if node.type == NodeTypes.ASSIGN:
            self.__gen_lval(node.left, output)
            self.__gen_from_node_inner(node.right, output)
            output.append('  pop rdi')
            output.append('  pop rax')
            output.append('  mov [rax], rdi')
            output.append('  push rdi')
        else:
            return False
        return True

    def __gen_operator(self, node, output):
        self.__gen_from_node_inner(node.left, output)
        self.__gen_from_node_inner(node.right, output)

        output.append('  pop rdi')
        output.append('  pop rax')

        if self.__gen_operation_arithmetic(node, output) or self.__gen_operation_comparison(node, output):
            pass
        else:
            return False

        output.append('  push rax')
        return True

    def __gen_operation_arithmetic(self, node, output):
        map_ = {
            NodeTypes.ADD: ['  add rax, rdi'],
            NodeTypes.SUB: ['  sub rax, rdi'],
            NodeTypes.MUL: ['  imul rdi'],
            NodeTypes.DIV: ['  cqo',
                            '  idiv rdi']
        }
        if node.type in map_:
            output += map_[node.type]
            return True
        return False

    def __gen_operation_comparison(self, node, output):
        map_ = {
            NodeTypes.EQ: ['  cmp rax, rdi',
                           '  sete al'],
            NodeTypes.NE: ['  cmp rax, rdi',
                           '  setne al'],
            NodeTypes.LE: ['  cmp rax, rdi',
                           '  setle al'],
            NodeTypes.GE: ['  cmp rdi, rax',
                           '  setle al'],
            NodeTypes.LT: ['  cmp rax, rdi',
                           '  setl al'],
            NodeTypes.GT: ['  cmp rdi, rax',
                           '  setl al'],
        }
        if node.type in map_:
            output += map_[node.type]
            output.append('  movzb rax, al')
            return True
        return False

    def __gen_lval(self, node, output):
        if node.type != NodeTypes.IDENT:
            error('代入の左辺値が変数ではありません')
        output.append(f'  mov rax, rbp')
        output.append(f'  sub rax, {node.offset}')
        output.append(f'  push rax')
