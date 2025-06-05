/**********************************************
 * Seengreat Thermal Camera MLX90640 demo codes
 * Author(s):Andy Li from Seengreat
 * ********************************************/

#include <stdio.h>
#include "CImg/CImg.h"
#include <sys/time.h>
#include <math.h>
#include <string.h>
#include "headers/MLX90640_API.h"
#include "headers/MLX90640_I2C_Driver.h"

using namespace cimg_library;

#define DEV_ADDR   0x33
#define IMG_W      24
#define IMG_H      32
#define DISP_W     320
#define DISP_H     400
#define REFRESH_RATE  16  //define refresh rate to 16HZ
char show_text[20];
CImg<unsigned char>img_src(24,32,1,3);
CImg<unsigned char>img_show(DISP_W,DISP_H,1,3);
char const tem_uint[2] = {0xb0,0x43};//"°C"

void Temp_To_RGB(int x, int y, float v) 
{
    // Heatmap code borrowed from: http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
    const int NUM_COLORS = 7;//(1) black, (2) blue, (3) cyan, (4) green, (5) yellow, (6) red, (7) white
    static float color[NUM_COLORS][3] = { {0,0,0}, {0,0,1}, {0,1,0}, {1,1,0}, {1,0,0}, {1,0,1}, {1,1,1} };
    unsigned int d_color[3] = {};
    int idx1, idx2;
    float fractBetween = 0;
    float vmin = 2.0;
    float vmax = 55.0;
    v = (v-vmin)/(vmax-vmin);
    if(v <= 0) // accounts for an input <=0
    {
        idx1=idx2=0;
    }
    else if(v >= 1) // accounts for an input >=0
    {
        idx1=idx2=6;
    }
    else
    {
        v *= (NUM_COLORS-1);
        idx1 = floor(v);
        idx2 = idx1+1;
        fractBetween = v - float(idx1);
    }

    d_color[0] = (int)((((color[idx2][0] - color[idx1][0]) * fractBetween) + color[idx1][0]) * 255.0); //red
    d_color[1] = (int)((((color[idx2][1] - color[idx1][1]) * fractBetween) + color[idx1][1]) * 255.0); //green
    d_color[2] = (int)((((color[idx2][2] - color[idx1][2]) * fractBetween) + color[idx1][2]) * 255.0); //blue
    img_src.draw_point(x,y,d_color);
}


int main()
{
    int res = 0;
    int minTemp = 100;
    int maxTemp = 0;
    unsigned int i=0;
    img_src.fill(0);
    
    unsigned char blue[] = {0,0,255};
    CImgDisplay disp(img_show,"SEENGREAT");

    static u_int16_t eemlx90640[832];
    float emissivity = 0.95;
    u_int16_t frame[834];
    static float mlx90640To[768];
    float eTa;
    paramsMLX90640 para_buf;
    
    usleep(50000);
    int refreshrate_num = (int)(log2(REFRESH_RATE)+1.0);
    MLX90640_SetRefreshRate(DEV_ADDR, refreshrate_num ); //set the refresh rate as 16 HZ
    res = MLX90640_GetRefreshRate(DEV_ADDR);
    printf("res:%d\r\n",res); 
    if(refreshrate_num == res)
    {
        printf("RefreshRate:%dHZ\r\n", REFRESH_RATE);
    }
    else
    {
        printf("set refresh rate failed!\r\n");
        return 0;	
    }
    MLX90640_SetChessMode(DEV_ADDR);
    MLX90640_DumpEE(DEV_ADDR, eemlx90640);
    MLX90640_ExtractParameters(eemlx90640, &para_buf);
    while(1)
    {
        MLX90640_GetFrameData(DEV_ADDR, frame);
        float vdd = MLX90640_GetVdd(frame,&para_buf);
        eTa = MLX90640_GetTa(frame, &para_buf);
        MLX90640_CalculateTo(frame, &para_buf, emissivity, eTa, mlx90640To);

        MLX90640_BadPixelsCorrection((&para_buf)->brokenPixels, mlx90640To, 1, &para_buf);
        MLX90640_BadPixelsCorrection((&para_buf)->outlierPixels, mlx90640To, 1, &para_buf);

        float minTemp = 100.0;
        float maxTemp = 0.0;
        for(int i=0;i<768;i++)//get the minimum and maximum temperature
        {
            if(minTemp > mlx90640To[i]) minTemp = mlx90640To[i];
            if(maxTemp < mlx90640To[i]) maxTemp = mlx90640To[i];
        }

        for(int y = 0; y < IMG_W; y++) //set pixel colour
        {
            for(int x = 0; x < IMG_H; x++)
            {
                float val = mlx90640To[IMG_H * (IMG_W-1-y) + x];
                Temp_To_RGB(y, x, val);
            }
        }
        img_src.blur(1.0);              
        img_show = img_src.resize(DISP_W,DISP_H,1,3);
        img_src.resize(IMG_W,IMG_H,1,3);//resize the img_src to 24*32
            
        sprintf(show_text,"Min:%d",int(minTemp));
        strcat(show_text, tem_uint);
        img_show.draw_text(10,DISP_H-30,show_text,blue,0,1,23);
        
        sprintf(show_text,"Max:%d",int(maxTemp));
        strcat(show_text, tem_uint);
        img_show.draw_text(DISP_W-120,DISP_H-30,show_text,blue,0,1,23);//
	
        disp.display(img_show);   		
    }
    return 0;
}
