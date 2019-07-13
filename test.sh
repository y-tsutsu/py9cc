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

try 0 "return 0;"
try 42 "return 42;"
try 21 "return 5+20-4;"
try 41 "return  12 + 34 - 5 ;"
try 47 "return 5+6*7;"
try 15 "return 5*(9-6);"
try 4 "return (3+5)/2;"
try 10 "return -10+20;"
try 42 "return +1*42;"
try 0 "return 1+(-1);"
try 3 "return 1++2;"
try 1 "return 42==42;"
try 0 "return 42==23;"
try 1 "return 42!=23;"
try 0 "return 42!=42;"
try 1 "return 42<=43;"
try 1 "return 42<=42;"
try 0 "return 42<=41;"
try 1 "return 42<43;"
try 0 "return 42<42;"
try 0 "return 42<41;"
try 1 "return 43>=42;"
try 1 "return 42>=42;"
try 0 "return 41>=42;"
try 1 "return 43>42;"
try 0 "return 42>42;"
try 0 "return 41>42;"
try 14 "a = 3; b = 5 * 6 - 8; return a + b / 2;"
try 6 "Foo = 1; Bar = 2 + 3; return Foo + Bar;"
try 130 "hoge = 42; piyo = hoge + 23; fuga = piyo * 2; return fuga;"
try 6 "x = 2; if (x == 2) x = x * 3; return x;"
try 2 "x = 2; if (x == 1) x = x * 3; return x;"
try 24 "x = 2; y = 0; z = 0; if (x == 2) y = x * 3; if (y > 0) z = y * 4; return z;"
try 6 "x = 2; y = 0; if (x == 2) y = x * 3; else y = x * 4; return y;"
try 8 "x = 2; y = 0; if (x == 1) y = x * 3; else y = x * 4; return y;"
try 10 "x = 0; while (x != 10) x = x + 1; return x;"
try 0 "x = 0; while (x != 0) x = x + 1; return x;"
try 20 "x = 0; for (i = 0; i < 10; i = i + 1) x = x + 2; return x;"
try 5 "x = 5; for (; i < 10; i = i + 1) x = x + 1; return x;"
try 55 "x = 0; y = 10; for (i = 0; i < 5; i = i + 1) { x = x + 1; y = y + 1; } return 2 * x + 3 * y;"
try 42 "x = 42; MyPrint(); return x;"
try 21 "v1 = 1; v2 = 2; v3 = 3; v4 = 4; v5 = 5; v6 = 6; ans = MyAdd(v1, v2, v3, v4, v5, v6); return ans;"
try 4 "v1 = 8; v2 = 2; ans = MyDiv(v1, v2); return ans;"
try 0 "x = 50000000; for (i = 0; i < 50000000; i = i + 1) x = x - 1; return x;"
try 0 "x = 50000000; for (i = 50000000; i > 0; i = i - 1) x = x - 1; return x;"
try 0 "x = 50000000; while (x > 0) x = x - 1; return x;"
try 0 "x = 50000000; for (i = 0; i < 50000000; i = i + 1) { x = x - 2; x = x + 1; } return x;"
try 0 "x = 50000000; for (i = 50000000; i > 0; i = i - 1) { x = x - 2; x = x + 1; } return x;"
try 0 "x = 50000000; while (x > 0) { x = x - 2; x = x + 1; } return x;"
try 255 "x = 50000000; while (x > 0) { x = x - 1; if (x == 255) { return x; } } return x;"

# try 0 "for (i = 0; ;) { MyPrint(); } return 0;"

echo "OK"
