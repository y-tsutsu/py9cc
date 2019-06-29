from sys import argv

from generator import Generator
from utility import error


def main():
    if len(argv) != 2:
        error(f'引数の個数が正しくありません {argv}')
        exit(1)

    user_input = argv[1]

    generator = Generator(int(user_input))
    assembly = generator.generate()

    for x in assembly:
        print(x)


if __name__ == '__main__':
    main()
