class Generator:
    def __init__(self, num):
        self.__num = num

    def generate(self):
        gen1 = self.__gen_pre()
        gen2 = self.__gen_from_input(self.__num)
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

    def __gen_from_input(self, num):
        result = []
        result.append(f'  push {num}')
        return result
