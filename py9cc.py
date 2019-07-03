from sys import argv

from generator import Generator
from node import Parser
from tokenizer import Tokenizer
from utility import error


def main():
    if len(argv) != 2:
        error(f'引数の個数が正しくありません {argv}')

    c_code = argv[1]

    tokenizer = Tokenizer(c_code)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens)
    nodes = parser.parse()

    generator = Generator(nodes, c_code, parser.varsize)
    assembly = generator.generate()

    for x in assembly:
        print(x)


if __name__ == '__main__':
    main()
