#ifndef _USR_API_H_
#define _USR_API_H_

#include <stdint.h>
extern "C"{
	
void Mlx90640_Init(int dev_addr, int refreshrate);
void Get_temp_val(int dev_addr, float *tem_buf);

}
#endif
