from node_parser import NodeTypes


class Generator:
    def __init__(self, nodes, c_code):
        self.__nodes = nodes
        self.__c_code = c_code

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_node(self.__nodes)
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

    def __gen_from_node(self, nodes):
        result = []
        for x in nodes:
            self.__gen_from_node_inner(x, result)
        return result

    def __gen_from_node_inner(self, node, output):
        if node.type == NodeTypes.NUM:
            output.append(f'  push {node.value}')
            return

        self.__gen_from_node_inner(node.left, output)
        self.__gen_from_node_inner(node.right, output)

        output.append('  pop rdi')
        output.append('  pop rax')

        map_ = {
            NodeTypes.ADD: ['  add rax, rdi'],
            NodeTypes.SUB: ['  sub rax, rdi'],
            NodeTypes.MUL: ['  imul rdi'],
            NodeTypes.DIV: ['  cqo',
                            '  idiv rdi']
        }
        if node.type in map_:
            output += map_[node.type]

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

        output.append('  push rax')
