from sys import stderr


def error(message):
    print(message, file=stderr)
    exit(1)
