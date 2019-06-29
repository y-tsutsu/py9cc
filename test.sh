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

try 0 0
try 42 42

echo OK
