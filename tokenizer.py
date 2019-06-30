from collections import deque
from enum import Enum, auto
from string import ascii_letters, digits

from utility import error, error_at


class TokenTypes(Enum):
    RESERVED = auto()
    RETURN = auto()
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

    def __consume_inner(self, t_type):
        if self.__tokens:
            if self.__tokens[0].type == t_type:
                token = self.__tokens.popleft()
                return token
        return None

    def consume_num(self):
        return self.__consume_inner(TokenTypes.NUM)

    def consume_ident(self):
        return self.__consume_inner(TokenTypes.IDENT)

    def consume_return(self):
        return self.__consume_inner(TokenTypes.RETURN)

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
    __var_name_head = ascii_letters + '_'
    __var_name = digits + __var_name_head

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

    def __trim_left_varname(self, c_code):
        return self.__trim_left(c_code, lambda x: x in Tokenizer.__var_name)

    def __create_new_token(self, t_type, c_code, length):
        token = Token()
        token.type = t_type
        token.code = c_code
        token.length = length
        return token

    def __create_new_num_token(self, c_code):
        num, _ = self.__trim_left_num(c_code)
        token = self.__create_new_token(TokenTypes.NUM, c_code, len(num))
        token.value = num
        return token

    def __create_new_varname_token(self, c_code):
        name, _ = self.__trim_left_varname(c_code)
        token = self.__create_new_token(TokenTypes.IDENT, c_code, len(name))
        return token

    def __create_new_reserved_token(self, c_code, reserved):
        map_ = {'return': TokenTypes.RETURN}
        if reserved not in map_:
            error(f'不正な予約語です {reserved}')
        token = self.__create_new_token(map_[reserved], c_code, len(reserved))
        return token

    def __is_reserved_token(self, c_code, reserved):
        rlen = len(reserved)
        return (reserved == c_code[:rlen]) and (c_code[rlen] not in Tokenizer.__var_name)

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

            if self.__is_reserved_token(c_code, 'return'):
                token = self.__create_new_reserved_token(c_code, 'return')
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            if c in Tokenizer.__var_name_head:
                token = self.__create_new_varname_token(c_code)
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
