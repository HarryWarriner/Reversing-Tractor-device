# Seengreat Thermal Camera MLX90640 demo codes
# Author(s):Andy Li from Seengreat

import time,threading
import math
import tkinter as tk
from ctypes import *
import numpy as np
from PIL import ImageDraw, Image, ImageFont, ImageTk, ImageFilter

DEV_ADDR  = 0x33
IMG_W     = 24
IMG_H     = 32
DISP_W    = 320
DISP_H    = 400
REFRESH_RATE  = 16  #define refresh rate to 64HZ

mlx = cdll.LoadLibrary('./lib/libmlx90640.so')

img_src = Image.new("RGB", (IMG_W, IMG_H), "RED")
pixels = img_src.load()
img_show = Image.new("RGB", (DISP_W, DISP_H), "BLACK")
image_show = Image.new("RGB", (DISP_W, DISP_H), "BLACK")
font = ImageFont.truetype("./lib/MiSans-Light.ttf",size=20)

window = tk.Tk()
window.title('SEENGREAT')
window.geometry("320x400+0+0")

def Temp_To_RGB(x, y, v): 
    # Heatmap code borrowed from: http://www.andrewnoske.com/wiki/Code_-_heatmaps_and_color_gradients
    NUM_COLORS = 7  # (1) black, (2) blue, (3) cyan, (4) green, (5) yellow, (6) red, (7) white
    color = [[0,0,0], [0,0,1], [0,1,0], [1,1,0], [1,0,0], [1,0,1], [1,1,1]]
    d_color = []
    idx1 = 0
    idx2 = 0
    fractBetween = 0.0
    vmin = 2.0
    vmax = 55.0
    float(v)
    v = (v-vmin)/(vmax-vmin)
    if(v <= 0): # accounts for an input <=0
        idx1=idx2=0
    elif(v >= 1): # accounts for an input >=0
        idx1=idx2=6
    else:   
        v *= (NUM_COLORS-1)
        idx1 = math.floor(float(v))
        idx2 = idx1+1
        fractBetween = v - float(idx1)
    d_color.append(int((((color[idx2][0] - color[idx1][0]) * fractBetween) + color[idx1][0]) * 255.0)) #red
    d_color.append(int((((color[idx2][1] - color[idx1][1]) * fractBetween) + color[idx1][1]) * 255.0)) #green
    d_color.append(int((((color[idx2][2] - color[idx1][2]) * fractBetween) + color[idx1][2]) * 255.0)) #bule
    pixels[x,y] = tuple(d_color)
    
# mlx90640 will output 32*24 temperature array with chess mode
def Update_image():
    global image_show,img_show,window,label
    data_valid = True
    mlx.Mlx90640_Init(DEV_ADDR, REFRESH_RATE)  # mlx90640 init and set the refresh rate as 16 HZ
    mlx90640To=(c_float*768)()
    p_mlx90640To=pointer(mlx90640To)
    image_show = ImageTk.PhotoImage(img_show)    
    label = tk.Label(window,image=image_show)
    while True:
        minTemp = 100.0
        maxTemp = 0.0        
        mlx.Get_temp_val(DEV_ADDR,p_mlx90640To)
        data_valid = True
        for i in range(768):
            if mlx90640To[i] != mlx90640To[i]: # find NaN value
                data_valid = False
                break
        if data_valid:
            for i in range(768):  # get the minimum and maximum temperature
                if(minTemp > mlx90640To[i]):
                    minTemp = mlx90640To[i]
                if(maxTemp < mlx90640To[i]):
                    maxTemp = mlx90640To[i]
            for y in range(IMG_W):  # set pixel color
                for x in range(IMG_H):
                    val = mlx90640To[IMG_H * (IMG_W-1-y) + x]
                    Temp_To_RGB(y, x, val) # update image pixels colors
            img_temp= img_src.filter(ImageFilter.BoxBlur(1.5)) # image blur
            img_show = img_temp.resize((DISP_W,DISP_H))
            draw = ImageDraw.Draw(img_show)        
            show_text = str.format("Min:%d%s"%(int(minTemp),"°C"))
            draw.text((10,DISP_H-30),show_text,fill=(0,0,255),font=font)# draw minimum temperature
        
            show_text = str.format("Max:%d%s"%(int(maxTemp),"°C"))
            draw.text((DISP_W-100,DISP_H-30),show_text,fill=(0,0,255),font=font) # draw maximum temperature
            
            image_show = ImageTk.PhotoImage(img_show)
            label.configure(image = image_show)
            label.image = image_show # keep a refrence to eliminate screen flicker
            label.place(x=0,y=0)

if __name__ == '__main__':
    print("mlx90640 for python demo")    
    thread = threading.Thread(target=Update_image)
    thread.start()
    window.mainloop()
    thread.join()


