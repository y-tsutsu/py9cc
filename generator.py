from node_parser import NodeTypes
from utility import error


class Generator:
    def __init__(self, node, c_code):
        self.__node = node
        self.__c_code = c_code

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_node(self.__node)
        gen3 = self.__gen_suf()
        return gen1 + gen2 + gen3

    def __gen_pre(self):
        result = []
        result.append('.intel_syntax noprefix')
        result.append('.global main')
        result.append('main:')
        return result

    def __gen_suf(self):
        result = []
        result.append('  pop rax')
        result.append('  ret')
        return result

    def __gen_from_node(self, node):
        result = []
        self.__gen_from_node_inner(node, result)
        return result

    def __gen_from_node_inner(self, node, output):
        if node.type == NodeTypes.ND_NUM:
            output.append(f'  push {node.value}')
            return

        self.__gen_from_node_inner(node.left, output)
        self.__gen_from_node_inner(node.right, output)

        output.append('  pop rdi')
        output.append('  pop rax')

        if node.type == NodeTypes.ND_ADD:
            output.append('  add rax, rdi')
        elif node.type == NodeTypes.ND_SUB:
            output.append('  sub rax, rdi')
        elif node.type == NodeTypes.ND_MUL:
            output.append('  imul rax, rdi')
        elif node.type == NodeTypes.ND_DIV:
            output.append('  cqo')
            output.append('  idiv rdi')
        else:
            error(f'予期せぬノードです {node.type}')

        output.append('  push rax')
