
//
// --------------------------------------------------------------------------------------------------------------------
//
#include <avocado/compress.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

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
        number_of_bits += instance->codes.codes[(uint8_t)input[i]].size;
    }

    output[0] = (char) (number_of_bits & 0xFFU);
    output[1] = (char) ((number_of_bits >> 8) & 0xFFU);
    output[2] = (char) ((number_of_bits >> 16) & 0xFFU);
    output[3] = (char) ((number_of_bits >> 24) & 0xFFU); 

    size_t current_bit = 0;
    for(size_t i=0;i<number_of_characters;++i)
    {
        for(size_t j=0;j<instance->codes.codes[(uint8_t)input[i]].size;++j)
        {
            const uint32_t byte = (((uint32_t)current_bit) / 8U);
            const uint32_t bit = (((uint32_t)current_bit) % 8U);
            output[4 + byte] |= (instance->codes.codes[(uint8_t)input[i]].code & (1 << j)) ? (1 << bit) : 0; 
            current_bit++;
        }
    }
    return (int32_t)number_of_bits;
}

//
// --------------------------------------------------------------------------------------------------------------------
//

#include <stdbool.h>

struct HuffmanTreeNode;

struct HuffmanTreeNode 
{
    char c;
    struct HuffmanTreeNode *left;
    struct HuffmanTreeNode *right;
};

typedef struct 
{
    struct HuffmanTreeNode *node; 
} HuffmanTreeIterator_t;

static char AVOCADO_HuffmanTreeIteratorSymbol(HuffmanTreeIterator_t *it);
static bool AVOCADO_HuffmanTreeIteratorNextBit(HuffmanTreeIterator_t *it, uint32_t bit);
static bool AVOCADO_HuffmanTreeIteratorIsLeaf(const HuffmanTreeIterator_t *it);

typedef struct
{
    struct HuffmanTreeNode *root;
} HuffmanTree_t;

static HuffmanTree_t AVOCADO_CreateHuffmanTree(BinaryCodes_t *codes); 
static HuffmanTreeIterator_t AVOCADO_HuffmanTreeIterator(HuffmanTree_t *t);

int32_t AVOCADO_Decode(AVOCADO_Codec_t instance, const char *cstr, char *output, uint32_t size)
{
    uint32_t number_of_bits = (((uint32_t)cstr[0]) & 0xFFU) | ((((uint32_t)(cstr[1])) << 8) & 0xFF00U) | ((((uint32_t)(cstr[2])) << 24) & 0xFF0000U) | ((((uint32_t)(cstr[3])) << 24) & 0xFF000000U);
    HuffmanTree_t tree = AVOCADO_CreateHuffmanTree(&instance->codes);
    uint32_t output_character = 0U; 
    uint32_t i = 0U;
    HuffmanTreeIterator_t it = AVOCADO_HuffmanTreeIterator(&tree); 
    while((i < number_of_bits) && (output_character < (size - 1U)))
    {
        const uint32_t byte = i / 8U;
        const uint32_t bit = i % 8U;
        if (
            AVOCADO_HuffmanTreeIteratorNextBit(
                &it, (((uint8_t)cstr[4 + byte]) & (1U << bit)) ? 1U : 0U
            )
        )
        {
            output[output_character++] = AVOCADO_HuffmanTreeIteratorSymbol(&it);
            it = AVOCADO_HuffmanTreeIterator(&tree);
        }
        ++i;
    }
    return output_character < (size - 1U) ? (int32_t)output_character : -1;
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

static char AVOCADO_HuffmanTreeIteratorSymbol(HuffmanTreeIterator_t *it)
{
    return it->node->c;
}

static bool AVOCADO_HuffmanTreeIteratorNextBit(HuffmanTreeIterator_t *it, uint32_t bit)
{
    if(NULL == it->node)
    {
        return false;
    }
    if(AVOCADO_HuffmanTreeIteratorIsLeaf(it))
    {
        return true;
    }
    
    if(bit)
    {
        it->node = it->node->right;
    }
    else
    {
        it->node = it->node->left;
    }

    return it->node != NULL && AVOCADO_HuffmanTreeIteratorIsLeaf(it);
}

static bool AVOCADO_HuffmanTreeIteratorIsLeaf(const HuffmanTreeIterator_t *it)
{
    return it->node->left == NULL && it->node->right == NULL;
}

static void AVOCADO_HuffmanTreeAddNode(struct HuffmanTreeNode *node, char c, uint32_t code, uint32_t bit, uint32_t max_bit)
{
    if(bit >= max_bit)
    {
        node->c = c;
    }
    else
    {
        if((code & bit) != 0U)
        {
            if(node->right == NULL)
            {
                struct HuffmanTreeNode *new_node = malloc(sizeof(struct HuffmanTreeNode));
                new_node->c = 0;
                new_node->left = NULL;
                new_node->right = NULL;
                node->right = new_node;
            }
            AVOCADO_HuffmanTreeAddNode(node->right, c, code, bit << 1, max_bit);
        }
        else
        {
            if(node->left == NULL)
            {
                struct HuffmanTreeNode *new_node = malloc(sizeof(struct HuffmanTreeNode));
                new_node->c = 0;
                new_node->left = NULL;
                new_node->right = NULL;
                node->left = new_node;
            }
            AVOCADO_HuffmanTreeAddNode(node->left, c, code, bit << 1, max_bit);
        }
    }
}

static HuffmanTree_t AVOCADO_CreateHuffmanTree(BinaryCodes_t *codes)
{
    struct HuffmanTreeNode *node = malloc(sizeof(struct HuffmanTreeNode));
    node->c = 0;
    node->left = NULL;
    node->right = NULL;
    HuffmanTree_t t = {
        .root=node
    };
    for(size_t i=0;i<256;++i)
    {
        if(codes->codes[i].size > 0)
        {
            AVOCADO_HuffmanTreeAddNode(
                node, (char)i, codes->codes[i].code, 1U, 1U << codes->codes[i].size 
            );    
            
        }
    }
    return t;
} 

static HuffmanTreeIterator_t AVOCADO_HuffmanTreeIterator(HuffmanTree_t *t)
{
    HuffmanTreeIterator_t it = {
        .node=t->root
    };
    return it;
}
//
// --------------------------------------------------------------------------------------------------------------------
//
