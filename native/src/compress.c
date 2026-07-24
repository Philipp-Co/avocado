
//
// --------------------------------------------------------------------------------------------------------------------
//
#include <avocado/compress.h>
#include <assert.h>
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
    //
    // Ignore the size...
    // Assume that the encoded Bits fit into the output of size * 8 Bits.
    //
    (void)size;
    const char *current_character = input;
    int32_t current_bit = 0;
    do {
        const uint8_t symbol = (uint8_t)(*current_character++);
        const uint32_t code = instance->codes.codes[symbol].code;
        const uint32_t length = instance->codes.codes[symbol].size;
        assert(length < (sizeof(uint32_t) * 8U));

        const int32_t byte = current_bit / 8;
        const int32_t bit = current_bit % 8;
        const uint8_t lo = (uint8_t)(code << bit);
        const uint8_t hi = (uint8_t)(code >> (8 - bit)); 

        output[2 + byte] |= (char)lo;
        output[2 + byte + 1] = (char)hi;
        
        current_bit += length;
        if('\0' == symbol) break;
    } while(1);

    output[0] = (char) ((uint8_t)(((uint32_t)current_bit) & 0xFFU));
    output[1] = (char) ((uint8_t)((((uint32_t)current_bit) >> 8) & 0xFFU));
    
    return (int32_t)current_bit;
}

//
// --------------------------------------------------------------------------------------------------------------------
//

int32_t AVOCADO_Decode(AVOCADO_Codec_t instance, const char *input, char *output, uint32_t size)
{
    //
    // Read the number of Bits used.
    // Assume that the inputs number of Bytes fits these Bits.
    //  -> In some Cases there can be some unused Bits.
    //
    const uint8_t lo_number_bits = (uint8_t)input[0];
    const uint8_t hi_number_bits = (uint8_t)input[1];
    const uint16_t number_of_bits = ((uint16_t)lo_number_bits) | (uint16_t)(((uint16_t)hi_number_bits) << 8); 
    if(number_of_bits >= (size * 8U))
    {
        return -1;
    }
    //
    // Prepare LUT Algorithm.
    //
    char *current_output_byte = output;
    uint16_t buffer = 0U;
    uint32_t current_bit = 0U;
    do
    {
        const uint32_t byte = current_bit / 8U;
        const uint32_t bit = current_bit % 8U;
        const uint8_t lo_bits = (uint8_t)(((uint8_t)input[2 + byte]) >> bit); 
        const uint8_t hi_bits = (uint8_t)(((uint8_t)input[2 + byte + 1]) << (8U - bit));
        buffer = (
            lo_bits | hi_bits
        );
        const AVOCADO_MapValue_t value = AVOCADO_MapGetValue(&instance->map, buffer);
        current_bit = (current_bit + (uint32_t)value.number_of_bits);
        *current_output_byte++ = value.symbol;
    } while(current_bit < number_of_bits);
    return (int32_t)(current_output_byte - output);
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
