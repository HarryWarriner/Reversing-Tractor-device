/**********************************************
 * Seengreat Thermal Camera MLX90640 demo codes
 * Author(s):Andy Li from Seengreat
 * ********************************************/

#include <stdio.h>
#include <math.h>
#include "MLX90640_I2C_Driver.h"
#include "MLX90640_API.h"
#include "usr_api.h"

//there are the application layer functions called for python users
//all cpp files will generate mlx90640.so dynamic library file called by python

paramsMLX90640 para_buf;
    
void Mlx90640_Init(int dev_addr, int refreshrate)
{
	u_int16_t eemlx90640[832];
	int res;
	int refreshrate_num = (int)(log2(refreshrate)+1.0);
    MLX90640_SetRefreshRate(dev_addr, refreshrate_num); //set the refresh rate 
    res = MLX90640_GetRefreshRate(dev_addr);
    printf("res:%d\r\n",res); 
    if(refreshrate_num == res)
    {
	    printf("RefreshRate:%dHZ\r\n", refreshrate);
    }
    else
    {
		printf("set refresh rate failed!\r\n");
    }
    MLX90640_SetChessMode(dev_addr);
    MLX90640_DumpEE(dev_addr, eemlx90640);
    MLX90640_ExtractParameters(eemlx90640, &para_buf);
}

void Get_temp_val(int dev_addr, float *tem_buf)
{
	float emissivity = 0.95;
	u_int16_t frame[834];
	float eTa;
	MLX90640_GetFrameData(dev_addr, frame);
	eTa = MLX90640_GetTa(frame, &para_buf);
	MLX90640_CalculateTo(frame, &para_buf, emissivity, eTa, tem_buf);

	MLX90640_BadPixelsCorrection((&para_buf)->brokenPixels, tem_buf, 1, &para_buf);
	MLX90640_BadPixelsCorrection((&para_buf)->outlierPixels, tem_buf, 1, &para_buf);
}
