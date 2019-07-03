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

try 0 "0;"
try 42 "42;"
try 21 "5+20-4;"
try 41 " 12 + 34 - 5 ;"
try 47 "5+6*7;"
try 15 "5*(9-6);"
try 4 "(3+5)/2;"
try 10 "-10+20;"
try 42 "+1*42;"
try 0 "1+(-1);"
try 3 "1++2;"
try 1 "42==42;"
try 0 "42==23;"
try 1 "42!=23;"
try 0 "42!=42;"
try 1 "42<=43;"
try 1 "42<=42;"
try 0 "42<=41;"
try 1 "42<43;"
try 0 "42<42;"
try 0 "42<41;"
try 1 "43>=42;"
try 1 "42>=42;"
try 0 "41>=42;"
try 1 "43>42;"
try 0 "42>42;"
try 0 "41>42;"
try 14 "a = 3; b = 5 * 6 - 8; a + b / 2;"
try 6 "foo = 1; bar = 2 + 3; foo + bar;"

echo OK
