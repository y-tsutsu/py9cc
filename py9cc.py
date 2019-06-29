from sys import argv

from generator import Generator
from node_parser import Parser
from tokenizer import Tokenizer
from utility import error


def main():
    if len(argv) != 2:
        error(f'引数の個数が正しくありません {argv}')

    c_code = argv[1]

    tokenizer = Tokenizer(c_code)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens)
    node = parser.parse()

    generator = Generator(node, c_code)
    assembly = generator.generate()

    for x in assembly:
        print(x)


if __name__ == '__main__':
    main()
