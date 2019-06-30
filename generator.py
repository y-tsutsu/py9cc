from node_parser import NodeTypes
from utility import error


class Generator:
    def __init__(self, nodes, c_code):
        self.__nodes = nodes
        self.__c_code = c_code

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_prologue()
        gen3 = self.__gen_from_nodes(self.__nodes)
        gen4 = self.__gen_epilogue()
        return gen1 + gen2 + gen3 + gen4

    def __gen_pre(self):
        result = []
        result.append('.intel_syntax noprefix')
        result.append('.global main')
        result.append('main:')
        return result

    def __gen_prologue(self):
        result = []
        result.append('  push rbp')
        result.append('  mov rbp, rsp')
        result.append('  sub rsp, 208')
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
        if self.__gen_num(node, output):
            return

        if self.__gen_address(node, output):
            return

        self.__gen_from_node_inner(node.left, output)
        self.__gen_from_node_inner(node.right, output)

        output.append('  pop rdi')
        output.append('  pop rax')

        _ = self.__gen_arithmetic_operation(node, output)
        _ = self.__gen_comparison_operation(node, output)

        output.append('  push rax')

    def __gen_num(self, node, output):
        if node.type == NodeTypes.NUM:
            output.append(f'  push {node.value}')
        else:
            return False
        return True

    def __gen_address(self, node, output):
        if node.type == NodeTypes.LVAR:
            self.__gen_lval(node, output)
            output.append('  pop rax')
            output.append('  mov rax, [rax]')
            output.append('  push rax')
        elif node.type == NodeTypes.ASSIGN:
            self.__gen_lval(node.left, output)
            self.__gen_from_node_inner(node.right, output)
            output.append('  pop rdi')
            output.append('  pop rax')
            output.append('  mov [rax], rdi')
            output.append('  push rdi')
        else:
            return False
        return True

    def __gen_arithmetic_operation(self, node, output):
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

    def __gen_comparison_operation(self, node, output):
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
        if node.type != NodeTypes.LVAR:
            error('代入の左辺値が変数ではありません')
        output.append(f'  mov rax, rbp')
        output.append(f'  sub rax, {node.offset}')
        output.append(f'  push rax')
