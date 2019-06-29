from enum import Enum, auto

from utility import error


class TokenTypes(Enum):
    TK_RESERVED = auto()
    TK_NUM = auto()


class Token:
    def __init__(self):
        self.type = None
        self.value = None
        self.code = None


class Tokenizer:
    def __init__(self, c_code):
        self.__c_code = c_code

    def __trim_left(self, c_code, conditions):
        result = ''
        for x in c_code:
            if (conditions(x)):
                result += x
            else:
                break
        return result, c_code[len(result):]

    def __trim_left_num(self, c_code):
        return self.__trim_left(c_code, lambda x: x.isdigit())

    def __create_new_token(self, t_type, c_code):
        token = Token()
        token.type = t_type
        token.code = c_code
        return token

    def __create_new_num_token(self, c_code):
        token = self.__create_new_token(TokenTypes.TK_NUM, c_code)
        token.value, _ = self.__trim_left_num(c_code)
        return token

    def tokenize(self):
        result = []

        c_code = self.__c_code
        while c_code:
            c = c_code[0]

            if c.isspace():
                c_code = c_code[1:]
                continue

            if c in ('+', '-'):
                token = self.__create_new_token(TokenTypes.TK_RESERVED, c_code)
                result.append(token)
                c_code = c_code[1:]
                continue

            if c.isdigit():
                token = self.__create_new_token(TokenTypes.TK_NUM, c_code)
                token.value, c_code = self.__trim_left_num(c_code)
                result.append(token)
                continue

            error('トークナイズできません')

        return result
