#include "map.h"
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>


#define haszero(x) (~(((((x) & 0x7F7F7F7FU) + 0x7F7F7F7FU) | (x)) | 0x7F7F7F7FU))
#define hasvalue(x, n) (haszero((x) ^ (~0U/255 * (n))))



void AVOCADO_InitializeMap(AVOCADO_Map_t *map)
{
    memset(map->values, 0, sizeof(map->values));
}

const AVOCADO_MapValue_t* AVOCADO_MapGetValue(const AVOCADO_Map_t *map, uint32_t key)
{
    assert(key < AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES);
    if(map->values[key].number_of_bits == 0)
    {
        return NULL;
    }
    return &map->values[key];
}

void AVOCADO_MapSetValue(AVOCADO_Map_t *map, uint32_t key, const AVOCADO_MapValue_t *value)
{
    assert(key < AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES);
    map->values[key] = *value;
}

typedef struct 
{
    uint32_t code;
    uint32_t mask;
    uint32_t number_of_bits;
} AVOCADO_TmpCode_t;

static AVOCADO_TmpCode_t AVOCADO_StrToInt(const char* cstr);
static char* AVOCADO_U32ToCstr(uint32_t value, char *cstr);

void AVOCADO_InitializeMapFromCodes(AVOCADO_Map_t *map, const Codes_t *codes)
{
    AVOCADO_InitializeMap(map);
    AVOCADO_TmpCode_t tmp;
    AVOCADO_MapValue_t map_value;
    for(size_t i=0;i<(size_t)codes->size;++i)
    {
        tmp = AVOCADO_StrToInt(codes->codes[i]);
        size_t j=0;
        uint32_t pattern = 0U;
        while(j < (1U << (AVOCADO_MAX_CODE_LENGTH_IN_BITS - tmp.number_of_bits)))
        {
            pattern = (
                    ((uint32_t)j) << (tmp.number_of_bits)
            ) | tmp.code;
            map_value.node = NULL;
            map_value.symbol = codes->characters[i];
            map_value.number_of_bits = (uint8_t)tmp.number_of_bits;
            AVOCADO_MapSetValue(map, pattern, &map_value);
            ++j;
        }
    } 
}

static AVOCADO_TmpCode_t AVOCADO_StrToInt(const char* cstr)
{
    AVOCADO_TmpCode_t tmp = {
        .code=0,
        .mask=0,
        .number_of_bits=0   
    };
    while('\0' != *cstr)
    {
        tmp.code |= ((*cstr == '0' ? 0U : 1U) << tmp.number_of_bits);
        ++cstr;
        ++tmp.number_of_bits;
    }
    tmp.mask = ((1U << tmp.number_of_bits)) - 1U;
    return tmp;
}

static char* AVOCADO_U32ToCstr(uint32_t value, char *cstr)
{
    char *ptr = cstr;
    for(size_t i=0;i<32;++i)
    {
        *ptr = value & (1U << i) ? '1': '0';
        ++ptr;
    }
    *ptr = '\0';
    return cstr;
}

char* AVOCADO_MapToString(const AVOCADO_Map_t *map)
{
    const uint32_t length = AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES * 75;
    char *buffer = malloc(length);
    char small[48];
    char *tmp = buffer;
    for(size_t i=0;i<AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES;++i)
    {
        const AVOCADO_MapValue_t *entry = AVOCADO_MapGetValue(map, (uint32_t)i);
        const int len = snprintf(tmp, length - (tmp - buffer), "[%-3lu] Symbol: %-3i, #Bits: %-3i, Code: 0b%s\n", i, (int)entry->symbol, entry->number_of_bits, AVOCADO_U32ToCstr((uint32_t)i, small));
        tmp += len; 
    }
    return buffer;
}
