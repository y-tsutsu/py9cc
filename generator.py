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

        if node.type == NodeTypes.ND_NUM:
            print(f'  push {node.value}')
            return

        self.__gen_from_node(node.left)
        self.__gen_from_node(node.right)

        print('  pop rdi')
        print('  pop rax')

        if node.type == NodeTypes.ND_ADD:
            result.append('  add rax, rdi')
        elif node.type == NodeTypes.ND_SUB:
            result.append('  sub rax, rdi')
        elif node.type == NodeTypes.ND_MUL:
            result.append('  imul rax, rdi')
        elif node.type == NodeTypes.ND_DIV:
            result.append('  cqo')
            result.append('  idiv rdi')
        else:
            error(f'予期せぬノードです {node.type}')

        result.append('  push rax')
        return result
