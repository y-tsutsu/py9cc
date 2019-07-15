from abc import ABCMeta, abstractmethod

from utility import error


class NodeGenerator(metaclass=ABCMeta):
    REG_ARGS = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

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

    def _append_missing_pop(self, output):
        push_count = len([x for x in output if x.lstrip().startswith('push') and not x.rstrip().endswith('rbp')])
        pop_count = len([x for x in output if x.lstrip().startswith('pop') and not x.rstrip().endswith('rbp')])
        if (push_count - pop_count) == 0:
            pass
        elif (push_count - pop_count) == 1:
            output.append('  pop rax')
        elif (push_count - pop_count) > 1:
            error(f'pushが多すぎます push: {push_count} pop: {pop_count}')
        else:
            error(f'popが多すぎます push: {push_count} pop: {pop_count}')


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
        if node.expr:
            node.expr.generate(output)
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
        self._append_missing_pop(output)
        output.append(f'.Lend{id(node)}:')


class IfElseGenerator(NodeGenerator):
    def generate(self, node, output):
        node.expr.generate(output)
        output.append(f'  pop rax')
        output.append(f'  cmp rax, 0')
        output.append(f'  je  .Lelse{id(node)}')
        node.stmt.generate(output)
        self._append_missing_pop(output)
        output.append(f'  jmp .Lend{id(node)}')
        output.append(f'.Lelse{id(node)}:')
        node.else_stmt.generate(output)
        self._append_missing_pop(output)
        output.append(f'.Lend{id(node)}:')


class WhileGenerator(NodeGenerator):
    def generate(self, node, output):
        output.append(f'.Lbegin{id(node)}:')
        node.expr.generate(output)
        output.append(f'  pop rax')
        output.append(f'  cmp rax, 0')
        output.append(f'  je  .Lend{id(node)}')
        node.stmt.generate(output)
        self._append_missing_pop(output)
        output.append(f'  jmp .Lbegin{id(node)}')
        output.append(f'.Lend{id(node)}:')


class ForGenerator(NodeGenerator):
    def generate(self, node, output):
        if node.expr1:
            node.expr1.generate(output)
            self._append_missing_pop(output)
        output.append(f'.Lbegin{id(node)}:')
        node.expr2.generate(output)
        output.append(f'  pop rax')
        output.append(f'  cmp rax, 0')
        output.append(f'  je  .Lend{id(node)}')
        node.stmt.generate(output)
        self._append_missing_pop(output)
        if node.expr3:
            node.expr3.generate(output)
            self._append_missing_pop(output)
        output.append(f'  jmp .Lbegin{id(node)}')
        output.append(f'.Lend{id(node)}:')


class BlockGenerator(NodeGenerator):
    def generate(self, node, output):
        for stmt in node.stmts:
            stmt.generate(output)
            self._append_missing_pop(output)


class CallGenerator(NodeGenerator):
    def generate(self, node, output):
        if len(NodeGenerator.REG_ARGS) < len(node.args):
            error(f'引数が多すぎます {node.args}')

        for arg, reg in zip(node.args, CallGenerator.REG_ARGS):
            arg.generate(output)
            output.append(f'  pop {reg}')

        output.append(f'  push  r15')
        output.append(f'  xor   r15, r15')
        output.append(f'  test  rsp, 0xf')
        output.append(f'  setnz r15b')
        output.append(f'  shl   r15, 3')
        output.append(f'  sub   rsp, r15')
        output.append(f'  call  {node.name}')
        output.append(f'  add   rsp, r15')
        output.append(f'  pop   r15')
        output.append(f'  push  rax')


class FuncGenerator(NodeGenerator):
    def generate(self, node, output):
        if len(NodeGenerator.REG_ARGS) < len(node.arg_offsets):
            error(f'引数が多すぎます {node.args}')

        output.append(f'{node.name}:')

        output.append(f'  push rbp')
        output.append(f'  mov rbp, rsp')
        output.append(f'  sub rsp, {node.varsize}')

        for offset, reg in zip(node.arg_offsets, CallGenerator.REG_ARGS):
            output.append(f'  mov rax, rbp')
            output.append(f'  sub rax, {offset}')
            output.append(f'  mov [rax], {reg}')

        node.block.generate(output)

        if not output[-1].lstrip().startswith('ret'):
            output.append(f'  mov rsp, rbp')
            output.append(f'  pop rbp')
            output.append(f'  ret')


class AddressGenerator(NodeGenerator):
    def generate(self, node, output):
        self._gen_lval(node.unary, output)


class DereferenceGenerator(NodeGenerator):
    def generate(self, node, output):
        node.unary.generate(output)
        output.append('  pop rax')
        output.append('  mov rax, [rax]')
        output.append('  push rax')


class Generator:
    def __init__(self, node_context):
        self.__ncontext = node_context

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_nodes(self.__ncontext)
        return gen1 + gen2

    def __gen_pre(self):
        result = []
        result.append('.intel_syntax noprefix')
        result.append('.global main')
        return result

    def __gen_from_nodes(self, ncontext):
        result = []
        for node in ncontext.nodes:
            output = []
            node.generate(output)
            result += output
        return result
