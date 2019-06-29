from tokenizer import TokenTypes
from utility import error_at


def trim_left(c_code, conditions):
    result = ''
    for x in c_code:
        if (conditions(x)):
            result += x
        else:
            break
    return result, c_code[len(result):]


class Generator:
    def __init__(self, tokens, c_code):
        self.__tokens = tokens
        self.__c_code = c_code

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_input(self.__tokens)
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

    def __gen_from_input(self, tokens):
        result = []

        token = tokens[0]
        if token.type == TokenTypes.TK_NUM:
            num = token.value
            result.append(f'  mov rax, {num}')
        else:
            error_at(self.__c_code, token.code, f'{TokenTypes.TK_NUM}ではありません')

        tokens = tokens[1:]
        while tokens:
            token = tokens[0]
            if token.type == TokenTypes.TK_RESERVED:
                map_ = {'+': 'add', '-': 'sub'}
                if token.code[0] in map_:
                    next_token = tokens[1]
                    if next_token.type == TokenTypes.TK_NUM:
                        command = map_[token.code[0]]
                        result.append(f'  {command} rax, {next_token.value}')
                        tokens = tokens[2:]
                    else:
                        error_at(self.__c_code, next_token.code, f'{TokenTypes.TK_NUM}ではありません')
            else:
                error_at(self.__c_code, token.code, f'{TokenTypes.TK_RESERVED}ではありません')

        result.append('  push rax')
        return result
