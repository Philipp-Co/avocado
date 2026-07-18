

#ifndef __AVOCADO_COMPRESS_H__
#define __AVOCADO_COMPRESS_H__

//
// --------------------------------------------------------------------------------------------------------------------
//

#include <stdint.h>

//
// --------------------------------------------------------------------------------------------------------------------
//

#if defined(_WIN32)
#  if defined(AVOCADO_BUILD_DLL)
#    define AVOCADO_API __declspec(dllexport)
#  else
#    define AVOCADO_API __declspec(dllimport)
#  endif
#else
#  define AVOCADO_API __attribute__((visibility("default")))
#endif

//
// --------------------------------------------------------------------------------------------------------------------
//

struct AVOCADO_Codec;
typedef struct AVOCADO_Codec* AVOCADO_Codec_t;
//
// --------------------------------------------------------------------------------------------------------------------
//

typedef struct
{
    char *characters;
    char **codes;
    int32_t size;
} Codes_t;
//
// --------------------------------------------------------------------------------------------------------------------
//

///
/// \brief  Create a new Instance.
///         When its lifetime is over destroy this object with a call to DeInit to release Ressources.
///
/// \param[in] codes: The new Instance is constructed from this Code Table.
///
AVOCADO_API AVOCADO_Codec_t AVOCADO_Init(const Codes_t *codes);
///
/// \brief  Destroy an Instance.
/// \param[in/out] instance:    When calling this function "instance" must point to a valid Object.
///                             If it was possible to destroy the given Instance the Value of "instance" will be set to NULL.
///
AVOCADO_API void AVOCADO_DeInit(AVOCADO_Codec_t *instance);
///
/// \brief  Encode a given Inputstring.
///
/// \param[in] instance:    An Instance.
/// \param[in] input:       A Null terminated C-String.
/// \param[out] output:     A Buffer. The encoded Output is written to this Buffer.
/// \param[int] size:       Size of the "outpu" in Bytes.
///
/// \returns    The Number of Bits which where written to the Outputbuffer. Or -1 if an Error occured.
///
AVOCADO_API int32_t AVOCADO_Encode(AVOCADO_Codec_t instance, const char *input, char *output, uint32_t size);
///
/// \brief  Decode a given Inputstring.
///
/// \param[int] instance: An Instance.
/// \param[in] input: Encoded Inputbuffer.
/// \param[out] output: Outputbuffer.
/// \param[in] size: Size in Bytes of the given "output"-Buffer. 
///
/// \returns The Number of Bytes written to the "output". -1 if an Error occured.
///
AVOCADO_API int32_t AVOCADO_Decode(AVOCADO_Codec_t instance, const char *input, char *output, uint32_t size);

//
// --------------------------------------------------------------------------------------------------------------------
//

#endif
