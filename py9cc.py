from sys import argv

from generator import Generator
from utility import error


def main():
    if len(argv) != 2:
        error(f'引数の個数が正しくありません {argv}')

    c_code = argv[1]
    generator = Generator(c_code)
    assembly = generator.generate()

    for x in assembly:
        print(x)


if __name__ == '__main__':
    main()
