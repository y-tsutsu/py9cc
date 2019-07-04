#!/bin/bash
try() {
    expected="$1"
    input="$2"

    python py9cc.py "$input" > tmp.s

    if [ "$?" != "0" ]; then
        echo "py9cc.py error"
        exit 1
    fi

    gcc -o tmp tmp.s
    ./tmp
    actual="$?"

    if [ "$actual" = "$expected" ]; then
        echo "$input => $actual"
    else
        echo "$input => $expected expected, but got $actual"
        exit 1
    fi

    rm tmp.s tmp
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
try 6 "foo = 1; bar = 2 + 3; return foo + bar;"
try 130 "hoge = 42; piyo = hoge + 23; fuga = piyo * 2; return fuga;"
try 6 "x = 2; if (x == 2) x = x * 3; return x;"
try 2 "x = 2; if (x == 1) x = x * 3; return x;"
try 24 "x = 2; y = 0; z = 0; if (x == 2) y = x * 3; if (y > 0) z = y * 4; return z;"
try 6 "x = 2; y = 0; if (x == 2) y = x * 3; else y = x * 4; return y;"
try 8 "x = 2; y = 0; if (x == 1) y = x * 3; else y = x * 4; return y;"

echo OK
