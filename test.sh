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

try 0 "main() { return 0; }"
try 42 "main() { return 42; }"
try 21 "main() { return 5+20-4; }"
try 41 "main() { return  12 + 34 - 5 ; }"
try 47 "main() { return 5+6*7; }"
try 15 "main() { return 5*(9-6); }"
try 4 "main() { return (3+5)/2; }"
try 10 "main() { return -10+20; }"
try 42 "main() { return +1*42; }"
try 0 "main() { return 1+(-1); }"
try 3 "main() { return 1++2; }"
try 1 "main() { return 42==42; }"
try 0 "main() { return 42==23; }"
try 1 "main() { return 42!=23; }"
try 0 "main() { return 42!=42; }"
try 1 "main() { return 42<=43; }"
try 1 "main() { return 42<=42; }"
try 0 "main() { return 42<=41; }"
try 1 "main() { return 42<43; }"
try 0 "main() { return 42<42; }"
try 0 "main() { return 42<41; }"
try 1 "main() { return 43>=42; }"
try 1 "main() { return 42>=42; }"
try 0 "main() { return 41>=42; }"
try 1 "main() { return 43>42; }"
try 0 "main() { return 42>42; }"
try 0 "main() { return 41>42; }"
try 14 "main() { a = 3; b = 5 * 6 - 8; return a + b / 2; }"
try 6 "main() { Foo = 1; Bar = 2 + 3; return Foo + Bar; }"
try 130 "main() { hoge = 42; piyo = hoge + 23; fuga = piyo * 2; return fuga; }"
try 6 "main() { x = 2; if (x == 2) x = x * 3; return x; }"
try 2 "main() { x = 2; if (x == 1) x = x * 3; return x; }"
try 24 "main() { x = 2; y = 0; z = 0; if (x == 2) y = x * 3; if (y > 0) z = y * 4; return z; }"
try 6 "main() { x = 2; y = 0; if (x == 2) y = x * 3; else y = x * 4; return y; }"
try 8 "main() { x = 2; y = 0; if (x == 1) y = x * 3; else y = x * 4; return y; }"
try 10 "main() { x = 0; while (x != 10) x = x + 1; return x; }"
try 0 "main() { x = 0; while (x != 0) x = x + 1; return x; }"
try 20 "main() { x = 0; for (i = 0; i < 10; i = i + 1) x = x + 2; return x; }"
try 5 "main() { x = 5; for (; i < 10; i = i + 1) x = x + 1; return x; }"
try 55 "main() { x = 0; y = 10; for (i = 0; i < 5; i = i + 1) { x = x + 1; y = y + 1; } return 2 * x + 3 * y; }"
try 42 "main() { x = 42; MyPrint(); return x; }"
try 21 "main() { v1 = 1; v2 = 2; v3 = 3; v4 = 4; v5 = 5; v6 = 6; ans = MyAdd(v1, v2, v3, v4, v5, v6); return ans; }"
try 4 "main() { v1 = 8; v2 = 2; ans = MyDiv(v1, v2); return ans; }"
try 0 "main() { x = 50000000; for (i = 0; i < 50000000; i = i + 1) x = x - 1; return x; }"
try 0 "main() { x = 50000000; for (i = 50000000; i > 0; i = i - 1) x = x - 1; return x; }"
try 0 "main() { x = 50000000; while (x > 0) x = x - 1; return x; }"
try 0 "main() { x = 50000000; for (i = 0; i < 50000000; i = i + 1) { x = x - 2; x = x + 1; } return x; }"
try 0 "main() { x = 50000000; for (i = 50000000; i > 0; i = i - 1) { x = x - 2; x = x + 1; } return x; }"
try 0 "main() { x = 50000000; while (x > 0) { x = x - 2; x = x + 1; } return x; }"
try 255 "main() { x = 50000000; while (x > 0) { x = x - 1; if (x == 255) { return x; } } return x; }"
try 21 "my_add(v1, v2, v3, v4, v5, v6) { ans = v1 + v2 + v3 + v4 + v5 + v6; return ans; } main() { x1 = 1; x2 = 2; x3 = 3; x4 = 4; x5 = 5; x6 = 6; ans = my_add(x1, x2, x3, x4, x5, x6); return ans; }"
try 4 "my_div(v1, v2) { ans = v1 / v2; return ans; } main() { v1 = 8; v2 = 2; ans = my_div(v1, v2); return ans; }"
try 0 "fib_(max, left, right) { if (max < left) { return; } MyPrintNum(left); tmp = left; left = right; right = tmp + right; fib_(max, left, right); } fib(max) { fib_(max, 0, 1); } main() { fib(1000); return 0; }"
try 3 "main() { x = 3; y = &x; return *y; }"
try 3 "main() { x = 3; y = 5; z = &y + 8; return *z; }"

# try 0 "main() { for (i = 0; ;) { MyPrint(); } return 0; }"

echo "OK"
