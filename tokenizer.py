from collections import deque
from enum import Enum, auto

from utility import error_at, error


class TokenTypes(Enum):
    TK_RESERVED = auto()
    TK_NUM = auto()


class Token:
    def __init__(self):
        self.type = None
        self.value = None
        self.code = None


class TokenResult:
    def __init__(self, tokens, c_code):
        self.__tokens = deque(tokens)
        self.__c_code = c_code

    def is_empty(self):
        return len(self.__tokens) == 0

    def consume(self, op):
        if not self.__tokens:
            error('トークンが残っていません')
        token = self.__tokens[0]
        if token.type == TokenTypes.TK_RESERVED and token.code[0] == op:
            token = self.__tokens.popleft()
            return token
        return None

    def consume_num(self):
        if not self.__tokens:
            error('トークンが残っていません')
        token = self.__tokens[0]
        if token.type == TokenTypes.TK_NUM:
            token = self.__tokens.popleft()
            return token
        return None

    def expect(self, op):
        token = self.consume(op)
        if not token:
            error_at(self.__c_code, self.__tokens[0].code, f'{op}ではありません')
        return token

    def expect_num(self):
        token = self.consume_num()
        if not token:
            error_at(self.__c_code, self.__tokens[0].code, '数ではありません')
        return token


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
        tokens = []

        c_code = self.__c_code
        while c_code:
            c = c_code[0]

            if c.isspace():
                c_code = c_code[1:]
                continue

            if c in ('+', '-'):
                token = self.__create_new_token(TokenTypes.TK_RESERVED, c_code)
                tokens.append(token)
                c_code = c_code[1:]
                continue

            if c.isdigit():
                token = self.__create_new_token(TokenTypes.TK_NUM, c_code)
                token.value, c_code = self.__trim_left_num(c_code)
                tokens.append(token)
                continue

            error_at(self.__c_code, c_code, 'トークナイズできません')

        return TokenResult(tokens, self.__c_code)
