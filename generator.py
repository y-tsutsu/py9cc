from abc import ABCMeta, abstractmethod

from utility import error


class NodeGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, node):
        pass

    def _gen_lval(self, node, output):
        from node import NodeTypes

        if node.type != NodeTypes.IDENT:
            error('代入の左辺値が変数ではありません')
        output.append(f'  mov rax, rbp')
        output.append(f'  sub rax, {node.offset}')
        output.append(f'  push rax')


class NumGenerator(NodeGenerator):
    def generate(self, node, output):
        output.append(f'  push {node.value}')


class OperatorGenerator(NodeGenerator):
    def __gen_arithmetic(self, node, output):
        from node import NodeTypes

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

    def __gen_comparison(self, node, output):
        from node import NodeTypes

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

    def generate(self, node, output):
        node.left.generate(output)
        node.right.generate(output)

        output.append('  pop rdi')
        output.append('  pop rax')

        self.__gen_arithmetic(node, output)
        self.__gen_comparison(node, output)

        output.append('  push rax')
        return True


class AssignGenerator(NodeGenerator):
    def generate(self, node, output):
        self._gen_lval(node.left, output)
        node.right.generate(output)
        output.append('  pop rdi')
        output.append('  pop rax')
        output.append('  mov [rax], rdi')
        output.append('  push rdi')


class IdentGenerator(NodeGenerator):
    def generate(self, node, output):
        self._gen_lval(node, output)
        output.append('  pop rax')
        output.append('  mov rax, [rax]')
        output.append('  push rax')


class ReturnGenerator(NodeGenerator):
    def generate(self, node, output):
        node.child.generate(output)
        output.append('  pop rax')
        output.append('  mov rsp, rbp')
        output.append('  pop rbp')
        output.append('  ret')


class IfGenerator(NodeGenerator):
    def generate(self, node, output):
        node.expr.generate(output)
        output.append(f'  pop rax')
        output.append(f'  cmp rax, 0')
        output.append(f'  je  .Lend{id(node)}')
        node.stmt.generate(output)
        output.append(f'.Lend{id(node)}:')


class IfElseGenerator(NodeGenerator):
    def generate(self, node, output):
        node.expr.generate(output)
        output.append(f'  pop rax')
        output.append(f'  cmp rax, 0')
        output.append(f'  je  .Lelse{id(node)}')
        node.stmt.generate(output)
        output.append(f'  jmp .Lend{id(node)}')
        output.append(f'.Lelse{id(node)}:')
        node.else_stmt.generate(output)
        output.append(f'.Lend{id(node)}:')


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

    def __gen_from_nodes(self, nodes):
        result = []
        for node in nodes:
            node.generate(result)
            # result.append('  pop rax')
        return result

    def __gen_epilogue(self):
        result = []
        result.append('  mov rsp, rbp')
        result.append('  pop rbp')
        result.append('  ret')
        return result
