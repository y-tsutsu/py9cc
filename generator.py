from utility import error


def trim_left(c_code, conditions):
    result = ''
    for x in c_code:
        if (conditions(x)):
            result += x
        else:
            break
    return result, c_code[len(result):]


class Generator:
    def __init__(self, c_code):
        self.__c_code = c_code

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_input(self.__c_code)
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

    def __gen_from_input(self, c_code):
        result = []
        num, c_code = trim_left(c_code, lambda x: x.isdigit())
        result.append(f'  mov rax, {num}')
        while c_code:
            if c_code[0] == '+':
                num, c_code = trim_left(c_code[1:], lambda x: x.isdigit())
                result.append(f'  add rax, {num}')
                continue
            if c_code[0] == '-':
                num, c_code = trim_left(c_code[1:], lambda x: x.isdigit())
                result.append(f'  sub rax, {num}')
                continue
            else:
                error(f'予期しない文字です: {c_code[0]}')
        result.append('  push rax')
        return result
