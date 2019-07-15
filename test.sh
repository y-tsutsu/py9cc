#!/bin/bash
try() {
    expected="$1"
    input="$2"

    gcc -c sample.c

    python py9cc.py "$input" > tmp.s

    if [ "$?" != "0" ]; then
        echo "py9cc.py error"
        exit 1
    fi

    gcc -o tmp tmp.s sample.o

    if [ "$?" != "0" ]; then
        echo "gcc compile error"
        exit 1
    fi

    ./tmp
    actual="$?"

    if [ "$actual" = "$expected" ]; then
        echo "$input => $actual"
    else
        echo "$input => $expected expected, but got $actual"
        echo "NG"
        exit 1
    fi

    rm tmp.s tmp sample.o
}

try 0 "int main() { return 0; }"
try 42 "int main() { return 42; }"
try 21 "int main() { return 5+20-4; }"
try 41 "int main() { return  12 + 34 - 5 ; }"
try 47 "int main() { return 5+6*7; }"
try 15 "int main() { return 5*(9-6); }"
try 4 "int main() { return (3+5)/2; }"
try 10 "int main() { return -10+20; }"
try 42 "int main() { return +1*42; }"
try 0 "int main() { return 1+(-1); }"
try 3 "int main() { return 1++2; }"
try 1 "int main() { return 42==42; }"
try 0 "int main() { return 42==23; }"
try 1 "int main() { return 42!=23; }"
try 0 "int main() { return 42!=42; }"
try 1 "int main() { return 42<=43; }"
try 1 "int main() { return 42<=42; }"
try 0 "int main() { return 42<=41; }"
try 1 "int main() { return 42<43; }"
try 0 "int main() { return 42<42; }"
try 0 "int main() { return 42<41; }"
try 1 "int main() { return 43>=42; }"
try 1 "int main() { return 42>=42; }"
try 0 "int main() { return 41>=42; }"
try 1 "int main() { return 43>42; }"
try 0 "int main() { return 42>42; }"
try 0 "int main() { return 41>42; }"
try 14 "int main() { int a; a = 3; int b; b = 5 * 6 - 8; return a + b / 2; }"
try 6 "int main() { int Foo; int Bar; Foo = 1; Bar = 2 + 3; return Foo + Bar; }"
try 130 "int main() { int hoge; hoge = 42; int piyo; piyo = hoge + 23; int fuga; fuga = piyo * 2; return fuga; }"
try 6 "int main() { int x; x = 2; if (x == 2) x = x * 3; return x; }"
try 2 "int main() { int x; x = 2; if (x == 1) x = x * 3; return x; }"
try 24 "int main() { int x; int y; int z; x = 2; y = 0; z = 0; if (x == 2) y = x * 3; if (y > 0) z = y * 4; return z; }"
try 6 "int main() { int x; int y; x = 2; y = 0; if (x == 2) y = x * 3; else y = x * 4; return y; }"
try 8 "int main() { int x; int y; x = 2; y = 0; if (x == 1) y = x * 3; else y = x * 4; return y; }"
try 10 "int main() { int x; x = 0; while (x != 10) x = x + 1; return x; }"
try 0 "int main() { int x; x = 0; while (x != 0) x = x + 1; return x; }"
try 20 "int main() { int x; x = 0; int i; for (i = 0; i < 10; i = i + 1) x = x + 2; return x; }"
try 15 "int main() { int x; x = 5; int i; i = 0; for (; i < 10; i = i + 1) x = x + 1; return x; }"
try 55 "int main() { int x; int y; x = 0; y = 10; int i; for (i = 0; i < 5; i = i + 1) { x = x + 1; y = y + 1; } return 2 * x + 3 * y; }"
try 42 "int main() { int x; x = 42; MyPrint(); return x; }"
try 21 "int main() { int v1; int v2; int v3; int v4; int v5; int v6; v1 = 1; v2 = 2; v3 = 3; v4 = 4; v5 = 5; v6 = 6; int ans; ans = MyAdd(v1, v2, v3, v4, v5, v6); return ans; }"
try 4 "int main() { int v1; v1 = 8; int v2; v2 = 2; int ans; ans = MyDiv(v1, v2); return ans; }"
try 0 "int main() { int x; x = 50000000; int i; for (i = 0; i < 50000000; i = i + 1) x = x - 1; return x; }"
try 0 "int main() { int x; x = 50000000; int i; for (i = 50000000; i > 0; i = i - 1) x = x - 1; return x; }"
try 0 "int main() { int x; x = 50000000; while (x > 0) x = x - 1; return x; }"
try 0 "int main() { int x; x = 50000000; int i; for (i = 0; i < 50000000; i = i + 1) { x = x - 2; x = x + 1; } return x; }"
try 0 "int main() { int x; x = 50000000; int i; for (i = 50000000; i > 0; i = i - 1) { x = x - 2; x = x + 1; } return x; }"
try 0 "int main() { int x; x = 50000000; while (x > 0) { x = x - 2; x = x + 1; } return x; }"
try 255 "int main() { int x; x = 50000000; while (x > 0) { x = x - 1; if (x == 255) { return x; } } return x; }"
try 21 "int my_add(int v1, int v2, int v3, int v4, int v5, int v6) { int ans; ans = v1 + v2 + v3 + v4 + v5 + v6; return ans; } int main() { int x1; int x2; int x3; int x4; int x5; int x6; x1 = 1; x2 = 2; x3 = 3; x4 = 4; x5 = 5; x6 = 6; int ans; ans = my_add(x1, x2, x3, x4, x5, x6); return ans; }"
try 4 "int my_div(int v1, int v2) { int ans; ans = v1 / v2; return ans; } int main() { int v1; v1 = 8; int v2; v2 = 2; int ans; ans = my_div(v1, v2); return ans; }"
try 0 "int fib_(int max, int left, int right) { if (max < left) { return 0; } MyPrintNum(left); int tmp; tmp = left; left = right; right = tmp + right; fib_(max, left, right); return 0; } int fib(int max) { fib_(max, 0, 1); return 0; } int main() { fib(1000); return 0; }"
try 3 "int main() { int x; x = 3; int y; y = &x; return *y; }"
try 3 "int main() { int x; x = 3; int y; y = 5; int z; z = &y + 8; return *z; }"
try 100 "int foo(int num) { int i; int j; j = 0; for (i = num; i > 0; i = i - 1) { if (i == 100) { return 253; } if (i = 1) { while (j < 100) { j = j + 2; if (j == 255) { return 252; } } return j; } } return 251; } int main() { int i; int j; j = 0; for (i = 1; i < 100; i = i + 1) { if (i == 0) { return 255; } if (i == 99) { return foo(i); } else { j = j + 1; if (j == 99) { return 254; } } } return 0; }"

# try 0 "int main() { for (i = 0; ;) { MyPrint(); } return 0; }"

echo "OK"
