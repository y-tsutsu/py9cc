from collections import deque
from enum import Enum, auto
from string import ascii_lowercase

from utility import error, error_at


class TokenTypes(Enum):
    RESERVED = auto()
    IDENT = auto()
    NUM = auto()


class Token:
    def __init__(self):
        self.type = None
        self.value = None
        self.code = None
        self.length = None


class TokenResult:
    def __init__(self, tokens, c_code):
        self.__tokens = deque(tokens)
        self.__c_code = c_code

    def is_empty(self):
        return len(self.__tokens) == 0

    def consume(self, op):
        if self.__tokens:
            tk = self.__tokens[0]
            if tk.type == TokenTypes.RESERVED and tk.code[: tk.length] == op:
                token = self.__tokens.popleft()
                return token
        return None

    def consume_num(self):
        if self.__tokens:
            if self.__tokens[0].type == TokenTypes.NUM:
                token = self.__tokens.popleft()
                return token
        return None

    def consume_ident(self):
        if self.__tokens:
            if self.__tokens[0].type == TokenTypes.IDENT:
                token = self.__tokens.popleft()
                return token
        return None

    def expect(self, op):
        token = self.consume(op)
        if not token:
            if self.__tokens:
                error_at(self.__c_code, self.__tokens[0].code, f'{op}ではありません')
            else:
                error(f'{op}がありません')
        return token

    def expect_num(self):
        token = self.consume_num()
        if not token:
            if self.__tokens:
                error_at(self.__c_code, self.__tokens[0].code, '数ではありません')
            else:
                error('数がありません')
        return token


class Tokenizer:
    __symbols = ('==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '(', ')', ';', '=')

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

    def __create_new_token(self, t_type, c_code, length):
        token = Token()
        token.type = t_type
        token.code = c_code
        token.length = length
        return token

    def __create_new_num_token(self, c_code):
        token = self.__create_new_token(TokenTypes.NUM, c_code, 0)
        token.value, _ = self.__trim_left_num(c_code)
        token.length = len(token.value)
        return token

    def tokenize(self):
        tokens = []

        c_code = self.__c_code
        while c_code:
            c = c_code[0]

            if c.isspace():
                c_code = c_code[1:]
                continue

            if c.isdigit():
                token = self.__create_new_num_token(c_code)
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            if c in ascii_lowercase:
                token = self.__create_new_token(TokenTypes.IDENT, c_code, len(c))
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            cc = c_code[: 2]
            for x in (cc, c):
                if x in Tokenizer.__symbols:
                    token = self.__create_new_token(TokenTypes.RESERVED, c_code, len(x))
                    tokens.append(token)
                    c_code = c_code[token.length:]
                    break
            else:
                error_at(self.__c_code, c_code, 'トークナイズできません')

        return TokenResult(tokens, self.__c_code)
