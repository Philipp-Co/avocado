#ifndef __AVOCADO_MAP_H__
#define __AVOCADO_MAP_H__

#include <stdint.h>
#include <avocado/compress.h>


#define AVOCADO_MAX_CODE_LENGTH_IN_BITS (8U)
#define AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES (1U << (AVOCADO_MAX_CODE_LENGTH_IN_BITS))

typedef struct
{
    uint8_t number_of_bits;
    char symbol;
} AVOCADO_MapValue_t;

typedef struct
{
    AVOCADO_MapValue_t values[AVOCADO_MAP_MAX_NUMBER_OF_ENTRIES];
} AVOCADO_Map_t;


void AVOCADO_InitializeMap(AVOCADO_Map_t *map);
void AVOCADO_InitializeMapFromCodes(AVOCADO_Map_t *map, const Codes_t *codes);
AVOCADO_MapValue_t AVOCADO_MapGetValue(const AVOCADO_Map_t *map, uint32_t key);
void AVOCADO_MapSetValue(AVOCADO_Map_t *map, uint32_t key, const AVOCADO_MapValue_t *value);

char* AVOCADO_MapToString(const AVOCADO_Map_t *map);


#endif
