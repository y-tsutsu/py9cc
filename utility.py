from sys import stderr


def error(message):
    print(message, file=stderr)
    exit(1)


def error_at(c_code, error_c_code, message):
    pos = len(c_code) - len(error_c_code)
    print(f'{c_code}', file=stderr)
    print(' ' * pos, end='', file=stderr)
    print(f'^ {message}', file=stderr)
    exit(1)
