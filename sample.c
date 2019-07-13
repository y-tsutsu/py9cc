#include <stdio.h>

void MyPrint()
{
    printf("Hello, My Print!!\n");
}

void MyPrintNum(int num)
{
    printf("%d\n", num);
}

int MyAdd(int v1, int v2, int v3, int v4, int v5, int v6)
{
    int ans = v1 + v2 + v3 + v4 + v5 + v6;
    return ans;
}

int MyDiv(int v1, int v2)
{
    int ans = v1 / v2;
    return ans;
}
