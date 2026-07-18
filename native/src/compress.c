
//
// --------------------------------------------------------------------------------------------------------------------
//
#include <avocado/compress.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include "map.h"

//
// --------------------------------------------------------------------------------------------------------------------
//
typedef struct
{ 
    uint32_t code;
    uint32_t size;
} BinaryCode_t;

typedef struct
{
   BinaryCode_t codes[256]; 
} BinaryCodes_t;

struct AVOCADO_Codec
{
    BinaryCodes_t codes;
    AVOCADO_Map_t map;
};

//
// --------------------------------------------------------------------------------------------------------------------
//



static void AVOCADO_UnicodeToBinaryCode(BinaryCodes_t *bin, char c, const char *unicode);
//
// --------------------------------------------------------------------------------------------------------------------
//

AVOCADO_Codec_t AVOCADO_Init(const Codes_t *codes)
{
    struct AVOCADO_Codec *codec = malloc(sizeof(struct AVOCADO_Codec));
    memset(&codec->codes, '\0', sizeof(codec->codes));
    for(int32_t i=0;i<codes->size;++i)
    {
        AVOCADO_UnicodeToBinaryCode(
            &codec->codes,
            codes->characters[i],
            codes->codes[i]
        );
    }

    AVOCADO_InitializeMapFromCodes(&codec->map, codes);

    return codec;
}

void AVOCADO_DeInit(AVOCADO_Codec_t *instance)
{
    free(
        *instance
    );
    *instance = NULL;
}

int32_t AVOCADO_Encode(AVOCADO_Codec_t instance, const char *input, char *output, uint32_t size)
{
    memset(output, '\0', size);

    size_t number_of_characters = strlen(input); 
    uint32_t number_of_bits = 0U;
    for(size_t i=0;i < number_of_characters; ++i)
    {
        const uint8_t symbol = (uint8_t)input[i];
        number_of_bits += instance->codes.codes[symbol].size;
    }

    output[0] = (char) ((uint8_t)(number_of_bits & 0xFFU));
    output[1] = (char) ((uint8_t)((number_of_bits >> 8) & 0xFFU));
    output[2] = (char) ((uint8_t)((number_of_bits >> 16) & 0xFFU));
    output[3] = (char) ((uint8_t)((number_of_bits >> 24) & 0xFFU)); 

    uint32_t current_bit = 0U;
    for(size_t i=0U;i<number_of_characters;++i)
    {
        const uint8_t symbol = (uint8_t)input[i];
        for(uint32_t j=0;j<instance->codes.codes[symbol].size;++j)
        {
            const uint32_t byte = current_bit / 8U;
            const uint32_t bit = current_bit % 8U;
            output[4U + byte] |= (instance->codes.codes[symbol].code & (1U << j)) ? (1U << bit) : 0U; 
            current_bit++;
        }
    }
    return (int32_t)number_of_bits;
}

//
// --------------------------------------------------------------------------------------------------------------------
//

int32_t AVOCADO_Decode(AVOCADO_Codec_t instance, const char *cstr, char *output, uint32_t size)
{
    //
    // Read the number of Bits used.
    // Assume that the inputs number of Bytes fits these Bits.
    //  -> In some Cases there can be some unused Bits.
    //
    uint32_t number_of_bits = (((uint32_t)cstr[0]) & 0xFFU) | ((((uint32_t)(cstr[1])) << 8) & 0xFF00U) | ((((uint32_t)(cstr[2])) << 24) & 0xFF0000U) | ((((uint32_t)(cstr[3])) << 24) & 0xFF000000U);
    //
    // Prepare LUT Algorithm.
    //
    uint32_t next_output_character = 0U;
    uint32_t buffer = 0U;
    uint32_t current_bit = 0U;
    const AVOCADO_MapValue_t *value = NULL;
    while((current_bit < number_of_bits) && (next_output_character < size))
    {
        const uint32_t byte = current_bit / 8U;
        const uint32_t bit = current_bit % 8U;
        const uint32_t lo_byte_as_u32 = (uint32_t)((uint8_t)cstr[4 + byte]);        // If char is < 0 then Cast to uint32_t will populate Register with 1s... 
        const uint32_t hi_byte_as_u32 = (uint32_t)((uint8_t)cstr[4 + byte + 1]);    // Therefore first cast to uint8_t, no more negative Numbers, then cast to uint32_t. 
        const uint32_t lo_bits = lo_byte_as_u32 >> bit; 
        const uint32_t hi_bits = hi_byte_as_u32 << (8U - bit);
        buffer = (
            lo_bits | hi_bits
        ) & 0xFFU;                                                                  // Must be Masked for the special case when bit = 0 and 8U - bit = 8. 

        value = AVOCADO_MapGetValue(&instance->map, buffer);
        if((NULL == value) || (value->number_of_bits == 0))
        {
            return -1;
        }
        current_bit += value->number_of_bits;

        output[next_output_character++] = value->symbol;
    }
    return next_output_character < (size - 1U) ? (int32_t)next_output_character : -1;
}


static void AVOCADO_UnicodeToBinaryCode(BinaryCodes_t *bin, char c, const char *unicode)
{
    bin->codes[(uint8_t)c].code = 0U; 
    for(size_t i=0;i<strlen(unicode); ++i)
    {
        if(unicode[i] == '1')
        {
            bin->codes[(uint8_t)c].code |= (1U << i);
        }
        else
        {
        }
    }
    bin->codes[(uint8_t)c].size = (uint32_t)strlen(unicode); 
}

//
// --------------------------------------------------------------------------------------------------------------------
//
