#include "include/bwt.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct 
{
    const char *cstr;
    size_t length;
} AVOCADO_Tmp_t;

int AVOCADO_LexCompare(void *thunk, const void *a, const void *b)
{
    uint16_t *left = (uint16_t*)a;
    uint16_t *right = (uint16_t*)b;
    const char *original_cstr = ((AVOCADO_Tmp_t*)thunk)->cstr;
    
    size_t length = ((AVOCADO_Tmp_t*)thunk)->length;
    
    uint32_t i = 0;
    while((i < length) && (original_cstr[((*left) + i) % length] == original_cstr[(((*right) + i ) % length)]))
    {
        ++i;
    };

    if(i == length)
    {
        return 0;
    }

    return original_cstr[((*left) + i ) % length] < original_cstr[((*right) + i) % length] ? -1 : 1;
}

int32_t AVOCADO_Bwt(const char *cstr, char *buffer)
{
    size_t length = strlen(cstr) + 1; 
    uint16_t *indecies = malloc(sizeof(uint16_t) * length);
    for(uint16_t i=0;i<length;++i)
    {
        indecies[i] = i;
    }

    AVOCADO_Tmp_t tmp = {.cstr=cstr, .length=length};
    
    qsort_r(indecies, length, sizeof(uint16_t), &tmp, AVOCADO_LexCompare); 
    
    for(size_t i=0;i<length;++i)
    {
        /*
        printf("--------------------\n");
        printf("Copy %c from Index %lu to output\n", cstr[(indecies[i] + (length - 1)) % length], ((indecies[i] + (length - 1)) % length));
        for(uint16_t j=0;j < (length);++j)
        {
            printf("%c", cstr[(j + indecies[i]) % (length)]);
        }
        printf("\n");
        printf("--------------------\n");
        */
        buffer[i] = cstr[
            (indecies[i] + (length - 1)) % length
        ];
    }

    free(indecies);

    return 0;
}

int32_t AVOCADO_InverseBwt(const char *cstr)
{

    return -1;
}
