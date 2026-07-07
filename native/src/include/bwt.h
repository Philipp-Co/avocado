#ifndef __AVOCADO_BWT_H__
#define __AVOCADO_BWT_H__


#include <stdint.h>
#include <stddef.h>


int32_t AVOCADO_Bwt(const char *cstr, char *buffer);
int32_t AVOCADO_InverseBwt(const char *cstr);



#endif
