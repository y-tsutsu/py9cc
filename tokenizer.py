from collections import deque
from enum import Enum, auto
from string import ascii_letters, digits

from utility import error, error_at


class TokenTypes(Enum):
    SYMBOL = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
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

    def consume_if(self):
        return self.__consume_inner(TokenTypes.IF)

    def consume_else(self):
        return self.__consume_inner(TokenTypes.ELSE)

    def consume_while(self):
        return self.__consume_inner(TokenTypes.WHILE)

    def consume_for(self):
        return self.__consume_inner(TokenTypes.FOR)

    def consume_symbol(self, symbol):
        if self.__tokens:
            tk = self.__tokens[0]
            if tk.type == TokenTypes.SYMBOL and tk.code[: tk.length] == symbol:
                token = self.__tokens.popleft()
                return token
        return None

    def expect_num(self):
        token = self.consume_num()
        if not token:
            if self.__tokens:
                error_at(self.__c_code, self.__tokens[0].code, '数ではありません')
            else:
                error('数がありません')
        return token

    def expect_symbol(self, symbol):
        token = self.consume_symbol(symbol)
        if not token:
            if self.__tokens:
                error_at(self.__c_code, self.__tokens[0].code, f'{symbol}ではありません')
            else:
                error(f'{symbol}がありません')
        return token


class Tokenizer:
    __symbols = ('==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '(', ')', ';', '=', '{', '}')
    __reserved_map = {'return': TokenTypes.RETURN, 'if': TokenTypes.IF, 'else': TokenTypes.ELSE, 'while': TokenTypes.WHILE, 'for': TokenTypes.FOR}
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

    def __create_token(self, t_type, c_code, length):
        token = Token()
        token.type = t_type
        token.code = c_code
        token.length = length
        return token

    def __create_num_token(self, c_code):
        num, _ = self.__trim_left_num(c_code)
        token = self.__create_token(TokenTypes.NUM, c_code, len(num))
        token.value = num
        return token

    def __create_varname_token(self, c_code):
        name, _ = self.__trim_left_varname(c_code)
        token = self.__create_token(TokenTypes.IDENT, c_code, len(name))
        return token

    def __create_reserved_token(self, c_code, reserved):
        if reserved not in Tokenizer.__reserved_map:
            error(f'不正な予約語です {reserved}')
        token = self.__create_token(Tokenizer.__reserved_map[reserved], c_code, len(reserved))
        return token

    def __startswith_reserved(self, c_code):
        for reserved in Tokenizer.__reserved_map:
            if (c_code.startswith(reserved)) and (c_code[len(reserved)] not in Tokenizer.__var_name):
                return reserved
        return None

    def tokenize(self):
        tokens = []

        c_code = self.__c_code
        while c_code:
            c = c_code[0]

            if c.isspace():
                c_code = c_code[1:]
                continue

            if c.isdigit():
                token = self.__create_num_token(c_code)
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            reserved = self.__startswith_reserved(c_code)
            if reserved:
                token = self.__create_reserved_token(c_code, reserved)
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            if c in Tokenizer.__var_name_head:
                token = self.__create_varname_token(c_code)
                tokens.append(token)
                c_code = c_code[token.length:]
                continue

            cc = c_code[: 2]
            for x in (cc, c):
                if x in Tokenizer.__symbols:
                    token = self.__create_token(TokenTypes.SYMBOL, c_code, len(x))
                    tokens.append(token)
                    c_code = c_code[token.length:]
                    break
            else:
                error_at(self.__c_code, c_code, 'トークナイズできません')

        return TokenResult(tokens, self.__c_code)
